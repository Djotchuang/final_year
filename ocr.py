from PIL import Image
import pytesseract as tess
tess.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'


def get_text(image_file):
    image = Image.open(image_file)
    text = tess.image_to_string(image)
    # print(text)
    return text
