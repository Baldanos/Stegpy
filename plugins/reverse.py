class reverse():

    def __init__(self):
        self.name="Reversed colors view"
        self.description="Calculates the reverse colors for an image"
        self.inputdata="image"
        self.parameters = None
        self.mode="visual"

    def process(self, image):
        """
        Calculates the reverse colors for an image
        """
        if image.mode == 'RGBA':
            out = image.copy()
            out.putdata( [(self._reverse(r), self._reverse(g), self._reverse(b), a)
                for r, g, b, a in out.getdata()] )
        else:
            out = image.convert('RGB')
            out.putdata( [(self._reverse(r), self._reverse(g), self._reverse(b))
                for r, g, b in out.getdata()] )
        return out

    def _reverse(self, b):
        b = (b & 0xF0) >> 4 | (b & 0x0F) << 4
        b = (b & 0xCC) >> 2 | (b & 0x33) << 2
        b = (b & 0xAA) >> 1 | (b & 0x55) << 1
        return b

def register():
    return reverse()
