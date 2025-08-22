# Gán phím tắt
bind_keys = {
    'scan-guzheng':  'f3',
    'scan-common':   'f4',  # Nhị hồ, sáo trúc, kèn sô na
    'scan-drum':     'f5',
    'scan-clapper':  'f6',
    'scan-gong':     'f7',

    'loop-guzheng':  'f8',
    'loop-common':   'f9',
    'loop-drum':     'f10',
    'loop-clapper':  'f11',
    'loop-gong':     'f12',

    'end':           'f1'
}

# Chế độ quét:
# Không làm gì khác, chỉ quét màn hình và nhấn phím tương ứng theo kết quả OCR.

# Chế độ lặp:
# Đứng cạnh nhạc cụ, trên màn hình cần hiển thị phím E.
# Khi bật, tự động chọn "Chuyên gia - Thiên tuyển" để chơi.
# Mỗi lần chơi xong một bản sẽ gọi chế độ quét một lần.
# Sau khi chơi hai lần thì thoát, rồi lặp lại quy trình trên.



import yaml
import os

key_delay = {}
tesseract_path = ''

# Vietnamese localization helpers (display only)
vi_type = {
    'guzheng': 'Đàn tranh',
    'common':  'Chung (Nhị hồ, Sáo, Kèn bầu)',  # Nhị hồ, sáo trúc, kèn sô na
    'drum':    'Trống',
    'clapper': 'Mõ',
    'gong':    'Chiêng',
}

vi_mode = {
    'scan': 'Quét',
    'loop': 'Lặp',
}

def vi_func_name(name: str) -> str:
    try:
        parts = name.split('-')
        if len(parts) == 2:
            return f"{vi_mode.get(parts[0], parts[0])} - {vi_type.get(parts[1], parts[1])}"
        return name
    except Exception:
        return name

def load_config_yaml():

    global key_delay
    global tesseract_path
    data = yaml.load(open('config.yaml', encoding='utf-8').read(), Loader=yaml.FullLoader)
    key_delay = data['key_delay']
    tesseract_path = data['tesseract_path']
    assert os.path.exists(tesseract_path)

load_config_yaml()
