from PIL import Image # ImageGrab is no longer needed
import os
from tkinter import filedialog
from tkinter import messagebox
import config
# import win32clipboard # Removed

# Attempt to import pyperclip and handle if not found
try:
    import pyperclip
except ImportError:
    pyperclip = None # Flag to indicate pyperclip is not available

def get_unique_filename(initial_name):
    """
    Generates a unique filename by appending (1), (2), etc., if the given name already exists.
    """
    base_name, ext = os.path.splitext(initial_name)
    counter = 1
    new_name = initial_name
    while os.path.exists(new_name):
        new_name = f"{base_name}({counter}){ext}"
        counter += 1
    return new_name

def save_as_image():
    """Saves the current Matplotlib figure to a user-specified image file."""
    if config.current_fig:
        unique_filename = get_unique_filename("function.png")
        file_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                                                 initialfile=unique_filename)
        if not file_path:  # If the user cancels the file dialog, then return
            return
        try:
            config.current_fig.savefig(file_path)
            # print(f"Image saved as {file_path}") # Optional: keep for logging if run from console
            messagebox.showinfo("저장 완료", f"이미지가 다음 경로에 저장되었습니다:\n{file_path}")
        except Exception as e:
            messagebox.showerror("저장 실패", f"이미지를 저장하는 중 오류가 발생했습니다:\n{e}")


def copy_to_clipboard():
    """
    Saves the current Matplotlib figure as a temporary image file ('temp_img.png')
    and copies the absolute path of this file to the clipboard using pyperclip.
    Notifies the user of the outcome via message boxes.
    """
    if not pyperclip:
        messagebox.showerror("오류: pyperclip 라이브러리 없음", 
                             "pyperclip 라이브러리가 필요합니다. 'pip install pyperclip' 명령어로 설치해주세요.")
        return

    if config.current_fig:
        temp_file_name = "temp_img.png"
        try:
            # Save the figure to a temporary file
            config.current_fig.savefig(temp_file_name)
            
            # Get the absolute path of the saved image
            img_path = os.path.abspath(temp_file_name)
            
            # Copy the image path to the clipboard
            pyperclip.copy(img_path)
            
            messagebox.showinfo("클립보드에 복사됨", 
                                f"이미지 파일의 경로가 클립보드에 복사되었습니다:\n{img_path}")
        except Exception as e:
            messagebox.showerror("복사 실패", f"이미지 경로를 클립보드에 복사하는 중 오류가 발생했습니다:\n{e}")
        # No need to explicitly delete temp_img.png, it will be overwritten or can be managed by user/OS.
    else:
        messagebox.showwarning("경고: 그림 없음", "클립보드에 복사할 그림이 없습니다.")
