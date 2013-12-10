#!/usr/bin/env python


#Stegpy - a simple steganalysis script
#Copyright (C) 2013 Nicolas Oberli
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import os, sys
import itertools
import argparse
from Tkinter import Tk , StringVar, OptionMenu, Label
import tkSimpleDialog
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
        self.views = OptionMenu(self.window, self.currentView,
                *options, command=self.applyFilter)
        self.views.pack()

        self.tkImage = ImageTk.PhotoImage(image)
        self.lblImage = Label(image=self.tkImage)
        self.lblImage.bind('<Button-1>', self.displayInfos)
        self.lblImage.bind('<Button-3>', self.save)
        self.lblImage.image = self.tkImage
        self.lblImage.pack()

        self.status = StringVar()
        self.lblStatus = Label(textvariable=self.status, justify='right')
        self.lblStatus.pack()

        self.window.mainloop()

    def displayInfos(self, event):
        """
        Displays the coordinates in the status bar
        """
        x = int((event.x-0.1)/args.scalefactor)
        y = int((event.y-0.1)/args.scalefactor)
        pixel = orig.getpixel((x,y))
        self.setStatus("Coordinates : (%s:%s) - Pixel value : (%s,%s,%s)" %
                (
                    x, y,
                    pixel[0], pixel[1], pixel[2]
                    )
                )

    def setStatus(self, text):
        """
        Changes the text in the status bar
        """
        self.status.set(text)

    def save(self, event):
        """
        Saves the filtered image to a file
        """
        import tkFileDialog
        options = {'filetypes':[('PNG','.png'),('GIF','.gif')]}
        outfile = tkFileDialog.asksaveasfilename(**options)
        if outfile == '':
            return
        else:
            self.image.save(outfile)
            return

    def genViews(self):
        """
        Generates filters based on the source image
        """
        self.filters={}
        for plug in viewPlugins:
            self.filters.update({plug.name:viewPlugins.index(plug)})

    def applyFilter(self, view):
        """
        Applies a filter to the image
        """
        view = self.filters[self.currentView.get()]
        plugin = viewPlugins[view]
        if plugin.parameters:
            for param in plugin.parameters.keys():
                a = tkSimpleDialog.askinteger('Question', plugin.parameters[param])
                if a is not None:
                    setattr(viewPlugins[view],param,a)
        self.image = viewPlugins[view].process(self.original)

        self.showImage(self.currentView.get(), self.image)
        self.setStatus("")
        return

    def showImage(self, title, image):
        """
        Updates the image in the window
        """
        self.tkImage = ImageTk.PhotoImage(image)
        self.lblImage.configure(image=self.tkImage)
        self.lblImage.image = self.tkImage

def itob(s):
    """
    Returns the binary expression of an int value as a string
    """
    return bin(s)[2:].zfill(8)

def btoi(binValue):
    """
    Takes a list of strings, a list of integers or a string and
    returns a decimal value
    """
    return int(''.join([str(int(x)) for x in binValue]), 2)

def reverse(b):
    b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
    b = (b & 0xCC) >> 2 | (b & 0x33) << 2
    b = (b & 0xAA) >> 1 | (b & 0x55) << 1
    return b

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
        colors = {number:[color, (palette[color*3], palette[(color*3)+1],
            palette[(color*3)+2])]
            for number, color in image.getcolors()}

        numbers = colors.keys()
        numbers.sort();numbers.reverse()
        print '  Nb   Color            Times used'
        for number in numbers:
            print '  %03s  %15s  (%s times)' % \
                    (colors[number][0], colors[number][1], number)
        image = image.convert('RGB')

    print 'Image colors : '
    colors = {n:c for n, c in [color for color in image.getcolors()]}
    numbers = colors.keys()
    numbers.sort();numbers.reverse()
    print '  Color           Times used'
    for number in numbers:
        print '  %15s (%02s times)' % (colors[number], number)
    print ''
    print 'Color statistics : '
    if image.mode == 'RGBA':
        print '  Red distribution :     %s' % \
                str(list(set([r for r,g,b,a in colors.values()])))
        print '  Green distribution :   %s' % \
                str(list(set([g for r,g,b,a in colors.values()])))
        print '  Blue distribution :    %s' % \
                str(list(set([b for r,g,b,a in colors.values()])))
        print '  Alpha distribution :   %s' % \
                str(list(set([a for r,g,b,a in colors.values()])))
    else:
        stat = image.convert('RGB')
        print '  Red distribution :     %s' % \
                str(list(set([r for r,g,b in colors.values()])))
        print '  Green distribution :   %s' % \
                str(list(set([g for r,g,b in colors.values()])))
        print '  Blue distribution :    %s' % \
                str(list(set([b for r,g,b in colors.values()])))


def saveFile(filename, data):
    outfile = open(filename, 'wb')
    outfile.write(data)
    outfile.close()
    print 'Wrote data to %s' % outfilename

viewPlugins = []
commandPlugins = []
plugins = []

def loadPlugins():
    import os
    import sys
    sys.path.insert(0,'plugins/')
    plugs = []
    for filename in os.listdir('plugins/'):
        name, ext = os.path.splitext(filename)
        if ext.endswith(".py"):
            plugs.append(__import__(name))
    for plug in plugs:
        plugin = plug.register()
        if plugin.mode == 'visual':
            viewPlugins.append(plugin)
        elif plugin.mode == 'command':
            commandPlugins.append(plugin)
        else:
            plugins.append(plugin)

if __name__ == '__main__':

    loadPlugins()

    paths = { 'lrud':0, 'rlud':1, 'lrdu':2, 'rldu':3, 'udlr':4, 'udrl':5,
            'dulr':6, 'durl':7}
    orders = [''.join(o) for o in itertools.permutations('rgba', 1)]
    orders += [''.join(o) for o in itertools.permutations('rgba', 2)]
    orders += [''.join(o) for o in itertools.permutations('rgba', 3)]
    orders += [''.join(o) for o in itertools.permutations('rgba', 4)]

    parser = argparse.ArgumentParser(
            description='Analyzes an image to find steganography data.')
    parser.add_argument('filename', metavar='FILE', type=file,
            help='file to analyze')
    visualMode = parser.add_argument_group('Visual mode')
    visualMode.add_argument('-V', '--visual', dest='visual', action='store_true',
            help='Starts visual mode')
    visualMode.add_argument('-ts', '--thumbnail-size', dest='thumbsize', type=int,
            metavar='SIZE', default=0, help='Use a thumbnail of maximum SIZE pixels to view generated images')
    visualMode.add_argument('-sf', '--scale-factor', dest='scalefactor', type=float,
            metavar='FACTOR', default=1, help='Scale the image to FACTOR. can be positive or a fraction')
    commandGroup = parser.add_argument_group('Command mode')
    commandGroup.add_argument('-C', '--command', dest='command', action='store_true',
            help='Starts command mode')
    commandGroup.add_argument('-p', '--plugin', dest='plugin',
            choices = [plugin.name for plugin in commandPlugins],
            help='Use the following plugin (unset to have a list)')
    for plugin in commandPlugins:
        if plugin.parameters is not None:
            a = parser.add_argument_group(plugin.name, description=plugin.description)
            for argument in plugin.parameters.keys():
                a.add_argument('-'+argument, dest = argument, help=plugin.parameters[argument])

    args = parser.parse_args()

    try:
        orig = Image.open(args.filename)
    except IOError, e:
        print e.message
        sys.exit(1)

    #Enter visual mode
    if args.visual:
        #Creating a thumbnail to work with
        if args.thumbsize:
            thumb = orig.copy()
            thumb.thumbnail((args.thumbsize, args.thumbsize), Image.NEAREST)
            v = Viewer(thumb)
        #If scale factor is used
        elif args.scalefactor:
            image = orig.resize(tuple([int(args.scalefactor*x) for x in orig.size]), Image.NEAREST)
            v = Viewer(image)
        else:
            v = Viewer(orig)
        sys.exit(0)
    elif args.command:
        if args.plugin is None:
            print "Missing plugin name, use one of the following :"
            for plug in commandPlugins:
                if plug.mode == "command":
                    print "%s  - %s" % (plug.name, plug.description)
        elif args.plugin not in [plugin.name for plugin in commandPlugins]:
            print "Error: Plugin does not exist"
            parser.print_usage()
        else:
            #Get the right plugin
            for plugin in commandPlugins:
                if plugin.name == args.plugin:
                    break
            for parameter in plugin.parameters.keys():
                setattr(plugin, parameter, getattr(args, parameter))
            print plugin.process(orig)

            pass

    else:
        print "Error : Please use either -C or -V"
        parser.print_usage()
    
    #if args.extract:
    #    if args.path == '*':
    #        for path in paths.keys():
    #            if args.order == '*':
    #                for order in orders:
    #                    data = extractBits(orig, paths[path], args.redmask,
    #                            args.greenmask, args.bluemask, args.alphamask,
    #                            args.skipbits, order)
    #                    outfilename = output+os.path.basename(args.filename.name)+\
    #                            '_data_%s_%s_%s_%s_%s_%s.bin' % \
    #                            (args.redmask, args.greenmask, args.bluemask,
    #                                    args.alphamask, path, order)
    #                    saveFile(outfilename, data)
    #            else:
    #                data = extractBits(orig, paths[path], args.redmask,
    #                        args.greenmask, args.bluemask, args.alphamask,
    #                        args.skipbits, args.order)
    #                outfilename = output+os.path.basename(args.filename.name)+\
    #                        '_data_%s_%s_%s_%s_%s_%s.bin' % \
    #                        (args.redmask, args.greenmask, args.bluemask,
    #                                args.alphamask, path, args.order)
    #                saveFile(outfilename, data)
    #    else:
    #        if args.order == '*':
    #            for order in orders:
    #                data = extractBits(orig, paths[args.path], args.redmask,
    #                        args.greenmask, args.bluemask, args.alphamask,
    #                        args.skipbits, order)
    #                outfilename = output+os.path.basename(args.filename.name)+\
    #                        '_data_%s_%s_%s_%s_%s_%s.bin' % \
    #                        (args.redmask, args.greenmask, args.bluemask,
    #                                args.alphamask, args.path, order)
    #                saveFile(outfilename, data)
    #        else:
    #            data = extractBits(orig, paths[args.path], args.redmask, args.greenmask, args.bluemask, args.alphamask, args.skipbits, args.order)
    #            if args.output:
    #                outfilename = output+os.path.basename(args.filename.name)+\
    #                        '_data_%s_%s_%s_%s_%s_%s.bin' % \
    #                        (args.redmask, args.greenmask, args.bluemask,
    #                                args.alphamask, args.path, args.order)
    #                outfile = open(outfilename, 'wb')
    #                outfile.write(data)
    #                outfile.close()
    #                print ''
    #                print 'Wrote data to %s' % outfilename
    #            else:
    #                sys.stdout.write(data)
