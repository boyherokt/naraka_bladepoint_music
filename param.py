import musical_guzheng
import musical_common
import musical_drum
import musical_clapper
import musical_gong

# Tên tiến trình
process_name = "NarakaBladepoint.exe"

# Số khung hình tối đa mỗi giây (FPS)
fps = 20

# Hàm xử lý cho từng nhạc cụ trong chế độ quét
type_handles = {
    'guzheng': {'start': musical_guzheng.start, 'stop': musical_guzheng.stop},
    'common':  {'start': musical_common.start, 'stop': musical_common.stop},
    'drum':    {'start': musical_drum.start,  'stop': musical_drum.stop},
    'clapper': {'start': musical_clapper.start,'stop': musical_clapper.stop},
    'gong':    {'start': musical_gong.start,   'stop': musical_gong.stop},
}
