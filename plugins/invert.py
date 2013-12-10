class invert():

    def __init__(self):
        self.name="Inverted colors view"
        self.description="Calculates the invert colors for an image"
        self.inputdata="image"
        self.parameters = None
        self.mode="visual"

    def process(self, image):
        """
        Calculates the invert colors for an image
        """
        if image.mode == 'RGBA':
            out = image.copy()
            out.putdata( [(r^0xff, g^0xff, b^0xff, a)
                for r, g, b, a in out.getdata()] )
        else:
            out = image.convert('RGB')
            out.putdata( [(r^0xff, g^0xff, b^0xff) 
                for r, g, b in out.getdata()] )
        return out

def register():
    return invert()
