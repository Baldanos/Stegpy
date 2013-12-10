import itertools
class alpha():

    def __init__(self):
        self.name="Alpha channel view"
        self.description="Generates a view of the alpha channel"
        self.inputdata="image"
        self.parameters = None
        self.mode="visual"
        self.splitpalette = [v for v in itertools.product(range(0, 255, 32), repeat=3)]


    def process(self, image):
        """
        Generates a view of the alpha channel
        """
        if image.mode == 'RGBA':
            out = image.copy()
        else:
            out = image.convert('RGBA')
        out.putdata( [self.splitpalette[a] for r, g, b, a in out.getdata() ] )
        return out

def register():
    return alpha()
