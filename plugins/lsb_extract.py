import itertools
from PIL import Image

paths = { 'lrud':0, 'rlud':1, 'lrdu':2, 'rldu':3, 'udlr':4, 'udrl':5,
                        'dulr':6, 'durl':7}

class lsb_extract():

    def __init__(self):
        self.name="lsb_extract"
        self.description="Extracts data from the pixel LSB"
        self.inputdata="image"
        self.parameters = {
                'path': 'The path to follow when extracting data',
                'mr': 'Red mask',
                'mg':'Green mask',
                'mb':'Blue mask',
                'ma':'Alpha mask',
                'sb':'Skip first n bits',
                'order':'Color order'
                }
        self.mr=0
        self.mg=0
        self.mb=0
        self.ma=0
        self.sb=0
        self.order='rgb'
        self.mode="command"

    def get_argParser(self):
        import argparse
        orders = [''.join(o) for o in itertools.permutations('rgba', 1)]
        orders += [''.join(o) for o in itertools.permutations('rgba', 2)]
        orders += [''.join(o) for o in itertools.permutations('rgba', 3)]
        orders += [''.join(o) for o in itertools.permutations('rgba', 4)]
        parser = argparse.ArgumentParser()

        a = parser.add_argument_group(self.name, description=self.description)
        a.add_argument('--path', dest = 'path', type=str, choices=paths.keys(),
                    help="Path to follow when extracting", default='lrud')
        a.add_argument('--mr', dest = 'mr', type=int,
                    help='Red mask', default=0)
        a.add_argument('--mg', dest = 'mg', type=int,
                    help='Green mask', default=0)
        a.add_argument('--mb', dest = 'mb', type=int,
                    help='Blue mask', default=0)
        a.add_argument('--ma', dest = 'ma', type=int,
                    help='Alpha mask', default=0)
        a.add_argument('--sb', dest = 'sb', type=int,
                    help='Skip bits', default=0)
        a.add_argument('--order', dest = 'order', type=str, choices=orders,
                    help='Color order', default='rgb')
        return parser


    def process(self, image):
        """
        Extracts bits of data from image.

        Masks represents the bits to extract
        Path means the path to follow to extract data :
            0 - Left-Right-Up-Down
            1 - Right-Left-Up-Down
            2 - Left-Right-Down-Up
            3 - Right-Left-Down-Up
            4 - Up-Down-Left-Right
            5 - Up-Down-Right-Left
            6 - Down-Up-Left-Right
            7 - Down-Up-Right-Left

        sb is used to skip the first n bits
        """
        result = []

        if self.ma is None:
            self.ma = 0

        if image.mode == 'P':
            out = image.convert('RGBA')
        else:
            out = image.copy()

        #When reading from right to left, just flip the image
        self.path = paths[self.path]
        if self.path & 0x1 :
            out = out.transpose(Image.FLIP_LEFT_RIGHT)

        #When reading from down to up, flip the image
        if self.path & 0x2 :
            out = out.transpose(Image.FLIP_TOP_BOTTOM)

        #Revert the image when reading top-down first
        if self.path & 0x4 :
            out = out.transpose(Image.FLIP_LEFT_RIGHT)
            out = out.transpose(Image.ROTATE_90)

        if out.mode == 'RGBA':
            for pix in out.getdata():
                r, g, b, a = pix
                for chan in self.order:
                    if getattr(self, 'm'+chan):
                        result.append(bool(locals()[chan] & getattr(self, 'm'+chan)))
        else:
            #In case the alpha channel has been added by mistake
            order = self.order.replace('a','')
            for pix in out.getdata():
                r, g, b = pix
                for chan in order:
                    if getattr(self, 'm'+chan):
                        result.append(bool(locals()[chan] & getattr(self, 'm'+chan)))

        # Remove skipped bits
        result = result[int(self.sb):]

        return ''.join(chr(self._btoi(result[i:i+8])) for i in range(0, len(result), 8))

    def _btoi(self, binValue):
        """
        Takes a list of strings, a list of integers or a string and
        returns a decimal value
        """
        return int(''.join([str(int(x)) for x in binValue]), 2)


    def _saveFile(self, filename, data):
        outfile = open(filename, 'wb')
        outfile.write(data)
        outfile.close()
        print 'Wrote data to %s' % outfilename

def register():
    return lsb_extract()
