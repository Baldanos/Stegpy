class diff():

    def __init__(self):
        self.name="Pixel difference view"
        self.description="Generates an image containing the pixel difference of the source image"
        self.inputdata="image"
        self.parameters = None
        self.mode="visual"

    def process(self, image):
        """
        Generates an image containing the pixel difference of the source image
        """
        if image.mode == 'RGBA':
            out = image.copy()
            sx, sy = image.size
            for x in xrange(sx):
                for y in xrange(sy):
                    try:
                        if image.getpixel((x, y)) == image.getpixel((x-1, y)):
                            out.putpixel((x, y), (0, 0, 0, 255))
                        else:
                            out.putpixel((x, y), (255, 255, 255, 255))
                    except:
                        out.putpixel((x, y), (0, 0, 0, 255))
        else:
            out = image.convert('RGB')
            sx, sy = image.size
            for x in xrange(sx):
                for y in xrange(sy):
                    try:
                        if image.getpixel((x, y)) == image.getpixel((x-1, y)):
                            out.putpixel((x, y), (0, 0, 0))
                        else:
                            out.putpixel((x, y), (255, 255, 255))
                    except:
                            out.putpixel((x, y), (0, 0, 0))
        return out


def register():
    return diff()
