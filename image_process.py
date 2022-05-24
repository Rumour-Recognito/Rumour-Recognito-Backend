import requests
import pytesseract
import cv2


def analyze_image(url):
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    #pytesseract.pytesseract.tesseract_cmd = "/app/.apt/usr/bin/tesseract"

    if(url != ''):
        file_name = "image.jpg"

        res = requests.get(url, stream=True)

        if res.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(requests.get(url).content)
            print('Image sucessfully Downloaded: ', file_name)
        else:
            print('Image Couldn\'t be retrieved')

    img = cv2.imread("image.jpg")
    (h, w) = img.shape[:2]
    img = cv2.resize(img, (w*3, h*3))
    gry = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thr = cv2.threshold(
        gry, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(thr)

    return text


'''
val = analyze_image(
    "https://www.techsmith.com/blog/wp-content/uploads/2020/11/TechSmith-Blog-ExtractText.png")
print(val)

'''
