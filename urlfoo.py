from flask import *
import sqlite3
import uuid

class DataFoo:
    def __init__(self):
        self.data_file = "urlfoo.db"
        self.db_conn = sqlite3.connect(self.data_file, check_same_thread=False)
        cursor = self.db_conn.cursor()

        urls_table = """CREATE TABLE IF NOT EXISTS urls (
                            id         INTEGER       PRIMARY KEY AUTOINCREMENT,
                            uid        VARCHAR(36),
                            url        VARCHAR(4096)
                        );"""
        cursor.execute(urls_table)

        cursor.close()

    def __del__(self):
        self.db_conn.close()

    def write(self, query, values = None):
        cursor = self.db_conn.cursor()

        if values != None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        self.db_conn.commit()

        return cursor

    def read(self, query, values = None):
        cursor = self.db_conn.cursor()

        if values != None:
            cursor.execute(query, values)
        else:
            cursor.execute(query)

        return cursor

app = Flask(__name__)
data = DataFoo()

def db_get_urls():
    c = data.read("""SELECT * FROM urls
                     ORDER BY id DESC;""")
    urls = [dict(id=row[0],
                 uid=row[1],
                 url=row[2]) for row in c.fetchall()]

    return urls

def db_get_url_by_uid(uid):
    c = data.read("""SELECT * FROM urls
                     WHERE uid=?;""",
                  [uid])
    urls = [dict(id=row[0],
                 uid=row[1],
                 url=row[2]) for row in c.fetchall()]

    return urls[0] if len(urls) == 1 else None

def db_add_url(uid, url):
    c = data.write("""INSERT INTO urls (uid, url)
                      VALUES (?, ?);""",
                   [uid, url])

def db_modify_url(uid, url):
    c = data.read("""UPDATE urls
                     SET url=?
                     WHERE uid=?;""",
                  [url, uid])

@app.route("/", methods=["POST"])
def add():
    if request.method == "POST":
        if not request.json or not "uid" in request.json or not "url" in request.json:
            abort(400)

        db_add_url(request.json["uid"], request.json["url"])

        return "Ok.", 201
    # TODO urlfoo info page
    #else
    #    return render_template('urlfoo_info.html')

@app.route("/<uid>", methods=["PUT", "GET"])
def modify_or_redirect(uid):
    url = db_get_url_by_uid(uid)

    if request.method == "PUT":
        if not request.json or not "url" in request.json:
            abort(400)

        db_modify_url(uid, request.json["url"])

        return "Ok.", 200
    elif request.method == "GET":
        if url != None:
            return redirect(url["url"], code=302)
        else:
            return abort(404)

if __name__ == "__main__":
   app.run(host="0.0.0.0", debug=True, port=80)
