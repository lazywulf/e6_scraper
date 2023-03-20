import tkinter as tk


class UI:
    def __init__(self):
        self.root = tk.Tk()

    def prepare_window(self):
        r = self.root
        window_width = 800
        window_height = 600
        screen_width = r.winfo_screenwidth()
        screen_height = r.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)

        r.title("e621 scrapper 1.0 - by lazywulf")
        r.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        r.resizable(False, False)
        r.attributes("-topmost", 1)
        r.iconbitmap("/e6_scraper/assets/e621.ico")

    def load_component(self):
        ...

    def run(self):
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        finally:
            self.prepare_window()
            self.root.mainloop()


if __name__ == "__main__":
    window = UI()
    window.run()
