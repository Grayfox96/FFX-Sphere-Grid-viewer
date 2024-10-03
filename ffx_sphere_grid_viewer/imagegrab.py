import tkcap
import datetime
from logging import getLogger
import tkinter as tk
from PIL import Image


def _filename() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.png")


def grab(widget: tk.Widget, xsb, ysb, frame, *args, **kwargs) -> None:
    # Take a screenshot of the bounding box
    cap = tkcap.CAP(widget)

    # Get the logger
    logger = getLogger(__name__)

    # Save the screenshot
    filename = _filename()
    cap.capture(filename)
    logger.info(f"Screenshot saved as {filename}")

    # Load the image
    image = Image.open(filename)

    # Crop the image to remove scrollbars and window edges
    # Adjust these values based on the size of your scrollbars and window edges
    left = 5  # Adjust as needed
    top = 45  # Adjust as needed
    right = ysb.winfo_width()  # Adjust as needed
    bottom = xsb.winfo_height() + frame.winfo_height()  # Adjust as needed

    logger.info(f"Cropping image to {(left, top, right, bottom)}")
    cropped_image = image.crop(
        (left, top, image.width - right, image.height - bottom)
    )

    # Save the cropped screenshot
    cropped_filename = f"cropped_{filename}"
    cropped_image.save(cropped_filename, "PNG")

    # Log the action
    logger.info(f"Saved final screenshot to {filename}")
