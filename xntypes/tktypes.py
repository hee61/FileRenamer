import tkinter as tk
import tkinter.ttk as ttk

__all__ = ["Output"]


class Output(tk.Text):
    def __init__(self, master=None, **kwargs):
        self.frame = ttk.Frame(master)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side="right", fill="y")

        kwargs.update({"yscrollcommand": self.vbar.set})
        tk.Text.__init__(self, self.frame, **kwargs)
        self.pack(side="left", fill="both", expand=True)
        self.vbar["command"] = self.yview

        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != "_" and m not in ("config", "configure"):
                setattr(self, m, getattr(self.frame, m))

        self["bg"] = "#293134"
        self['fg'] = '#E0E2E4'
        self['selectbackground'] = '#2F393C'
        self['selectforeground'] = '#557dac'
        self['font'] = ("Verdana", "10")

    def display(self, *text, end='\n', sep=' '):
        """Functions similar to python's built-in print()"""
        self['state'] = 'normal'
        self.insert('end', sep.join(map(str, text)) + end)
        self['state'] = 'disabled'

    def delete_all(self):
        """Removes all text from the output window"""
        self['state'] = 'normal'
        self.delete('1.0', 'end')
        self['state'] = 'disabled'

    def write(self, *data):
        """Required function to allow an instance
        of this class to be used as stdout/stderr"""
        self.display(*data, end="")


# ****** ButtonFrame Widget ******
class ButtonFrame(ttk.Frame):
    """Ttk Frame widget containing left and right buttons,
    names and commands supplied as dicts of keys and values
    respectively."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.left = dict()
        self.right = dict()

    def make_buttons(self, left: dict, right: dict):
        left_buttons = ttk.Frame(self)
        left_buttons.grid(row=0, column=0, sticky="nsw")

        right_buttons = ttk.Frame(self)
        right_buttons.grid(row=0, column=1, sticky="nse")

        # ****** Left Button Widgets ******
        for i, key in enumerate(left):
            left_buttons.columnconfigure(i, pad=9)
            lb = ttk.Button(
                left_buttons,
                text=key,
                width=11,
                command=left[key])
            lb.grid(row=0, column=i)
            lb.bind("<Return>", lb["command"])
            self.left[key] = lb

        # ****** Right Button Widgets ******
        for i, key in enumerate(right):
            right_buttons.columnconfigure(i, pad=9)
            rb = ttk.Button(
                right_buttons,
                text=key,
                width=11,
                command=right[key])
            rb.grid(row=0, column=len(right)-(len(right)-i))
            rb.bind("<Return>", rb["command"])
            self.right[key] = rb


class PageMaster(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=100)

        self.frames = dict()

    def show_frame(self, cont):
        try:
            frame = self.frames[cont]
            frame.tkraise()
        except KeyError:
            frame = cont(self.container, self)
            self.frames[cont] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    @staticmethod
    def center(win):
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    @staticmethod
    def toggle(win):
        win.attributes("-alpha", float(not win.attributes("-alpha")))
