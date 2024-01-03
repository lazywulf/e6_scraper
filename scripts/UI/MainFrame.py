from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import xml.etree.cElementTree as et

from scripts.UI.UI import UI


class MainFrame(UI):
    def __init__(self, width, height, path):
        super().__init__(width, height, path)
        self.state = "main"

    def load_component(self):
        def _load_component(state):
            target = ...



        xml = et.parse(self.d_sheet).getroot().findall("Canvas")

    def toggle_expand(self):
        self.state = "expand" if self.state == "main" else "main"
        self.load_component()



