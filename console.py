import time
from functools import partial
import keyboard
import script
import config
import param
import utils


def bind_hotkey():
    @utils.new_thread
    def func():
        for mode in ['loop', 'scan']:
            for type in param.type_handles.keys():
                keyboard.add_hotkey(config.bind_keys[f'{mode}-{type}'], partial(script.start_script, mode, type))
        keyboard.add_hotkey(config.bind_keys['end'], script.stop_script)
        keyboard.wait()
    func()


if __name__ == '__main__':
    print('Chào mừng sử dụng script cày độ thành thạo nhạc cụ cho Naraka: Bladepoint\n')
    print('Phím tắt\t\tChức năng')
    for k, v in config.bind_keys.items():
        print(f'{v}\t\t{config.vi_func_name(k)}')
    print()

    bind_hotkey()

    while True:
        time.sleep(3600)