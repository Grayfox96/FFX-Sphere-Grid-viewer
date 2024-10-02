import tkinter as tk


class TkStatusLabel(tk.Label):
    def __init__(self, parent: tk.Widget, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)
        self.update('OK')

    def update(self, msg: str) -> None:
        text = f'Status: {msg}'
        self.configure(text=text)
