class info():

    def __init__(self):
        self.name="color_info"
        self.description="Displays the color information about an image"
        self.inputdata="image"
        self.parameters = None
        self.mode="command"


    def process(self, image):
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
        colors = {n:c for n, c in [color for color in image.getcolors(image.size[0]*image.size[1])]}
        numbers = colors.keys()
        numbers.sort();numbers.reverse()
        print '  Color                Times used'
        for number in numbers:
            print '  %20s (%02s times)' % (colors[number], number)
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

        return ''

def register():
    return info()
