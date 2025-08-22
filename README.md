# naraka_bladepoint_music

Naraka: Bladepoint — Tự động cày độ thành thạo nhạc cụ, có thể vượt qua bài kiểm tra

Nguyên lý: Nhận dạng hình ảnh và mô phỏng bàn phím/chuột

## Lưu ý

1. Phải chạy chương trình với quyền **Quản trị viên (Administrator)**.
2. Không được mở nhiều phiên bản cùng lúc.
3. Do ảnh hưởng của FPS và các yếu tố khác, **bắt buộc** điều chỉnh `key_delay` trong `config.yaml` theo tình trạng thực tế trên máy bạn. (Có thể bấm nút cấu hình để mở `config.yaml`).
4. Trong game, F1/F3/F6 đã được gán sẵn chức năng, nên khi dùng các tính năng tương ứng của chương trình, có thể cần nhấn phím đó **hai lần**. Ví dụ nhấn F6 sẽ kích hoạt “Quét - Phách gỗ”, đồng thời mở chế độ chụp ảnh trong game; hãy nhấn F6 lần nữa để tắt chế độ chụp ảnh.
5. Nếu có thể, ưu tiên chạy `python3 console.py` thay vì bản có UI. Bản UI có thể làm tăng độ trễ phím. Bản console cũng dễ quan sát lỗi (ví dụ F1 có dừng script thành công không).

## Phím tắt

| Chức năng     | Phím | Ghi chú                    |
| ------------- | ---- | -------------------------- |
| Quét - Cổ tranh | F3   |                            |
| Quét - Chung    | F4   | Nhị hồ, sáo trúc, kèn sô na |
| Quét - Trống    | F5   |                            |
| Quét - Phách gỗ | F6   |                            |
| Quét - Cồng     | F7   |                            |
| Lặp - Cổ tranh  | F8   |                            |
| Lặp - Chung     | F9   | Nhị hồ, sáo trúc, kèn sô na |
| Lặp - Trống     | F10  |                            |
| Lặp - Phách gỗ  | F11  |                            |
| Lặp - Cồng      | F12  |                            |
| Kết thúc        | F1   |                            |

 ## Chế độ

### Quét

Không thao tác gì khác; chỉ quét màn hình, dựa trên kết quả OCR để nhấn phím tương ứng.

Chế độ này dùng để làm bài kiểm tra.

### Lặp

Đứng cạnh nhạc cụ, màn hình phải hiển thị phím E.

Khi bật, chương trình sẽ tự chọn “Chuyên gia - Thiên tuyển” để biểu diễn. Mỗi bản nhạc sẽ gọi chế độ Quét một lần. Sau khi chơi 2 bản, thoát ra rồi lặp lại quy trình trên.

Phù hợp để cày độ thành thạo nhạc cụ.

## Khác

1. Nếu nhấn F1 mà chưa dừng, hãy nhấn thêm vài lần.
2. Nếu chương trình vẫn chạy không đúng, hãy thử khởi động lại.
3. Dự án ban đầu để tự dùng nên có thể còn lỗi nhỏ; mình không ưu tiên sửa thêm (dùng console là đủ, vốn dĩ không định viết UI).