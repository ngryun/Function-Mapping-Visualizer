from PIL import Image, ImageGrab
import os
from tkinter import filedialog
from tkinter import messagebox
import config
import win32clipboard

def get_unique_filename(initial_name):
    """
    주어진 이름의 파일이 이미 존재하는 경우, (1), (2), ... 등을 추가하여 고유한 이름을 생성합니다.
    """
    base_name, ext = os.path.splitext(initial_name)
    counter = 1
    new_name = initial_name
    while os.path.exists(new_name):
        new_name = f"{base_name}({counter}){ext}"
        counter += 1
    return new_name

def save_as_image():
    if config.current_fig:
        unique_filename = get_unique_filename("function.png")
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                                                 initialfile=unique_filename)
        if not file_path:  # If the user cancels the file dialog, then return
            return
        config.current_fig.savefig(file_path)
        print(f"Image saved as {file_path}")


def copy_to_clipboard():
    if config.current_fig:
        file_path = "temp_img.png"
        config.current_fig.savefig(file_path)
        image = Image.open(file_path)
        output = Image.new("RGB", image.size, (255, 255, 255))
        output.paste(image, mask=image.split()[3])  # 3 is the alpha channel

        # BMP 형식으로 임시 저장 (클립보드에서 필요)
        output = output.convert("RGB")  # 24-bit per pixel format
        with open("temp.bmp", "wb") as f:
            output.save(f, "BMP")

        # 클립보드에 BMP 이미지 복사
        with open("temp.bmp", "rb") as f:
            # BMP 형식을 DIB 형식으로 변환하기 위한 처리
            dib = f.read()[14:]  # BMP header (14 bytes) 제거
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, dib)
            win32clipboard.CloseClipboard()
        messagebox.showinfo("Notification", "Image has been copied to the clipboard.")

