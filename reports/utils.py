import pytesseract
from PIL import Image


def extract_text_from_image(image_path):
    # PIL Image object
    image = Image.open(image_path)
    # Extract text via pytesseract
    text = pytesseract.image_to_string(image)
    return text
