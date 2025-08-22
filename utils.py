import time, threading, os
import pytesseract
import pyautogui
import cv2
import numpy as np
import config


music_ui_image_path = r'images\perfect.jpg'
assert os.path.exists(music_ui_image_path)
music_ui_image = cv2.imread(music_ui_image_path)

music_book_image_path = r'images\music_book.jpg'
assert os.path.exists(music_book_image_path)
music_book_image = cv2.imread(music_book_image_path)


def new_thread(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    return wrapper


def time2str(timestamp):
    return time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime(timestamp)) + f'_{int(timestamp * 1000) % 1000:03d}'


def OCR(image):
    pytesseract.pytesseract.tesseract_cmd = config.tesseract_path
    # --psm 7 nhận dạng một dòng
    # --oem 3 dùng engine LSTM OCR
    # -c tessedit_char_whitelist=0123456789 chỉ nhận dạng ký tự số
    text = pytesseract.image_to_string(image, config='--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789')
    text = text.strip()
    return text


# Tìm kiếm target trong image, trả về danh sách tọa độ (x, y) sắp theo x
def image_search(image, target):
    # Tìm hình
    res = cv2.matchTemplate(image, target, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where(res >= threshold)
    coords = [coord for coord in zip(*loc[::-1])]

    # Loại trùng
    temp = []
    threshold = 10
    for coord in coords:
        exists = False
        for coord2 in temp:
            if abs(coord[0] - coord2[0]) <= threshold and abs(coord[1] - coord2[1]) <= threshold:
                exists = True
        if not exists:
            temp.append(coord)
    coords = sorted(temp, key=lambda pair: pair[0])
    return coords


def is_music_ui(image):
    x1 = 4; y1 = 268; x2 = 102; y2 = 300        #x1=4; y1=268; x2=102; y2=300   #x1 = 17; y1 = 261; x2 = 84; y2 = 305 
    image = image[y1:y2, x1:x2]
    res = image_search(image, music_ui_image)
    return len(res) > 0


def find_music_book():
    screenshot = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    x1 = 1773; y1 = 322; x2 = 1837; y2 = 392
    image = image[y1:y2, x1:x2]
    res = image_search(image, music_book_image)
    return len(res) > 0



if __name__ == '__main__':
    print(time2str(time.time()))