class original():

    def __init__(self):
        self.name="Original"
        self.description="Displays the original image"
        self.inputdata="image"
        self.parameters = None
        self.mode="visual"


    def process(self, image):
        return image

def register():
    return original()
