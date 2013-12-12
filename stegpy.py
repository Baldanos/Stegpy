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


import os
import sys
import argparse
from Tkinter import Tk , StringVar, OptionMenu, Label
import tkSimpleDialog
import tkFileDialog
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
        pixel = orig.getpixel((x, y))
        self.setStatus("Coordinates : (%s:%s) - Pixel value : %s" %
                (x, y, str(pixel)))

    def setStatus(self, text):
        """
        Changes the text in the status bar
        """
        self.status.set(text)

    def save(self, event):
        """
        Saves the filtered image to a file
        """
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
        self.filters = {}
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
                a = tkSimpleDialog.askinteger(
                        'Question', plugin.parameters[param])
                if a is not None:
                    setattr(viewPlugins[view], param, a)
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


viewPlugins = []
commandPlugins = []
plugins = []

def loadPlugins():
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

def parseVisualParameters(parent = None):
    params = argparse.ArgumentParser( parents=[parent],
            description="Visual mode parameters")
    params.add_argument('-ts', '--thumbnail-size', dest='thumbsize', type=int,
            metavar='SIZE', default=0,
            help='Use a thumbnail of maximum SIZE pixels to view generated images')
    params.add_argument('-sf', '--scale-factor', dest='scalefactor', type=float,
            metavar='FACTOR', default=1,
            help='Scale the image to FACTOR. can be positive or a fraction')
    return params

def parseCommandParameters( parent=None):
    params = argparse.ArgumentParser( parents=[parent], add_help=False,
            description="Command mode parameters")
    params.add_argument('-p', '--plugin', dest='plugin',
            choices = [plugin.name for plugin in commandPlugins],
            help='Use the following plugin (unset to have a list)')
    return params

if __name__ == '__main__':

    loadPlugins()


    parser = argparse.ArgumentParser(
            description='Analyzes an image to find steganography data.',
            add_help=False)
    parser.add_argument('filename', metavar='FILE', type=file,
            help='file to analyze')
    applicationMode = parser.add_mutually_exclusive_group(required=True)
    applicationMode.add_argument('-V', '--visual', dest='visual',
            action='store_true', help='Starts visual mode')
    applicationMode.add_argument('-C', '--command', dest='command',
            action='store_true', help='Starts command mode')

    args = parser.parse_known_args()[0]

    try:
        orig = Image.open(args.filename)
    except IOError, e:
        print e.message
        sys.exit(1)

    #Enter visual mode
    if args.visual:
        parser = parseVisualParameters(parser)
        args = parser.parse_known_args()[0]
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
        commandParser = parseCommandParameters(parser)
        args = commandParser.parse_known_args()[0]
        if args.plugin is None:
            commandParser.print_help()
        else:
            #Get the right plugin
            for plugin in commandPlugins:
                if plugin.name == args.plugin:
                    break
            if plugin.parameters is not None:
                pluginParser = plugin.get_argParser()
                pluginParser.parents = [parser, commandParser]
                args = pluginParser.parse_known_args()[0]
                for param in plugin.parameters.keys():
                    try:
                        setattr(plugin, param, getattr(args, param))
                    except AttributeError, e:
                        pass
            print plugin.process(orig)

        pass
