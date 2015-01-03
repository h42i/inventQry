#!/usr/bin/env python
import qrcode
from PIL import Image, ImageDraw, ImageFont
from subprocess import call

base_url = "http://i.hasi.it/"

class InventQryLabel(object):
    def __init__(self, label_size):
        self.w = w = label_size[0]
        self.h = h = label_size[1]

        self.qr_size = (h, h)
        self.text_size = (w - h, h)

    def mktext(self, string, font, fontsize):
        text = Image.new("1", self.text_size, color = 1)
        font = ImageFont.truetype(font, fontsize)
        draw = ImageDraw.Draw(text)
        # TODO perform text fitting and placing
        draw.text((0, 0), string, font=font)

        return text

    def gen_qrcode(self, id):
        # generate new qr code
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_Q, # 25% errors correctable
            box_size=10,
            border=0, # apparently the standard requires 4...
        )

        qr.add_data(base_url)
        qr.add_data(id)
        qr.make(fit=True)

        code = qr.make_image().resize(self.qr_size)

        return code

    def generate(self, name, owner, contact, usage_rule, uid):
        # create binary (black/white) image
        im = Image.new("1", (self.w, self.h), color=1)

        code = self.gen_qrcode(uid)

        size_s = 18
        size_m = 26
        size_l = 32

        # create font images
        name_txt = None
        if name == "Harry Plotter":
            name_txt = self.mktext(name, "./static/font/harry.ttf", 50)
        else:
            name_txt = self.mktext(name, "./static/font/Ubuntu-L.ttf", size_l)

        owner_label_txt = self.mktext("Owner",
                                      "./static/font/Ubuntu-L.ttf", size_s)
        owner_txt = self.mktext("{}".format(owner),
                                "./static/font/Ubuntu-L.ttf", size_m)
        contact_label_txt = self.mktext("Contact",
                                        "./static/font/Ubuntu-L.ttf", size_s)
        contact_txt = self.mktext("{}".format(contact),
                                  "./static/font/Ubuntu-L.ttf", size_m)
        permissions_label_txt = self.mktext("Permissions",
                                            "./static/font/Ubuntu-L.ttf", size_s)
        permissions_txt = self.mktext("{}".format(usage_rule),
                                      "./static/font/Ubuntu-L.ttf", size_m)

        # place image parts
        offset_x = 15
        offset_y = self.h - 145
        step_s = 17
        step_m = 29
        im.paste(name_txt, (offset_x, 0))
        posy = offset_y
        im.paste(owner_label_txt, (offset_x, posy))
        posy += step_s
        im.paste(owner_txt, (offset_x, posy))
        posy += step_m
        im.paste(contact_label_txt, (offset_x, posy))
        posy += step_s
        im.paste(contact_txt, (offset_x, posy))
        posy += step_m
        im.paste(permissions_label_txt, (offset_x, posy))
        posy += step_s
        im.paste(permissions_txt, (offset_x, posy))
        im.paste(code, (self.w-self.h, 0))

        # output needs to be W < H, so rotate
        final = im.rotate(90)

        return final

    def print(self, image):
        image.save("out.pbm")
        call([ "bash", "print" ])

if __name__ == "__main__":
    inventQryLabel = InventQryLabel((514, 196))
    label = inventQryLabel.generate("Name", "Owner", "Contact", "rule", "uid")
    inventQryLabel.print(label)
