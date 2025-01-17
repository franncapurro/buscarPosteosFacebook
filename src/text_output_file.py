class TextOutputFile(object):
    def __init__(self, content=""):
        self.content = content

    def append(self, content):
        self.content = content

    def save(self, filename):
        with open(filename, "w", encoding="UTF-8") as outfile:
            outfile.write(self.content)
