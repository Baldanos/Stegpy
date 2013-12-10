class isolate():

    def __init__(self):
        self.name="Isolate color view"
        self.description="Isolates a color, and displays it as black on white"
        self.inputdata="image"
        self.parameters = {
                'rr': 'Red reference',
                'rg':'Green reference',
                'rb':'Blue reference',
                'ra':'Alpha reference'
                }
        self.mr=0
        self.mg=0
        self.mb=0
        self.mode="visual"

    def process(self, image):
        """
        Generates an image with a color filter based on a bitmask
        """
        if image.mode == 'RGBA':
            out = image.copy()
            out.putdata( [self._highlight(r,g,b,a)
                for r, g, b, a in out.getdata()] )
        else:
            out = image.convert('RGB')
            out.putdata( [ self._highlight(r,g,b)
                for r, g, b in out.getdata()] )
        return out

    def _highlight(r,g,b):
        if (r == rr and g == rg and b == rb):
            return (0, 0, 0)
        else:
            return (255, 255, 255)

    def _highlight(r,g,b, a):
        if (r == rr and g == rg and b == rb and a == ra):
            return (0, 0, 0, 0)
        else:
            return (255, 255, 255, 255)
        

def register():
    return isolate()
