import itertools
from PIL import Image
class alpha():

    def __init__(self):
        self.name="LSB"
        self.description="Extracts data from the LSB data"
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
        self.path = int(self.path)
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
                        result.append(bool(locals()[chan] & int(getattr(self, 'm'+chan))))
        else:
            #In case the alpha channel has been added by mistake
            order = order.replace('a','')
            for pix in out.getdata():
                r, g, b = pix
                for chan in order:
                    if locals()['m'+chan]:
                        result.append(bool(locals()[chan] & locals()['m'+chan]))

        # Remove skipped bits
        result = result[int(self.sb):]

        return ''.join(chr(self._btoi(result[i:i+8])) for i in range(0, len(result), 8))

    def _btoi(self, binValue):
        """
        Takes a list of strings, a list of integers or a string and
        returns a decimal value
        """
        return int(''.join([str(int(x)) for x in binValue]), 2)

def register():
    return alpha()
    
#    extract = parser.add_argument_group('Data extraction', 'Data extraction options. This is useful for extracting LSB data for instance. You will need to set the channel masks to actually get data. When specifying a filename with the -w switch, data will be written in a file, otherwise on stdout')
#    extract.add_argument('-x', '--extract', dest='extract', action='store_true',
#            help='Extracts data from the image')
#    extract.add_argument('-p', '--path', dest='path', type=str,
#            choices=paths.keys()+['*'], default='lrud',
#            help='The path to follow when extracting data : (Up - Down - Left - Right)')
#    extract.add_argument('-o', '--order', dest='order', type=str,
#            choices=orders+['*'], default='rgba',
#            help='The order the LSBs must be extracted ')
#    extract.add_argument('-rm', '--red-mask', dest='redmask', type=int,
#            default=0, help='The red channel mask')
#    extract.add_argument('-gm', '--green-mask', dest='greenmask', type=int,
#            default=0, help='The green channel mask')
#    extract.add_argument('-bm', '--blue-mask', dest='bluemask', type=int,
#            default=0, help='The blue channel mask')
#    extract.add_argument('-am', '--alpha-mask', dest='alphamask', type=int,
#            help='The alpha channel mask')
#    extract.add_argument('-sb', '--skip-bits', dest='skipbits', type=int,
#            default=0, help='Nuber of bits to skip')
