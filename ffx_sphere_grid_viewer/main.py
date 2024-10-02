import logging
import tkinter as tk
from tkinter import messagebox

from .data.layout import (LAYOUT_EXPERT, LAYOUT_ORIGINAL, LAYOUT_STANDARD,
                          Layout)
from .logger import UIHandler, log_exceptions, log_tkinter_error
from .tkspheregrid import (KEY_TO_APPEARANCE_TYPE, KEY_TO_CHAR_NAME,
                           TkSphereGrid)
from .tkstatuslabel import TkStatusLabel


def show_help_window(title: str) -> None:
    characters = '/'.join(c.upper() for c in KEY_TO_CHAR_NAME)
    edit_node = '/'.join(c.upper() for c in KEY_TO_APPEARANCE_TYPE)
    lines = [
        'Move the Sphere Grid by dragging with the Mouse',
        'Zoom with the Mouse Wheel',
        'F1: show this Help Window',
        'F2: highlight all Nodes',
        'F3: turn off all Nodes',
        'F4: reset Zoom',
        'F5: load a custom Sphere Grid (if present)',
        'F6: load the Original Sphere Grid',
        'F7: load the Standard Sphere Grid',
        'F8: load the Expert Sphere Grid',
        'The following hotkeys will act based on Mouse position:',
        f'- {edit_node}: change Node Contents',
        f'- {characters}: highlight a Node or color a Link',
        f'- Shift + {characters}: add or remove Character Ring',
        f'- Ctrl + {characters}: add or remove Character Flag',
        '  (the Character Flag will link to the nearest Ring)',
    ]
    for c, character in KEY_TO_CHAR_NAME.items():
        lines.append(f'{c.upper()} -> {character}')
    messagebox.showinfo(title, '\n'.join(lines))


@log_exceptions()
def main(*,
         title='FFX Sphere Grid viewer',
         size='1280x720',
         layout: Layout | None = None,
         ) -> None:
    root = tk.Tk()
    root.report_callback_exception = log_tkinter_error
    root.protocol('WM_DELETE_WINDOW', root.quit)
    root.title(title)
    root.geometry(size)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    canvas = TkSphereGrid(root)
    canvas.grid(row=0, column=0, sticky='nsew')

    xsb = tk.Scrollbar(root, orient='horizontal', command=canvas.xview)
    xsb.grid(row=1, column=0, sticky='ew')

    ysb = tk.Scrollbar(root, orient='vertical', command=canvas.yview)
    ysb.grid(row=0, column=1, sticky='ns')

    canvas.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
    canvas.bind('<ButtonPress-1>', lambda e: canvas.scan_mark(e.x, e.y))
    canvas.bind('<B1-Motion>', lambda e: canvas.scan_dragto(e.x, e.y, gain=1))
    canvas.bind('<MouseWheel>', canvas.on_scrollwheel)
    for c in KEY_TO_CHAR_NAME:
        root.bind(f'<KeyPress-{c}>', canvas.highlight_nearest)
        root.bind(f'<KeyPress-{c.upper()}>', canvas.add_character_circle)
        root.bind(f'<Control-KeyPress-{c}>', canvas.add_character_flag)
    for c in KEY_TO_APPEARANCE_TYPE:
        root.bind(f'<KeyPress-{c}>', canvas.edit_node)

    buttons = [
        ('<F1>', lambda _=None: show_help_window(f'{title} - Help'), 'Help'),
        ('<F2>', canvas.highlight_all, 'Highlight'),
        ('<F3>', canvas.turn_off_all, 'Off'),
        ('<F4>', lambda: canvas.set_zoom(1.0), 'Reset Zoom'),
    ]
    if layout is None:
        canvas.draw_layout(LAYOUT_ORIGINAL)
    else:
        buttons.append(
            ('<F5>', lambda _=None: canvas.draw_layout(layout), 'Custom'))
        canvas.draw_layout(layout)
    buttons.extend([
        ('<F6>', lambda _=None: canvas.draw_layout(LAYOUT_ORIGINAL), 'Original'),
        ('<F7>', lambda _=None: canvas.draw_layout(LAYOUT_STANDARD), 'Standard'),
        ('<F8>', lambda _=None: canvas.draw_layout(LAYOUT_EXPERT), 'Expert'),
    ])
    frame = tk.Frame(root)
    frame.grid(row=2, column=0, columnspan=2, sticky='nsew')
    for i, (sequence, command, text) in enumerate(buttons):
        root.bind(sequence, command)
        tk.Button(frame, text=text, command=command).grid(row=0, column=i)

    status_label = TkStatusLabel(frame)
    status_label.grid(row=0, column=i + 1, sticky='e')
    frame.columnconfigure(i + 1, weight=1)
    handler = UIHandler(status_label)
    formatter = logging.Formatter(
        fmt='{levelname} - {message}',
        style='{',
        )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    logging.getLogger(__name__.split('.')[0]).addHandler(handler)

    root.mainloop()
