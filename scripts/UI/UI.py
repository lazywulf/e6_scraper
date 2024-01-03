import tkinter as tk
import xml.etree.cElementTree as et
ㄠ

class UI:
    def __init__(self, controller, width, height, path):
        self.root = tk.Tk()
        self.ctrl = controller
        self.width = width
        self.height = height
        self.d_sheet = path

    def prepare_window(self):
        r = self.root
        screen_width = r.winfo_screenwidth()
        screen_height = r.winfo_screenheight()
        center_x = int(screen_width/2 - self.width / 2)
        center_y = int(screen_height/2 - self.height / 2)

        r.title("e621 scrapper 1.0 - by lazywulf")
        r.geometry(f'{self.width}x{self.height}+{center_x}+{center_y}')
        r.resizable(False, False)
        r.attributes("-topmost", 1)
        r.iconbitmap("/e6_scrapper/assets/e621.ico")

    def load_component(self):
        def to_dict(tree):
            tags = {}
            for x in tree:
                if x.tag != "place":
                    tags[x.tag] = x.text
            place = {x.tag: x.text for x in tree.find("place")}
            return tags, place

        root = et.parse(self.d_sheet).getroot().find("Canvas")
        config = to_dict(root.find("config"))
        canvas = tk.Canvas(self.root, **config[0])
        canvas.place(**config[1])

        for child in root.find("component"):
            comp =


    def run(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        finally:
            self.prepare_window()
            self.load_component()
            self.root.mainloop()


if __name__ == "__main__":
    window = UI("w", 600, 720, "design/main.xml")
    window.run()
