import cv2
import numpy as np
import base64
from captcha_preprocess.split_captcha.split_captcha import split_icons, create_icons


def readb64(encoded_data):
    nparr = np.frombuffer(encoded_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return img


def b64_decode(im_b64: str):
    img_bytes = base64.b64decode(im_b64.encode("utf-8"))
    img = readb64(img_bytes)
    img_arr = np.asarray(img)
    img_bgr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)
    return img_bgr


def sobel_filter(threshold, img):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Применение фильтра Собеля для вычисления градиента по оси X и Y
    sobelx = cv2.Sobel(gray_img, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray_img, cv2.CV_32F, 0, 1, ksize=3)
    # Вычисление магнитуды градиента
    mag = np.sqrt(sobelx ** 2 + sobely ** 2)
    # Аналог паддинга нулями
    mag[0, :] = mag[-1, :] = mag[:, 0] = mag[:, -1] = 0
    # Применение порога
    _, mag_thresh = cv2.threshold(mag, threshold, 255, cv2.THRESH_TOZERO)
    # Преобразование магнитуды градиента в 8-битное изображение
    # Используем нормализацию для преобразования в диапазон 0-255
    processed_image = cv2.cvtColor(mag_thresh.astype(np.uint8), cv2.COLOR_GRAY2BGR)
    return processed_image


def preprocess_captcha_sobel(icons):
    icons_d = split_icons(icons)
    ans = create_icons(image=icons, icons=icons_d)

    return ans
