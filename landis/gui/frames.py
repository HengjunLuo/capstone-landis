import tkinter as tk


class CollapsableFrame(tk.Frame):

    def __init__(self, parent, text="", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.text = text
        self.show = False

        # Frames
        self.title_frame = tk.Frame(self)
        self.sub_frame = tk.Frame(self)

        self.title_frame.rowconfigure(0, minsize=35)
        self.title_frame.columnconfigure(0, minsize=335)

        self.title_frame.grid(sticky='e')

        self.lbl_title = tk.Label(self.title_frame, text="Show "+self.text, font=("Helvetica", 9, "italic"), pady=5, padx=15)
        self.lbl_title.grid(sticky='se')

        self.lbl_title.bind('<Enter>', self.highlight)
        self.lbl_title.bind('<Leave>', self.unhighlight)
        self.lbl_title.bind('<Button-1>', self.toggle)

    def toggle(self, _):
        self.show = not self.show
        if self.show:
            self.sub_frame.grid(row=1, column=0, sticky='nsew')
            self.lbl_title.configure(text="Hide "+self.text)
        else:
            self.sub_frame.grid_forget()
            self.lbl_title.configure(text="Show "+self.text)

    def highlight(self, _):
        self.lbl_title.config(font=("Helvetica", 9, "italic underline"))

    def unhighlight(self, _):
        self.lbl_title.config(font=("Helvetica", 9, "italic"))