#!/usr/bin/env python

import os, sys
import itertools
import argparse
from Tkinter import *
from PIL import Image, ImageTk

class Viewer():
    
    def __init__(self, image):
        self.original = image
        self.image = image.copy()
        self.window = Tk()

        self.genViews()
        self.currentView = StringVar(self.window)
        self.currentView.set('Original')
        options = self.filters.keys();options.sort()
        self.views = OptionMenu(self.window, self.currentView, *options, command=self.applyFilter)
        self.views.pack()

        self.tkImage = ImageTk.PhotoImage(image)
        self.lblImage = Label(image=self.tkImage)
        self.lblImage.image = self.tkImage
        self.lblImage.pack()

        self.window.mainloop()

    def save(self):
        return


    def genViews(self):
        """
        Generates filters based on the source image
        """
        self.filters = {
                'Original'                      : 0,
                'Pixel difference'              : 1,
                'Pixel invert (XOR)'            : 2,
                'Pixel reverse (lsb<->msb)'     : 3,
                'Value filter (00000001)'       : 4,
                'Value filter (00000010)'       : 5,
                'Value filter (00000100)'       : 6,
                'Value filter (00001000)'       : 7,
                'Value filter (00010000)'       : 8,
                'Value filter (00100000)'       : 9,
                'Value filter (01000000)'       : 10,
                'Value filter (10000000)'       : 11,
                }

    def applyFilter(self, view):
        """
        Applies a filter to the image
        """
        view = self.filters[self.currentView.get()]
        if view == 0:
            self.showImage(self.currentView.get(), self.original)
            return
        elif view == 1 :
            self.image = genDiff(self.original)
        elif view == 2 :
            self.image = genInvert(self.original)
        elif view == 3 :
            self.image = genReverse(self.original)
        elif view == 4 :
            self.image = genMask(self.original, 1,1,1)
        elif view == 5 :
            self.image = genMask(self.original, 2,2,2)
        elif view == 6 :
            self.image = genMask(self.original, 4,4,4)
        elif view == 7 :
            self.image = genMask(self.original, 8,8,8)
        elif view == 8 :
            self.image = genMask(self.original, 16,16,16)
        elif view == 9 :
            self.image = genMask(self.original, 32,32,32)
        elif view == 10 :
            self.image = genMask(self.original, 64,64,64)
        elif view == 11 :
            self.image = genMask(self.original, 128,128,128)
        self.showImage(self.currentView.get(), self.image)
        return


    def showImage(self,title, image):
        """
        Updates the image in the window
        """
        self.tkImage = ImageTk.PhotoImage(image)
        self.lblImage.configure(image=self.tkImage)
        self.lblImage.image = self.tkImage


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
    parser.add_argument('-ts', '--thumbnail-size', dest='thumbsize', type=int, metavar='SIZE', default=0, help='Use a thumbnail of maximum SIZE pixels to view generated images')
    parser.add_argument('-v', '--visual', dest='visual', action='store_true', help='Starts visual mode')
    extract = parser.add_argument_group('Data extraction', 'Data extraction options. This is useful for extracting LSB data for instance. You will need to set the channel masks to actually get data. When specifying a filename with the -w switch, data will be written in a file, otherwise on stdout')
    extract.add_argument('-x', '--extract', dest='extract', action='store_true', help='Extracts data from the image')
    extract.add_argument('-p', '--path', dest='path', type=str, choices=paths, default='LRUD', help='The path to follow when extracting data : (Up - Down - Left - Right)')
    extract.add_argument('-rm', '--red-mask', dest='redmask', type=int, default=0, help='The red channel mask')
    extract.add_argument('-gm', '--green-mask', dest='greenmask', type=int, default=0, help='The green channel mask')
    extract.add_argument('-bm', '--blue-mask', dest='bluemask', type=int, default=0, help='The blue channel mask')
    extract.add_argument('-am', '--alpha-mask', dest='alphamask', type=int, help='The alpha channel mask')
    extract.add_argument('-w', '--write', dest='output', type=file, metavar = 'DESTFILE', help='use DESTFILE to write data')
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


    #Creating a thumbnail to work with
    if args.thumbsize:
        thumb = orig.copy()
        thumb.thumbnail((args.thumbsize, args.thumbsize),Image.NEAREST)
    else:
        thumb = None

    if args.visual:
        if thumb:
            v = Viewer(thumb)
        else:
            v = Viewer(orig)
        sys.exit(0)

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