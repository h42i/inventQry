#!/usr/bin/env python
#! -*- coding:utf-8 -*-
import sys, re

labelinfo = {}
papersize = None
imageable = None

""" Parse .ppd file and extract Imageble Area and Paper Dimensions """
def read_labelinfos (filename):
    f = open(filename, 'r')
    data = f.read()

    # extract all ImageableArea formats
    ar = re.findall('(?ims)^\\*ImageableArea ([^"]*): "([0-9. ]*)"', data)
    ar = [(key, tuple([float(f) for f in val.split()])) for key, val in ar]
    ar = dict(ar)

    # extract all PaperDimension formats
    ps = re.findall ('(?ims)^\\*PaperDimension ([^"]*): "([0-9. ]*)"', data)
    ps = [(key, tuple ([float (f) for f in val.split()])) for key, val in ps]
    ps = dict(ps)

    if set (ar.keys()) != set (ps.keys()):
        raise Exception("assymmetric keys for ImageableArea and PaperDimension")

    # assemble label info
    for k in ar.keys():
        labelinfo[k] = (ps[k], ar[k])
    #   print("'{}': pd{} ia{}".format(k, labelinfo[k][0], labelinfo[k][1]))

""" Set the label type """
def set_labelinfo(key):
    global labelinfo, papersize, imageable

    # find matching key in labelinfos dict
    keys = [ k for k in labelinfo.keys() if re.search(key, k) ]

    if len(keys) == 0:
        raise Exception("unknown label format '{}'".format(key))
    if len(keys) > 1:
        raise Exception("ambigous label format '{}' (matching: {})".format(key, keys))

    key = keys[0]

    papersize = [float(i) for i in labelinfo[key][0]]
    imageable = [float(i) for i in labelinfo[key][1]]

    # print(papersize, imageable)
    # print("PWidth:  {}.2f".format(papersize[0] / 72.0 * 25.4)))
    # print("PHeight: {}.2f".format(papersize[1] / 72.0 * 25.4)))
    # print("x0:      {}.2f".format(imageable[0] / 72.0 * 25.4)))
    # print("x1:      {}.2f".format(imageable[1] / 72.0 * 25.4)))
    # print("Width:   {}.2f ({}d)".format((imageable[2] - imageable[0]) / 72.0 * 25.4,
    #                                     (imageable[2] - imageable[0]) / 72.0 * 300)))
    # print("Height:  {}.2f ({}d)".format((imageable[3] - imageable[1]) / 72.0 * 25.4,
    #                                     (imageable[3] - imageable[1]) / 72.0 * 300)))


""" Read netpbm image

    return width, height and image data
"""
def import_ppm(filename):
    f = open(filename, 'rb')

    format = f.read(2)

    if format.decode("utf-8") != "P4":
        raise Exception("Can only handle binary bitmap PBMs")

    c = f.read(1)
    while c.isspace():
        c = f.read(1)

    have_data = False
    width = 0
    while c.isdigit():
        width = width * 10 + int(c)
        c = f.read(1)
        have_data = True

    if not have_data:
        raise Exception("missing width data in bitmap PBM")

    while c.isspace():
        c = f.read(1)

    have_data = False
    height = 0
    while c.isdigit ():
        height = height * 10 + int(c)
        c = f.read(1)
        have_data = True

    if not have_data:
        raise Exception("missing height data in bitmap PBM")

    if not c.isspace():
        raise Exception( "missing whitespace after height data in PBM")

    imgdata = f.read()

    return (width, height, imgdata)

def do_print (filename):
    width, height, data = import_ppm(filename)

    if (width  != int ((imageable[2] - imageable[0]) / 72.0 * 300) or
        height != int ((imageable[3] - imageable[1]) / 72.0 * 300)):
        raise Exception("Invalid bitmap format for label size")

    bytes = (width + 7) // 8

    frame = bytearray(b"\x1B*")         # Restore defaults
    frame += bytearray(b"\x1BB\x00")    # dot tab 0
    frame += bytearray(b"\x1BD")
    frame.append(bytes)                 # Bytes per line
    frame += bytearray(b"\x1Bh")        # Text mode

    # label length - should be longer than actual length (syncs to hole then)
    formlen = int(height)

    frame += bytearray(b"\x1BL")
    frame.append(formlen // 256)
    frame.append(formlen % 256)

    sys.stdout.buffer.write(frame)

    for i in range(height):
        if data:
            line = data[:bytes]
            data = data[bytes:]
        sys.stdout.buffer.write(b"\x16" + line)

    sys.stdout.buffer.write(bytearray(b"\x1BE"))        # Form feed

if __name__ == '__main__':
    read_labelinfos ("static/ppd/lw450.ppd")
    set_labelinfo ("11355")

    do_print(sys.argv[1])
