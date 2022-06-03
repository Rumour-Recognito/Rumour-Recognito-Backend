import pytesseract
import cv2
import urllib.request
import numpy as np
from PIL import Image


def analyze_image(source, mode):
    #pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"

    if(mode == 'url'):
        url_response = urllib.request.urlopen(source)
        img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)

        (h, w) = img.shape[:2]
        img = cv2.resize(img, (w*3, h*3))
        gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        text = pytesseract.image_to_string(thr)

    else:
        img = Image.open(source)
        img = np.array(img)

        (h, w) = img.shape[:2]
        img = cv2.resize(img, (w*3, h*3))
        gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thr = cv2.threshold(gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        text = pytesseract.image_to_string(thr)

    return text
