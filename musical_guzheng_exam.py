import os, time, shutil, hashlib, threading, queue
import cv2
import numpy as np
import pyautogui
import config
import utils
import control
import script
import param
import param_common


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

    # Cắt vùng cụ thể
    image = image[y:y+height, x:x+width]
    image_ori = image

    # Đảo ngược màu
    image = 255 - image

    # Chuyển ảnh thành thang xám
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Đặt ngưỡng để chuyển ảnh xám thành ảnh đen trắng
    _, image = cv2.threshold(image, 75, 255, cv2.THRESH_BINARY)

    # Tính tỷ lệ điểm ảnh màu trắng
    region = image
    white_count = np.count_nonzero(region == 255)
    total_pixels = height * width
    white_ratio = white_count / total_pixels
    #print(f'type: {type}\twhite_ratio: {white_ratio}')

    text = ''
    # OCR khá chậm, dùng điều kiện này để bỏ qua phần lớn khung hình không hợp lệ
    if 0.5 < white_ratio < 0.95:
        text = utils.OCR(image)

        # if debug and temp_dir != '':
        #     temp = text
        #     if text == '':
        #         temp = 'null'
        #     cv2.imwrite(os.path.join(temp_dir, f'{frame_index}_{time_str}_{type}_{temp}.jpg'), image)
        #     #cv2.imwrite(os.path.join(temp_dir, f'{frame_index}_{time_str}_{type}_{temp}_ori.jpg'), image_ori)

    # Tính hash của ảnh để xác định vùng mục tiêu không thay đổi/lặp khung
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
            print('[CẢNH BÁO] Không đạt FPS yêu cầu, có thể gây trễ nhận phím')


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
        res_top = crop_and_ocr(image, param_common.args_top, time_str, frame_index)
        res_middle = crop_and_ocr(image, param_common.args_middle, time_str, frame_index)
        res_bottom = crop_and_ocr(image, param_common.args_bottom, time_str, frame_index)
        result_queue.put((frame_index, timestamp, res_top, res_middle, res_bottom))


def keypress_thread_func(ctrl):
    global result_list
    ack_index = -1
    last_index = 0
    last_press_index = 0
    last_key = ''
    last_hash_top = ''
    last_hash_middle = ''
    last_hash_bottom = ''

    while is_running:
        try:
            result = result_queue.get(timeout=queue_get_timeout)
        except queue.Empty:
            continue
        frame_index, timestamp, res_top, res_middle, res_bottom = result

        non_null = 0
        for res in result[2:]:  # res: (text, hash)
            if res[0] != '':
                non_null += 1
        if non_null == 0:
            continue
        if non_null != 1:
            print(f'[CẢNH BÁO] Nhiều dòng cùng có giá trị: {result}')
            continue

        num_top, hash_top = res_top
        num_middle, hash_middle = res_middle
        num_bottom, hash_bottom = res_bottom

        num = 0
        skip = False

        if num_top != '':
            if int(num_top) not in param_common.map_top.keys():
                print(f'[CẢNH BÁO] map_top không có phím tương ứng: {num_top}')
                continue
            key = param_common.map_top[int(num_top)]
            num = num_top
            if last_hash_top == hash_top:
                last_index = frame_index
                skip = True
            last_hash_top = hash_top
        elif num_middle != '':
            if int(num_middle) not in param_common.map_middle.keys():
                print(f'[CẢNH BÁO] map_middle không có phím tương ứng: {num_middle}')
                continue
            key = param_common.map_middle[int(num_middle)]
            num = num_middle
            if last_hash_middle == hash_middle:
                last_index = frame_index
                skip = True
            last_hash_middle = hash_middle
        else:
            if int(num_bottom) not in param_common.map_bottom.keys():
                print(f'[CẢNH BÁO] map_bottom không có phím tương ứng: {num_bottom}')
                continue
            key = param_common.map_bottom[int(num_bottom)]
            num = num_bottom
            if last_hash_bottom == hash_bottom:
                last_index = frame_index
                skip = True
            last_hash_bottom = hash_bottom

        if skip:
            continue

        # Do nhận dạng đa luồng, nếu phím hiện tại nằm trước phím mới nhất đã xác nhận thì bỏ qua
        if frame_index <= ack_index:
            continue

        # Không nhấn phím ở hai khung liền kề, vì khung thứ hai có thể nhận sai do số bị kẹt ở biên
        # Ví dụ cùng một phím: khung 1 nhận 3 đúng, khung 2 do 3 bị che một nửa nên nhận thành 1
        # Nếu đều phản hồi sẽ tiêu hao cơ hội nhấn đúng tiếp theo, gây vòng lặp xấu
        if frame_index <= last_press_index + 1:
            continue

        # Hai khung liền kề có thể thuộc cùng một lần nhấn (ví dụ nằm hai bên vùng cắt)
        if key != last_key or frame_index > last_index + 2:
            @utils.new_thread
            def custom_keypress(key, delay1, delay2):
                try:
                    ctrl.delay(delay1)
                    ctrl.keypress(key, delay2)
                except control.OperationInterrupt:
                    stop()
            custom_keypress(key, config.key_delay['common'], 0.01)
            print(f'{frame_index:08d}\t{utils.time2str(timestamp)}\t\t{key}\t{num}')

            ack_index = frame_index
            last_index = frame_index
            last_press_index = frame_index
            last_key = key


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

    # Chặn (join) luồng chính
    screenshot_thread.join()
    for recognize_thread in recognize_threads:
        recognize_thread.join()
    keypress_thread.join()

    is_running = False


def stop():
    global is_running
    if is_running:
        print('Dừng quét biểu diễn [Cổ tranh] (Chế độ thi)')
    is_running = False


if __name__ == '__main__':
    ctrl = control.Control(param.process_name)
    start(ctrl)
