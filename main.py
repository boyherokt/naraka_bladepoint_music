import subprocess
import tkinter as tk
from tkinter import font
import config
import console

def app():
    root = tk.Tk()
    root.title("Naraka: Bladepoint — Cày độ thành thạo nhạc cụ")
    root.iconbitmap("naraka.ico")
    root.geometry("312x440")

    font_bold = font.Font(family="Segoe UI", size=14, weight="bold")
    font_default = font.Font(family="Segoe UI", size=14)

    tk.Label(root, text='Phím tắt', font=font_bold).grid(row=0, column=0)
    tk.Label(root, text='Chức năng', font=font_bold).grid(row=0, column=1)

    index = 1
    for func, key in config.bind_keys.items():
        left = tk.Label(root, text=key, font=font_default)
        left.grid(row=index, column=0, padx=60, pady=1)
        right = tk.Label(root, text=config.vi_func_name(func), font=font_default)
        right.grid(row=index, column=1, padx=10, pady=1)
        index += 1

    def on_button_click():
        subprocess.run(['notepad.exe', 'config.yaml'])
        config.load_config_yaml()
        print('Độ trễ phím:', config.key_delay)

    button = tk.Button(root, text="Cấu hình", command=on_button_click, width=40, height=1, fg="white", bg="blue")
    button.grid(row=index, column=0, padx=10, pady=10, columnspan=2)

    console.bind_hotkey()

    root.mainloop()



if __name__ == '__main__':
    app()
