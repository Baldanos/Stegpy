class switch():

    def __init__(self):
        self.name="Palette switch view"
        self.description="Replaces a palette with different values to view palette switches"
        self.inputdata="image"
        self.parameters = None
        self.mode="visual"

    def process(self, image):
        """
        Replaces a palette with different values to view palette switches
        """
        if image.mode == 'P':
            palette = []
            for r in xrange(0, 255, 32):
                for g in xrange(0, 255, 32):
                    for b in xrange(0, 255, 32):
                        palette.append(r)
                        palette.append(g)
                        palette.append(b)

            out = image.copy()
            out.putpalette(palette[:768])
            return out
        return image

def register():
    return switch()
