x = 538 + 120 - 10  # Vì có dòng tiếp theo nên cần dịch trái một chút
width = 28 + 10     # Vì có số hai chữ số 10~13 nên tăng vùng khớp
height = 23

args_top = (x, 145, width, height, 'top')
args_middle = (x, 240, width, height, 'middle')
args_bottom = (x, 335, width, height, 'bottom')

map_top = {9: 'E', 10: 'R', 11: 'T', 12: 'Y', 13: 'U'}
map_middle = {5: 'D', 6: 'F', 7: 'H', 8: 'J'}
map_bottom = {1: 'C', 2: 'V', 3: 'N', 4: 'M'}