import numpy as np
import matplotlib.pyplot as plt
import re
from matplotlib.patches import FancyArrowPatch
import config


def get_y_values(elements, a):
    total_parts = len(elements) + 2
    y_all_values = np.linspace(a, -a, total_parts)
    return y_all_values[1:-1]

def draw_arrow(ax, domain_elements, codomain_elements, relation, x_offset_domain, x_offset_codomain):
    pattern = re.compile(r'f\((.*?)\)=([\w]+)')  # 정규 표현식 패턴
    #수정필요
    max_elements = max(len(domain_elements), len(codomain_elements))
    a = (max_elements+1)/2
    
    y_values_domain = get_y_values(domain_elements, a)
    y_values_codomain = get_y_values(codomain_elements, a)

    for rel in relation:
        match = pattern.match(rel)
        if match:  # 패턴이 일치하는 경우
            start_element = match.group(1).strip()  # f() 안의 값을 추출
            end_element = match.group(2).strip()
            try:
                start_y = y_values_domain[domain_elements.index(start_element)]
                end_y = y_values_codomain[codomain_elements.index(end_element)]
                
                # Offset arrow endpoints slightly so they do not start/end
                # exactly at the centre of the text labels.
                x2 = x_offset_codomain - 0.2 * (a / 2)
                y2 = end_y
                x1 = x_offset_domain + 0.2 * (a / 2)
                y1 = start_y
                
                arrow = FancyArrowPatch((x1, y1), (x2, y2), mutation_scale=15, arrowstyle='-|>', color="black")
                ax.add_patch(arrow)
            except ValueError:
                pass  # If input relation doesn't match domain or codomain, we'll skip drawing the arrow for that relation

def draw_elements(ax, elements, y_values, x_offset=0):
    for i, element in enumerate(elements):
        ax.text(x_offset, y_values[i], r'${}$'.format(element), ha='center', va='center', fontsize=config.current_fontsize)
def draw_ellipse(domain_elements, codomain_elements):
    max_elements = max(len(domain_elements), len(codomain_elements))
    a = (max_elements+1)/2
    b = a / 2

    theta = np.linspace(0, 2 * np.pi, 1000)
    x = b * np.cos(theta)
    y = a * np.sin(theta)

    fig = plt.Figure(figsize=(7, 6))
    ax = fig.add_subplot(111)
    plt.rcParams['mathtext.fontset'] = 'cm'
    
    # Drawing the domain ellipse
    ax.plot(x, y, color='black')
    y_values_domain = get_y_values(domain_elements, a)
    draw_elements(ax, domain_elements, y_values_domain)

    # Drawing the codomain ellipse translated to the right
    y_values_codomain = get_y_values(codomain_elements, a)
    ax.plot(x + 3*b, y, color='black')
    draw_elements(ax, codomain_elements, y_values_codomain, 3*b)

    ax.text(0, a, r'$X$', ha='center', va='center', fontsize=30, 
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.5'))
    ax.text(3*b, a, r'$Y$', ha='center', va='center', fontsize=30, 
        bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.5'))
    
    ax.set_xlim([-b, 4 * b])  # 조금의 여백을 위해 -1과 +1을 추가
    ax.set_ylim([-a + b*0.5, a + b*0.5])     # 조금의 여백을 위해 -1과 +1을 추가

    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.axis('equal')
    # Adjust the layout
    fig.tight_layout()
    return fig, a, b
