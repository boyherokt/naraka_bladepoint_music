import cv2, os


def check_output_path(s):
    for c in s:
        if (not (32 <= ord(c) <= 126)) or c == ' ':
            return False
    return True


def vedio2images(vedio_path, output_dir):
    if not check_output_path(output_dir):
        print('Đường dẫn xuất ảnh của thư viện cv2 không nên chứa tiếng Trung hoặc khoảng trắng')
        return 

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    vc = cv2.VideoCapture(vedio_path)
    
    if not vc.isOpened():
        print("Không thể mở tệp video:", video_path)
        return

    fps = vc.get(cv2.CAP_PROP_FPS)
    print(f'{vedio_path} FPS {fps}')

    cnt = 1
    while True:
        ret, frame = vc.read()
        if not ret:
            break
        output_path = os.path.join(output_dir, f'{cnt:08d}.jpg')
        cv2.imwrite(output_path, frame)
        cnt += 1

    vc.release()
    print(f'{vedio_path} tổng cộng {cnt} khung hình')


if __name__ == '__main__':
    vedio_path = r'/videos/guqin-part1.mp4'
    output_dir = r'D:\yjwj_music\images\guqin-part1'
    vedio2images(vedio_path, output_dir)