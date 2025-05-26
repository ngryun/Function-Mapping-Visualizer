import tkinter as tk
from tkinter import ttk 
from tkinter import Entry, Label, Button, filedialog
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, ArrowStyle  # 여기서 ArrowStyle을 추가로 import 합니다.
import matplotlib.patches as patches
import numpy as np
from graphics import draw_ellipse, draw_arrow, get_y_values
from utils import save_as_image, copy_to_clipboard
import config

def reverse_arrows_direction():
    if not config.current_fig:
        return

    ax = config.current_fig.gca()
    max_elements = max(len(domain_entry.get().split(',')), len(codomain_entry.get().split(',')))
    a = (max_elements+1)/2
    b = a / 2
    start_point = (0 + 0.5*b, a)
    end_point = (3*b- 0.5*b, a)
    
    # 화살표의 중간 위치 계산
    mid_point = ((start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2)
    # special_arrow가 라벨인 화살표의 arrowstyle 확인
    special_arrow_style = None
    for patch in ax.patches:
        if isinstance(patch, patches.FancyArrowPatch) and patch.get_label() == "special_arrow":
            if isinstance(patch.get_arrowstyle(), patches.ArrowStyle.CurveFilledB):
                special_arrow_style = '<|-'
                remove_functionName()
                ax.text(mid_point[0], mid_point[1] + 0.07*b, r'$f^{-1}$', ha='center', va='bottom', fontsize=30, color='black')
            else:
                special_arrow_style = '-|>'
                remove_functionName()
                ax.text(mid_point[0], mid_point[1] + 0.07*b, r'$f$', ha='center', va='bottom', fontsize=30, color='black')

    # special_arrow 라벨이 붙은 화살표가 없으면 첫 번째 화살표를 기준으로 스타일을 설정합니다.
    if not special_arrow_style and len(ax.patches) > 0:
        first_arrow = ax.patches[0]
        if isinstance(first_arrow.get_arrowstyle(), patches.ArrowStyle.CurveFilledB):
            special_arrow_style = '<|-'
        else:
            special_arrow_style = '-|>'

    # special_arrow의 스타일에 따라 모든 화살표의 스타일 변경
    if special_arrow_style:
        for patch in ax.patches[:]:  # 리스트의 복사본을 사용하여 수정 중 오류를 방지합니다.
            if isinstance(patch, patches.FancyArrowPatch):
                patch.set_arrowstyle(special_arrow_style)

    config.current_fig.canvas.draw_idle()  # 변경 사항을 반영하여 다시 그립니다.



def remove_arrows():
    if not config.current_fig:
        return

    ax = config.current_fig.gca()

    # FancyArrowPatch를 순회하면서 라벨이 "special_arrow"가 아닌 화살표만 삭제
    for patch in ax.patches[:]:
        if isinstance(patch, patches.FancyArrowPatch) and patch.get_label() != "special_arrow":
            patch.remove()

    config.current_fig.canvas.draw_idle()


def toggle_arrow():
    if show_arrow_var.get():
        draw_with_arrow()
    else:
        remove_special_arrow()
        remove_functionName()
        refresh_canvas()

def remove_special_arrow():
    if not config.current_fig:
        return
    
    ax = config.current_fig.gca()
    max_elements = max(len(domain_entry.get().split(',')), len(codomain_entry.get().split(',')))
    a = (max_elements+1)/2
    b = a / 2

    # 현재의 모든 주석과 텍스트를 검색하여 특정 화살표와 LaTeX 문자 f를 제거합니다.
    for artist in list(ax.texts):  # We use list() to ensure that we're iterating over a copy
        if isinstance(artist, plt.Annotation) and artist.get_position() == (0  + 0.5*b , a):
            artist.remove()
        elif isinstance(artist, plt.Text) and artist.get_text() == r'$f$' and artist.get_position() == ((0 + 3*b) / 2, a + 0.07*b):
            artist.remove()
    for patch in list(ax.patches):  # We iterate over a copy of ax.patches
        if hasattr(patch, 'get_label') and patch.get_label() == "special_arrow":
            patch.remove()

    config.current_fig.canvas.draw_idle()  # Redraw the figure
def remove_functionName():
    if not config.current_fig:
        return
    
    ax = config.current_fig.gca()
    max_elements = max(len(domain_entry.get().split(',')), len(codomain_entry.get().split(',')))
    a = (max_elements+1)/2
    b = a / 2

    # 현재의 모든 주석과 텍스트를 검색하여 특정 화살표와 LaTeX 문자 f를 제거합니다.
    for artist in list(ax.texts):  # We use list() to ensure that we're iterating over a copy
        #if isinstance(artist, plt.Text) and artist.get_text() == r'$f$' and artist.get_position() == ((0 + 3*b) / 2, a + 0.07*b):
        if isinstance(artist, plt.Text) and artist.get_position() == ((0 + 3*b) / 2, a + 0.07*b):
            artist.remove()

    config.current_fig.canvas.draw_idle()  # Redraw the figure


def refresh_canvas():
    canvas = FigureCanvasTkAgg(config.current_fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=10, pady=10)
    canvas.draw()


def draw_with_arrow():
    if not config.current_fig:  # current_fig가 None인 경우에만 draw_only_ellipse() 호출
        draw_only_ellipse()
    
    ax = config.current_fig.gca()
    max_elements = max(len(domain_entry.get().split(',')), len(codomain_entry.get().split(',')))
    a = (max_elements+1)/2
    b = a / 2

    # 화살표 시작점과 끝점
    start_point = (0 + 0.5*b, a)
    end_point = (3*b- 0.5*b, a)
    
    # 화살표의 중간 위치 계산
    mid_point = ((start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2)
    #ax.annotate("", xy=end_point, xytext=start_point, arrowprops=dict(arrowstyle="->", color='black', lw=1.5))
    arrow = FancyArrowPatch(start_point, end_point, mutation_scale=15, arrowstyle='-|>', color="black", label="special_arrow")
    
    ax.add_patch(arrow)
    # 중간 위치에 텍스트 추가
    ax.text(mid_point[0], mid_point[1] + 0.07*b, r'$f$', ha='center', va='bottom', fontsize=30, color='black')
    
    canvas = FigureCanvasTkAgg(config.current_fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=10, pady=10)
    canvas.draw()

    
def open_link(event):
    webbrowser.open_new("https://namgungyeon.tistory.com/")

def draw_only_ellipse():
    domain_elements = domain_entry.get().split(',')
    codomain_elements = codomain_entry.get().split(',')

    config.current_fig = draw_ellipse(domain_elements, codomain_elements)
    for widget in right_frame.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(config.current_fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=10, pady=10)
    
    if show_arrow_var.get():  # 체크박스가 체크되어 있다면
        draw_with_arrow()

    canvas.draw()

def draw_arrows():
    if not config.current_fig:
        return
    ax = config.current_fig.gca()
    domain_elements = domain_entry.get().split(',')
    codomain_elements = codomain_entry.get().split(',')
    relation = relation_entry.get().split(';')
    
    max_elements = max(len(domain_elements), len(codomain_elements))
    a = (max_elements + 1) / 2
    b = a / 2

    draw_arrow(ax, domain_elements, codomain_elements, relation, 0, 3 * b)

    canvas = FigureCanvasTkAgg(config.current_fig, master=right_frame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=10, pady=10)
    canvas.draw()

def draw_arrows_and_clear_entry(event=None):
    draw_arrows()
    relation_entry.delete(0, tk.END)
    root.after(100, lambda: relation_entry.focus_set()) 

def on_value_finalized(event):
    draw_only_ellipse()


def initialize_gui():
  
    global show_arrow_var
    global root, domain_entry, codomain_entry, relation_entry, right_frame
    
    root = tk.Tk()  # 여기서 root 를 전역 변수로 만듭니다.
    root.title("Function Relation Illustrator")
    show_arrow_var = tk.IntVar()
    show_arrow_var.set(1)
    
    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    bottom_frame = tk.Frame(root)  # 이 프레임은 두 레이블을 포함합니다.
    bottom_frame.pack(side=tk.BOTTOM, pady=5)

    # 정의역 입력칸
    Label(left_frame, text="Enter domain elements (e.g. a,b,c):").grid(row=0, column=0, pady=5)
    domain_entry = Entry(left_frame)
    domain_entry.grid(row=1, column=0, pady=5)
    domain_entry.bind("<Return>", on_value_finalized)
    domain_entry.bind("<FocusOut>", on_value_finalized)

    # 공역 입력칸
    Label(left_frame, text="Enter codomain elements (e.g. x,y,z):").grid(row=2, column=0, pady=5)
    codomain_entry = Entry(left_frame)
    codomain_entry.grid(row=3, column=0, pady=5)
    codomain_entry.bind("<Return>", on_value_finalized)
    codomain_entry.bind("<FocusOut>", on_value_finalized)

    # 함숫값 입력칸
    Label(left_frame, text="Enter relations (e.g. f(a)=1;f(b)=2):").grid(row=4, column=0, pady=5)
    relation_entry = Entry(left_frame)
    relation_entry.grid(row=5, column=0, pady=5)
    relation_entry.bind('<Return>', draw_arrows_and_clear_entry)


    #함수 이름 보이기
    show_arrow_checkbox = tk.Checkbutton(left_frame, text="Show function Name", variable=show_arrow_var, command=toggle_arrow)
    show_arrow_checkbox.grid(row=6, column=0, pady=5)  # grid 위치는 적절하게 조정해야 할 수 있습니다.
    
    #역함수 버튼
    inverse_button = tk.Button(left_frame, text="inverse arrows", command=reverse_arrows_direction)
    inverse_button.grid(row=7, column=0, pady=5)
    
    #화살표 지우기 
    remove_arrows_button = tk.Button(left_frame, text="Remove Arrows", command=remove_arrows)
    remove_arrows_button.grid(row=8, column=0, pady=5)
    # 레이아웃을 위한 공간 (버튼이 들어갈 정도의 공간)
    empty_label = Label(left_frame, text="")
    empty_label.grid(row=9, column=0)

    # 클립보드    
    clip_button = tk.Button(left_frame, text="copy_to_clipboard", command=copy_to_clipboard, bg="#87CEEB")  # 하늘색
    clip_button.grid(row=10, column=0, pady=5)

    # 이미지 저장
    save_button = tk.Button(left_frame, text="Save as Image", command=save_as_image, bg="#98FB98")  # 연두색
    save_button.grid(row=11, column=0, pady=5)


    
    #만든이표시
    creator_label = tk.Label(bottom_frame, text="Made by Namgung Yeon @Sokcho 2023.10.6", font=("Arial", 10), fg="gray")
    creator_label.pack(pady=5)  # 이제 여기서 side=tk.BOTTOM을 삭제했습니다.

    # 하이퍼링크 부분
    link_label = tk.Label(bottom_frame, text="https://namgungyeon.tistory.com/", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
    link_label.pack(pady=5)  # 여기서도 side와 anchor를 삭제했습니다.
    link_label.bind("<Button-1>", open_link)
    # 정의역과 공역의 초기 값을 설정
    domain_entry.insert(0, "a,b,c,d")
    codomain_entry.insert(0, "1,2,3")
    
    draw_only_ellipse()
    
    # 프로그램 시작 시 함숫값 입력칸에 포커스를 설정
    root.after(100, lambda: relation_entry.focus_set())  # after 메서드를 사용하여 약간의 지연 후에 포커스 설정

    root.mainloop()



