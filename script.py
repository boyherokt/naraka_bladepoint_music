import time, threading
import param_common
from control import *
import utils
import script
import param
import config

class RunStatus:
    def __init__(self):
        self._is_running = False
    def set_status(self, status):
        print(f'set _is_running: {status}')
        self._is_running = status
    def get_status(self):
        print(f'get _is_running: {self._is_running}')
        return self._is_running


run_status = RunStatus()
task_ctrls = {}
index = 0
lock = threading.Lock()


def start_script(mode, type):
    global index

    if run_status.get_status():
        print('[LỖI] Script không hỗ trợ chạy song song')
        return
    run_status.set_status(True)

    lock.acquire()

    ctrl = Control(param.process_name)
    task_ctrls[index] = ctrl

    disp_mode = config.vi_mode.get(mode, mode)
    disp_type = config.vi_type.get(type, type)
    print(f'[{disp_mode}] Bắt đầu: {disp_type}')

    @utils.new_thread
    def loop_thread_func(index):
        try:
            script.loop_script_body(ctrl, mode, type)
            print(f'[{disp_mode}] Hoàn thành: {disp_type}')
        except OperationInterrupt:
            print(f'[{disp_mode}] Đã dừng: {disp_type}')
            del task_ctrls[index]
        except Exception as e:
            print(e)
            raise

    @utils.new_thread
    def scan_thread_func(index):
        param.type_handles[type]['start'](ctrl)
        del task_ctrls[index]

    if mode == 'loop':
        loop_thread_func(index)
    else:
        scan_thread_func(index)

    index += 1
    lock.release()


def stop_script():
    print('Thử dừng mọi hoạt động biểu diễn')
    for ctrl in task_ctrls.values():
        ctrl.interrupt()
    for type in param.type_handles.keys():
        param.type_handles[type]['stop']()
    up_all_key()
    run_status.set_status(False)


# Tránh kẹt quy trình trong chế độ Vòng lặp - Common khi thoát nhạc cụ do vẫn giữ một số phím.
def up_all_key(ctrl=None):
    if ctrl is None:
        ctrl = Control(param.process_name)
    for key in list(param_common.map_top.values()) + list(param_common.map_middle.values()) + list(param_common.map_bottom.values()):
        ctrl.keyup(key)


def loop_script_body(ctrl, mode, type):
    c = ctrl

    while run_status.get_status():

        # Nhấn giữ phím E để bắt đầu biểu diễn (có thể lỗi, hãy lặp lại vài lần)
        c.keypress('E', 2)
        c.delay(1)
        while not utils.find_music_book():
            c.keypress('E', 2)
            c.delay(1)
        c.delay(3)

        # Biểu diễn vài lần
        times = 2
        for i in range(times):
            # Mở Sổ tay nghệ thuật
            c.moveto(1818, 356)
            c.delay(0.1)
            c.left_click()
            c.delay(1)

            # Lật Sổ tay đến trang cuối
            c.moveto(996, 710)
            c.delay(0.5)
            c.mouse_wheel(-3000)
            c.delay(1)

            # Chọn "Chuyên gia - Thiên tuyển"
            c.moveto(996, 710)
            c.delay(0.1)
            c.left_click()

            # Nhấn "Bắt đầu biểu diễn"
            c.moveto(1689, 943)
            c.delay(0.1)
            c.left_click()

            # Bắt đầu biểu diễn và đợi hoàn thành
            utils.new_thread(param.type_handles[type]['start'])(ctrl)
            # Thời lượng bài nhạc
            c.delay(3 * 60 + 24)
            c.delay(12)
            param.type_handles[type]['stop']()

            # Xác nhận cửa sổ nhận thành thạo, đôi khi sẽ hiện hai lần
            c.keypress(' ')
            c.delay(2)
            c.keypress(' ')
            c.delay(2)

            if type == 'common':
                up_all_key(c)

        # Nhấn Esc để đứng dậy
        c.keypress('\x1b')
        c.delay(3)
        # Xác nhận cửa sổ nhận thành thạo, đôi khi cũng xuất hiện ở đây
        c.keypress(' ')
        c.delay(5)

        # Nhảy nhẹ (để hiển thị phím E trên màn hình)
        c.keypress(' ')
        c.delay(0.5)