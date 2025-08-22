import os, time, shutil, hashlib, threading, queue
import cv2
import numpy as np
import pyautogui
import config
import utils
import control
import script
import param
import param_drum


debug = False
temp_dir = r'D:\temp'
if debug:
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

images_queue = queue.Queue()
result_queue = queue.Queue()
is_running = False
queue_get_timeout = 1


# Cắt ảnh và OCR
def crop_and_ocr(image, args, time_str, frame_index):
    x, y, width, height, type = args

    # Cắt vùng mục tiêu
    image = image[y:y+height, x:x+width]
    image_ori = image

    # Đảo màu
    image = 255 - image

    # Chuyển ảnh sang thang xám
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Ngưỡng hóa ảnh xám thành đen trắng
    _, image = cv2.threshold(image, 75, 255, cv2.THRESH_BINARY)

    # Tính tỷ lệ pixel trắng
    region = image
    white_count = np.count_nonzero(region == 255)
    total_pixels = height * width
    white_ratio = white_count / total_pixels
    #print(f'index: {frame_index}\ttype: {type}\twhite_ratio: {white_ratio}')

    text = ''

    if 0.2 < white_ratio < 0.8:
        text = '*'

        # if debug and temp_dir != '':
        #     print(f'index: {frame_index}\ttype: {type}\twhite_ratio: {white_ratio}')
        #     cv2.imwrite(os.path.join(temp_dir, f'{frame_index}_{time_str}_{type}.jpg'), image)
        #     cv2.imwrite(os.path.join(temp_dir, f'{frame_index}_{time_str}_{type}_ori.jpg'), image_ori)

    # Tính hash ảnh để phát hiện vùng mục tiêu không đổi/chèn khung lặp
    image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
    image_hash = hashlib.md5(image_bytes).hexdigest()

    return (text, image_hash)


def screenshot_thread_func():
    frame_interval = 1.0 / param.fps
    frame_index = 0

    while is_running:
        begin = time.time()
        screenshot = pyautogui.screenshot()
        image = screenshot#cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        images_queue.put((frame_index, begin, image))
        frame_index += 1
        end = time.time()
        if (end - begin) < frame_interval:
            time.sleep(frame_interval - (end - begin))
        else:
            pass


def recognize_thread_func():
    global images_list

    while is_running:
        try:
            frame_index, timestamp, image = images_queue.get(timeout=queue_get_timeout)
        except queue.Empty:
            continue
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        if not utils.is_music_ui(image):
            continue
        time_str = utils.time2str(timestamp)
        res_line1 = crop_and_ocr(image, param_drum.args_line1, time_str, frame_index)
        res_line2 = crop_and_ocr(image, param_drum.args_line2, time_str, frame_index)
        res_line3 = crop_and_ocr(image, param_drum.args_line3, time_str, frame_index)
        res_line4 = crop_and_ocr(image, param_drum.args_line4, time_str, frame_index)
        result_queue.put((frame_index, timestamp, res_line1, res_line2, res_line3, res_line4))


def keypress_thread_func(ctrl):
    global result_list
    ack_index = -1
    last_index = 0
    last_press_index = 0
    last_hash_line1 = ''
    last_hash_line2 = ''
    last_hash_line3 = ''
    last_hash_line4 = ''

    while is_running:
        try:
            result = result_queue.get(timeout=queue_get_timeout)
        except queue.Empty:
            continue
        frame_index, timestamp, res_line1, res_line2, res_line3, res_line4 = result

        non_null = 0
        for res in result[2:]:  # res: (text, hash)
            if res[0] != '':
                non_null += 1
        if non_null == 0:
            continue
        if non_null != 1:
            #print(f'[CẢNH BÁO] Nhiều dòng cùng có giá trị: {result}')
            continue

        text_line1, hash_line1 = res_line1
        text_line2, hash_line2 = res_line2
        text_line3, hash_line3 = res_line3
        text_line4, hash_line4 = res_line4
        skip = False

        if text_line1 == '*':
            key = param_drum.key_line1
            if last_hash_line1 == hash_line1:
                last_index = frame_index
                skip = True
            last_hash_line1 = hash_line1
        elif text_line2 == '*':
            key = param_drum.key_line2
            if last_hash_line2 == hash_line2:
                last_index = frame_index
                skip = True
            last_hash_line2 = hash_line2
        elif text_line3 == '*':
            key = param_drum.key_line3
            if last_hash_line3 == hash_line3:
                last_index = frame_index
                skip = True
            last_hash_line3 = hash_line3
        else:
            key = param_drum.key_line4
            if last_hash_line4 == hash_line4:
                last_index = frame_index
                skip = True
            last_hash_line4 = hash_line4

        if skip:
            continue

        # Do nhận dạng đa luồng, nếu phím hiện tại nằm trước phím mới nhất đã xác nhận thì bỏ qua
        if frame_index <= ack_index:
            continue

        # Không nên nhấn phím ở cả hai khung liên tiếp, vì số ở khung thứ hai có thể bị kẹt biên gây nhận sai
        # Ví dụ cùng một phím: khung 1 nhận đúng là 3, khung 2 do bị cắt một nửa nên nhận thành 1
        # Nếu đều phản hồi sẽ tiêu hao cơ hội lần sau và tạo vòng lặp xấu
        if frame_index <= last_press_index + 1:
            continue

        # Hai khung liên tiếp có thể là cùng một lần nhấn (ví dụ nằm bên trái/phải vùng cắt)
        if frame_index > last_index + 1:
            @utils.new_thread
            def custom_keypress(key, delay1, delay2):
                try:
                    ctrl.delay(delay1)
                    ctrl.keypress(key, delay2)
                except control.OperationInterrupt:
                    stop()
            custom_keypress(key, config.key_delay['drum'], 0.01)
            print(f'{frame_index:08d}\t{utils.time2str(timestamp)}\t\t{key}')

            ack_index = frame_index
            last_index = frame_index
            last_press_index = frame_index


def start(ctrl):
    global is_running
    if is_running:
        print('[LỖI] Script không hỗ trợ chạy song song')
        return
    is_running = True

    # Luồng chụp màn hình
    screenshot_thread = threading.Thread(target=screenshot_thread_func)
    screenshot_thread.daemon = True
    screenshot_thread.start()

    # Luồng nhận dạng
    recognize_threads = []
    for i in range(8):
        recognize_thread = threading.Thread(target=recognize_thread_func)
        recognize_thread.daemon = True
        recognize_threads.append(recognize_thread)
        recognize_thread.start()

    # Luồng nhấn phím
    keypress_thread = threading.Thread(target=keypress_thread_func, args=(ctrl,))
    keypress_thread.daemon = True
    keypress_thread.start()

    # Chặn luồng chính
    screenshot_thread.join()
    for recognize_thread in recognize_threads:
        recognize_thread.join()
    keypress_thread.join()

    is_running = False


def stop():
    global is_running
    if is_running:
        print('Dừng quét biểu diễn [Trống]')
    is_running = False


if __name__ == '__main__':
    ctrl = control.Control(param.process_name)
    start(ctrl)
