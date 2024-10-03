import os
import tkinter as tk
from datetime import datetime
from logging import getLogger

from PIL.ImageGrab import grab


def save_screenshot(widget: tk.Widget,
                    filename: str | None = None,
                    format: str = 'png',
                    ) -> None:
    x0 = widget.winfo_rootx()
    y0 = widget.winfo_rooty()
    x1 = x0 + widget.winfo_width()
    y1 = y0 + widget.winfo_height()
    image = grab((x0, y0, x1, y1), all_screens=True)
    if filename is None:
        filename = datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S.png')
    file_path = f'{SCREENSHOTS_DIRECTORY}/{filename}'
    if not os.path.exists(SCREENSHOTS_DIRECTORY):
        os.mkdir(SCREENSHOTS_DIRECTORY)
    image.save(file_path, format)
    getLogger(__name__).info(f'Saved screenshot to {file_path}')


SCREENSHOTS_DIRECTORY = 'ffx_sphere_grid_viewer_screenshots'
