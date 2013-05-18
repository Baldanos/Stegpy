#!/usr/bin/env python

import os, sys
import itertools
import argparse
from Tkinter import *
from PIL import Image, ImageTk

def showImage(title, image):
    lblTitle=Label(text=title+' '+str(image.size))
    lblTitle.pack()
    tkImage = ImageTk.PhotoImage(image)
    lblImage = Label(image=tkImage)
    lblImage.image = tkImage
    lblImage.pack()

def grouper(n, iterable, fillvalue=None):
    """
    Groups iterable into groups of n elements, filled with fillvalue
    """
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def itob(s):
    """
    Returns the binary expression of an int value as a string
    """
    return bin(s)[2:].zfill(8) 

def btoi(binValue):
    """
    Takes a list of strings, a list of integers or a string and returns a decimal value
    """
    return int(''.join([str(int(x)) for x in binValue]), 2)

def extractBits(image, path=0, mr=0, mg=0, mb=0, ma=0):
    """
    Extracts bits of data from image.

    Mask represents the bits to extract
    Path means the path to follow to extract data :
        0 - Left-Right-Up-Down
        1 - Right-Left-Up-Down
        2 - Left-Right-Down-Up
        3 - Right-Left-Down-Up
        4 - Up-Down-Left-Right
        5 - Up-Down-Right-Left
        6 - Down-Up-Left-Right
        7 - Down-Up-Right-Left
    """
    #TODO
    result = [] 

    if ma is None:
        ma=0

    #When reading from right to left, just flip the image
    if path == 0 :
        out = image.copy()
    if path & 0x1 :
        out = image.transpose(Image.FLIP_LEFT_RIGHT)

    #When reading from down to up, flip the image
    if path & 0x2 :
        out = image.transpose(Image.FLIP_TOP_BOTTOM)

    #Revert the image when reading top-down first
    if path & 0x4 :
        out = image.transpose(Image.FLIP_LEFT_RIGHT)
        out = out.transpose(Image.ROTATE_90)

    if out.mode == 'RGBA':
        for pix in out.getdata():
            r,g,b,a = pix
            if mr:
                result.append(bool(r & mr))
            if mg:
                result.append(bool(g & mg))
            if mb:
                result.append(bool(b & mb))
            if ma:
                result.append(bool(a & ma))
    else:
        for pix in out.getdata():
            r,g,b = pix
            if mr:
                result.append(bool(r & mr))
            if mg:
                result.append(bool(g & mg))
            if mb:
                result.append(bool(b & mb))


    return ''.join(chr(btoi(result[i:i+8])) for i in range(0,len(result),8))

def genInvert(image):
    """
    Calculates the invert colors for an image
    """
    if image.mode == 'RGBA':
        out = image.copy()
        out.putdata( [(r^0xff,g^0xff,b^0xff,a) for r,g,b,a in out.getdata()] )
    else:
        out = image.convert('RGB')
        out.putdata( [(r^0xff,g^0xff,b^0xff) for r,g,b in out.getdata()] )

    return out

def genReverse(image):
    """
    Calculates the reverse colors for an image
    """
    if image.mode == 'RGBA':
        out = image.copy()
        out.putdata( [(btoi(itob(r)[::-1]),btoi(itob(g)[::-1]),btoi(itob(b)[::-1]),a) for r,g,b,a in out.getdata()] )
    else:
        out = image.convert('RGB')
        out.putdata( [(btoi(itob(r)[::-1]),btoi(itob(g)[::-1]),btoi(itob(b)[::-1])) for r,g,b in out.getdata()] )

    return out

def genMask(image, mr=0, mg=0, mb=0, ma=0xff):
    """
    Generates an image with a color filter based on a bitmask
    """

    if ma is None:
        ma=0xff

    if image.mode == 'RGBA':
        out = image.copy()
        out.putdata( [((r&mr>0)*0xff,(g&mg>0)*0xff,(b&mb>0)*0xff,(a&ma>0)*0xff) for r,g,b,a in out.getdata()] )
    else:
        out = image.convert('RGB')
        out.putdata( [((r&mr>0)*0xff,(g&mg>0)*0xff,(b&mb>0)*0xff) for r,g,b in out.getdata()] )

    return out



def genDiff(image):
    """
    Generates an image containing the pixel difference of the source image
    """
    if image.mode=='RGBA':
        out=image.copy()
        sx, sy = image.size
        for x in xrange(sx):
            for y in xrange(sy):
                try:
                    if image.getpixel((x,y)) == image.getpixel((x-1,y)):
                        out.putpixel((x,y),(0,0,0,255))
                    else:
                        out.putpixel((x,y),(255,255,255,255))
                except:
                        out.putpixel((x,y),(0,0,0,255))
    else:
        out = image.convert('RGB')
        sx, sy = image.size
        for x in xrange(sx):
            for y in xrange(sy):
                try:
                    if image.getpixel((x,y)) == image.getpixel((x-1,y)):
                        out.putpixel((x,y),(0,0,0))
                    else:
                        out.putpixel((x,y),(255,255,255))
                except:
                        out.putpixel((x,y),(0,0,0))

    return out


def printColorInfos(image):
    """
    displays color information about the file
    """
    print 'File color mode : %s' % image.mode
    print ''
    if image.mode == 'P':
        print ''
        print 'Palette information :'
        palette = image.getpalette()
        colors = {number:[color,(palette[color*3],palette[(color*3)+1],palette[(color*3)+2])] for number, color in image.getcolors()}

        numbers=colors.keys();
        numbers.sort();numbers.reverse()
        print '  Nb   Color            Times used'
        for number in numbers:
            print '  %03s  %15s  (%s times)' % (colors[number][0], colors[number][1], number)
        image = image.convert('RGB')

    print 'Image colors : '
    colors={n:c for n,c in [color for color in image.getcolors()]}
    numbers=colors.keys();
    numbers.sort();numbers.reverse()
    print '  Color           Times used'
    for number in numbers:
        print '  %15s (%02s times)' % (colors[number], number)
    print ''
    print 'Color statistics : '
    if image.mode == 'RGBA':
        print '  Red distribution :     %s' % str(list(set([r for r,g,b,a in colors.values()])))
        print '  Green distribution :   %s' % str(list(set([g for r,g,b,a in colors.values()])))
        print '  Blue distribution :    %s' % str(list(set([b for r,g,b,a in colors.values()])))
        print '  Alpha distribution :   %s' % str(list(set([a for r,g,b,a in colors.values()])))
    else:
        stat = image.convert('RGB')
        print '  Red distribution :     %s' % str(list(set([r for r,g,b in colors.values()])))
        print '  Green distribution :   %s' % str(list(set([g for r,g,b in colors.values()])))
        print '  Blue distribution :    %s' % str(list(set([b for r,g,b in colors.values()])))


        
if __name__ == '__main__':

    paths = { 'LRUD':0, 'RLUD':1, 'LRDU':2, 'RLDU':3, 'UDLR':4, 'UDRL':5, 'DULR':6, 'DURL':7 }

    parser = argparse.ArgumentParser(description='Analyzes an image to find steganography data.')
    parser.add_argument('filename', metavar='FILE', type=file, help='file to analyze')
    parser.add_argument('-w', '--write', dest='output', metavar = 'DESTFOLDER', help='use DESTFOLDER to write files')
    parser.add_argument('-ts', '--thumbnail-size', dest='thumbsize', type=int, metavar='SIZE', default=0, help='Use a thumbnail of maximum SIZE pixels to view generated images')
    visual = parser.add_argument_group('Visualisation', 'Visualisation options. When specifying the -w switch, all generated images will be written with an extension')
    visual.add_argument('-v', '--visual', dest='visual', action='store_true', help='Display generated images')
    visual.add_argument('-d', '--difference', dest='difference', action='store_true', help='Generates a difference image. If pixel is different from the next one, change its color')
    visual.add_argument('-r', '--reverse', dest='reverse', action='store_true', help='Generates a reversed image. Pixel value is binary reversed')
    visual.add_argument('-i', '--invert', dest='invert', action='store_true', help='Generates a reversed image (pixel ^ 0xff)')
    visual.add_argument('-m', '--mask', dest='mask', action='store_true', help='Generates a masked view of the image. If the masked channel is >0, the channel value for this pixel will be 0xff')
    extract = parser.add_argument_group('Data extraction', 'Data extraction options. This is useful for extracting LSB data for instance. You will need to set the channel masks to actually get data. When specifying a filename with the -w switch, data will be written in a file, otherwise on stdout')
    extract.add_argument('-x', '--extract', dest='extract', action='store_true', help='Extracts data from the image')
    extract.add_argument('-p', '--path', dest='path', type=str, choices=paths, default='LRUD', help='The path to follow when extracting data : (Up - Down - Left - Right)')
    extract.add_argument('-rm', '--red-mask', dest='redmask', type=int, default=0, help='The red channel mask')
    extract.add_argument('-gm', '--green-mask', dest='greenmask', type=int, default=0, help='The green channel mask')
    extract.add_argument('-bm', '--blue-mask', dest='bluemask', type=int, default=0, help='The blue channel mask')
    extract.add_argument('-am', '--alpha-mask', dest='alphamask', type=int, help='The alpha channel mask')
    info = parser.add_argument_group('Image information', 'Prints various information about the image')
    info.add_argument('-C', '--colors', dest='colors', action='store_true', help='Shows the colors used in the image')
    info.add_argument('-I', '--info', dest='info', action='store_true', help='Shows the colors used in the image')


    args = parser.parse_args()
    if args.output:
        if  os.path.isdir(args.output):
            output = args.output
        else:
            print 'Error, %s is not a directory' % args.output
            sys.exit(1)
    else:
        output = None
        
    try:
        orig = Image.open(args.filename)
    except IOError, e:
        print e.message
        sys.exit(1)

    if args.info:
        print 'Filename :        %s' % orig.filename
        print 'Image size :      %s' % str(orig.size)
        print 'File format :     %s' % orig.format_description
        print ''

    if args.colors:
        printColorInfos(orig)

    if args.visual:
        window=Tk()

    #Creating a thumbnail to work with
    if args.thumbsize:
        thumb = orig.copy()
        thumb.thumbnail((args.thumbsize, args.thumbsize),Image.NEAREST)
    else:
        thumb = None

    if args.difference:
        if visual:
            if thumb:
                showImage('Difference', genDiff(thumb))
            else:
                showImage('Difference', genDiff(orig))
        if output:
            out = genDiff(orig)
            out.save(output+os.path.basename(f.name)+'_difference.'+out.format.lower())
    
    if args.reverse:
        if visual:
            if thumb:
                showImage('Reverse', genReverse(thumb))
            else:
                showImage('Reverse', genReverse(orig))
        if output:
            out = genReverse(orig)
            out.save(output+os.path.basename(f.name)+'_reverse.'+out.format.lower())
    
    if args.invert:
        if visual:
            if thumb:
                showImage('Invert', genInvert(thumb))
            else:
                showImage('Invert', genInvert(orig))
        if output:
            out = genInvert(orig)
            out.save(output+os.path.basename(f.name)+'_invert.'+out.format.lower())
    
    if args.mask:
        if visual:
            if thumb:
                showImage('Mask (%s,%s,%s,%s)' % (args.redmask, args.greenmask, args.bluemask, args.alphamask), genMask(thumb,args.redmask, args.greenmask, args.bluemask, args.alphamask))
            else:
                showImage('Mask (%s,%s,%s,%s)' % (args.redmask, args.greenmask, args.bluemask, args.alphamask), genMask(orig, args.redmask, args.greenmask, args.bluemask, args.alphamask))
        if output:
            out = genMask(orig, paths[args.path], args.redmask, args.greenmask, args.bluemask, args.alphamask)
            out.save(output+os.path.basename(f.name)+'_mask.'+out.format.lower())
    
    if args.extract:
        data = extractBits(orig, paths[args.path], args.redmask, args.greenmask, args.bluemask, args.alphamask) 
        if output:
            file = open(output+os.path.basename(args.filename.name)+'_data_%s_%s_%s_%s.bin' % (args.redmask, args.greenmask, args.bluemask, args.alphamask), 'wb')
            file.write(data)
            file.close()
            print ''
            print 'Wrote data to ' + output+os.path.basename(args.filename.name)+'_data_%s_%s_%s_%s.bin' % (args.redmask, args.greenmask, args.bluemask, args.alphamask)
        else:
            sys.stdout.write(data)

    if args.visual:
        window.mainloop()
