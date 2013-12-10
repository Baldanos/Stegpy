class mask():

    def __init__(self):
        self.name="Color mask view"
        self.description="Generates an image with a color filter based on a bitmask"
        self.inputdata="image"
        self.parameters = {
                'mr': 'Red mask',
                'mg':'Green mask',
                'mb':'Blue mask',
                'ma':'Alpha mask'
                }
        self.mr=0
        self.mg=0
        self.mb=0
        self.ma=0xff
        self.mode="visual"

    def process(self, image):
        """
        Generates an image with a color filter based on a bitmask
        """
        if self.ma is None:
            self.ma = 0xff

        if image.mode == 'RGBA':
            out = image.copy()
            out.putdata( [((r&self.mr>0)*0xff,(g&self.mg>0)*0xff,(b&self.mb>0)*0xff,(a&self.ma>0)*0xff)
                for r,g,b,a in out.getdata()] )
        else:
            out = image.convert('RGB')
            out.putdata( [((r&self.mr>0)*0xff, (g&self.mg>0)*0xff, (b&self.mb>0)*0xff)
                for r, g, b in out.getdata()] )
        return out

def register():
    return mask()

