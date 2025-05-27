import tkinter as tk
from tkinter import ttk 
from tkinter import Entry, Label, Button, filedialog, simpledialog
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, ArrowStyle
import matplotlib.patches as patches
import numpy as np
from graphics import draw_ellipse, draw_arrow, get_y_values # get_y_values is used by get_closest_element
from utils import save_as_image, copy_to_clipboard
import config
import math # For Euclidean distance in get_closest_element

# --- Global variable for Matplotlib Canvas ---
# This holds the FigureCanvasTkAgg object to allow connecting/disconnecting events
# and accessing canvas-specific methods if needed elsewhere.
canvas_tk_agg_obj = None
# Widgets that need to be updated when the function name changes
show_arrow_checkbox = None
relations_label_widget = None


def _is_ascii(text):
    """Return True if all characters in text are ASCII."""
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    return True

def reverse_arrows_direction():
    """Toggle all arrow directions and update the displayed function name."""
    if not config.current_fig:
        return

    config.arrows_inverse = not config.arrows_inverse

    ax = config.current_fig.gca()

    # Position for the function name text
    a_temp, b_temp = config.current_a, config.current_b
    if a_temp is None or b_temp is None:
        return
    mid_point_x = (0 + 0.5*b_temp + 3*b_temp - 0.5*b_temp) / 2
    mid_point_y = a_temp + 0.07*b_temp

    remove_functionName()
    if _is_ascii(config.current_function_name):
        text = fr'${config.current_function_name}$'
        if config.arrows_inverse:
            text = fr'${config.current_function_name}^{{-1}}$'
    else:
        text = config.current_function_name
        if config.arrows_inverse:
            text += '^-1'
    style = '<|-' if config.arrows_inverse else '-|>'

    config.function_text_artist = ax.text(mid_point_x, mid_point_y, text,
                                          ha='center', va='bottom', fontsize=30,
                                          color='black')

    # Update arrowstyle for all arrows
    for patch in ax.patches[:]:
        if isinstance(patch, patches.FancyArrowPatch):
            patch.set_arrowstyle(style)

    refresh_canvas()


def remove_arrows():
    """Removes all relation arrows (arrows not labeled 'special_arrow') from the canvas."""
    if not config.current_fig:
        return
    ax = config.current_fig.gca()
    for patch in ax.patches[:]: # Iterate over a copy for safe removal
        if isinstance(patch, patches.FancyArrowPatch) and patch.get_label() != "special_arrow":
            patch.remove()
    if hasattr(config.current_fig, 'canvas'): config.current_fig.canvas.draw_idle()


def toggle_arrow():
    """Toggles the visibility of the main function arrow (labeled 'special_arrow') and its name (f or f^-1)."""
    if show_arrow_var.get():
        draw_with_arrow() # This will draw the 'special_arrow' and its name
    else:
        remove_special_arrow() # Removes 'special_arrow'
        remove_functionName()  # Removes the function name 'f' or 'f^-1'
        # refresh_canvas() # Not strictly needed as remove_special_arrow/remove_functionName redraw


def change_function_name():
    """Prompt user for a new function name and update labels."""
    old_name = config.current_function_name
    new_name = simpledialog.askstring("Function name",
                                      "Enter function name:",
                                      initialvalue=old_name)
    if new_name:
        config.current_function_name = new_name.strip()
        if show_arrow_checkbox:
            show_arrow_checkbox.config(text=f"Show function Name ({config.current_function_name})")
        if relations_label_widget:
            relations_label_widget.config(
                text=f"Relations (e.g. {config.current_function_name}(a)=1;{config.current_function_name}(b)=2):")

        # Update existing relations in entry to use new name
        cur_rel = relation_entry.get()
        if cur_rel:
            try:
                import re
                pattern = re.compile(re.escape(old_name) + r"\(")
                cur_rel = pattern.sub(config.current_function_name + "(", cur_rel)
                relation_entry.delete(0, tk.END)
                relation_entry.insert(0, cur_rel)
            except Exception:
                pass

        # Update displayed function name text if present
        if config.function_text_artist:
            if _is_ascii(config.current_function_name):
                txt = fr'${config.current_function_name}$'
                if config.arrows_inverse:
                    txt = fr'${config.current_function_name}^{{-1}}$'
            else:
                txt = config.current_function_name
                if config.arrows_inverse:
                    txt += '^-1'
            config.function_text_artist.set_text(txt)
            refresh_canvas()

def remove_special_arrow():
    """Removes the main function arrow (labeled 'special_arrow') from the canvas."""
    if not config.current_fig or config.current_a is None or config.current_b is None:
        return
    ax = config.current_fig.gca()
    for patch in list(ax.patches): # Iterate over a copy
        if hasattr(patch, 'get_label') and patch.get_label() == "special_arrow":
            patch.remove()
    if hasattr(config.current_fig, 'canvas'): config.current_fig.canvas.draw_idle()


def remove_functionName():
    """Remove the function name text from the canvas if present."""
    if config.function_text_artist is not None:
        try:
            config.function_text_artist.remove()
        finally:
            config.function_text_artist = None
            refresh_canvas()


def refresh_canvas():
    """Redraws the Matplotlib canvas if it exists."""
    if hasattr(config, 'current_fig') and config.current_fig and hasattr(config.current_fig, 'canvas'):
        config.current_fig.canvas.draw_idle()


def draw_with_arrow():
    """Draws the main function arrow and its name (f) on the canvas. Assumes f, not f^-1."""
    if not config.current_fig:
        draw_only_ellipse() # Ensure figure and ellipses exist
        if not config.current_fig : # If still no figure, cannot proceed
             return 
    
    ax = config.current_fig.gca()
    if config.current_a is None or config.current_b is None: return # Ellipse params needed
    a_temp, b_temp = config.current_a, config.current_b

    # Define start and end points for the main function arrow (X to Y)
    start_point = (0 + 0.5*b_temp, a_temp) # Offset from center of domain ellipse top
    end_point = (3*b_temp - 0.5*b_temp, a_temp) # Offset from center of codomain ellipse top
    
    # Calculate midpoint for placing the function name 'f'
    mid_point_x = (start_point[0] + end_point[0]) / 2
    mid_point_y = a_temp + 0.07*b_temp # Slightly above the arrow

    # Remove any existing special arrow and function name before drawing new ones
    remove_special_arrow() 
    remove_functionName()

    style = '<|-' if config.arrows_inverse else '-|>'
    arrow = FancyArrowPatch(start_point, end_point, mutation_scale=15,
                            arrowstyle=style, color="black", label="special_arrow")
    ax.add_patch(arrow)
    if _is_ascii(config.current_function_name):
        text = fr'${config.current_function_name}$'
        if config.arrows_inverse:
            text = fr'${config.current_function_name}^{{-1}}$'
    else:
        text = config.current_function_name
        if config.arrows_inverse:
            text += '^-1'
    config.function_text_artist = ax.text(mid_point_x, mid_point_y, text,
                                          ha='center', va='bottom', fontsize=30,
                                          color='black')
    
    if hasattr(config.current_fig, 'canvas'): config.current_fig.canvas.draw_idle()


def open_link(event):
    """Opens the provided URL in a new web browser tab."""
    webbrowser.open_new("https://namgungyeon.tistory.com/")


def draw_only_ellipse():
    """
    Core function to draw/redraw the ellipses and their elements.
    Updates global config for ellipse parameters and canvas object.
    Connects canvas click events.
    """
    global canvas_tk_agg_obj # Needed to store/update the canvas object for event handling

    domain_elements_str = domain_entry.get()
    codomain_elements_str = codomain_entry.get()

    # If domain or codomain is empty, clear the canvas and reset config params
    if not domain_elements_str.strip() or not codomain_elements_str.strip(): 
        if hasattr(config, 'current_fig') and config.current_fig:
            for widget in right_frame.winfo_children(): # Clear existing canvas widget from frame
                widget.destroy()
            if config.current_fig: # Clear Matplotlib figure object
                config.current_fig.clf() 
                plt.close(config.current_fig) 
            config.current_fig = None
            config.current_a = None 
            config.current_b = None
            # Disconnect previous canvas events if any (though canvas_tk_agg_obj might be None or stale)
            if canvas_tk_agg_obj and hasattr(canvas_tk_agg_obj, '_tkcanvas'):
                 # This is tricky; proper event disconnection needs care.
                 # For now, relying on new canvas creation.
                 pass
            canvas_tk_agg_obj = None
            config.selected_marker = None
        return

    domain_elements = [e.strip() for e in domain_elements_str.split(',') if e.strip()]
    codomain_elements = [e.strip() for e in codomain_elements_str.split(',') if e.strip()]
    if not domain_elements: domain_elements = [""] # Ensure it's not completely empty for graphics.py
    if not codomain_elements: codomain_elements = [""]


    # Call graphics.py to draw ellipses; it returns fig, a, b
    fig, a, b = draw_ellipse(domain_elements, codomain_elements)
    config.current_fig = fig
    config.current_a = a  # Store ellipse semi-major axis
    config.current_b = b  # Store ellipse semi-minor axis
    config.selected_marker = None

    # Clear previous canvas widget from the Tkinter frame
    for widget in right_frame.winfo_children(): 
        widget.destroy()
    
    # Create new FigureCanvasTkAgg object and embed it in the Tkinter frame
    canvas_tk_agg_obj = FigureCanvasTkAgg(config.current_fig, master=right_frame)
    canvas_widget = canvas_tk_agg_obj.get_tk_widget()
    canvas_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # Make canvas responsive
    
    # Connect the 'button_press_event' (mouse click) on the canvas to the handler function
    # This is done here because canvas_tk_agg_obj is recreated each time.
    canvas_tk_agg_obj.callbacks.connect('button_press_event', on_canvas_click)

    # Draw the main function arrow ('f') if the checkbox is ticked
    if show_arrow_var.get():
        draw_with_arrow()
    else: 
        remove_special_arrow() # Ensure it's removed if checkbox is off
        remove_functionName()

    canvas_tk_agg_obj.draw() # Refresh the canvas display


def get_closest_element_in_ellipse(x_click, y_click, elements, elements_x_offset, a, b):
    """
    Finds the element (text label) in an ellipse closest to the click coordinates.
    
    Args:
        x_click, y_click: Coordinates of the mouse click.
        elements: List of element name strings.
        elements_x_offset: X-coordinate of the center of the ellipse where elements are located.
        a, b: Semi-major and semi-minor axes of the ellipse.
        
    Returns:
        A dictionary {'coords': (elem_x, elem_y), 'name': 'element_name'} if a close element is found, 
        otherwise None.
    """
    if not elements or (len(elements) == 1 and not elements[0]): # Handle empty or [""] elements list
        return None
    
    y_coords_of_elements = get_y_values(elements, a) # Get y-positions of elements from graphics.py
    # y_coords_of_elements is a numpy array; avoid ambiguous truth value check
    if len(y_coords_of_elements) == 0:
        return None  # Should not happen if elements is not empty, but good check

    min_dist_sq = float('inf') # Use squared distance to avoid sqrt until necessary
    found_element_info = None
    
    # Heuristic for clickable radius around element text (y-axis based)
    # This is roughly half the vertical spacing between elements.
    clickable_radius_y = (a / (len(elements) + 1)) / 2 if len(elements) > 0 else a / 2

    for i, element_name in enumerate(elements):
        if i >= len(y_coords_of_elements): break # Safety break if y_coords mismatch
        elem_y = y_coords_of_elements[i]
        
        # Calculate squared Euclidean distance from click to element's center
        dist_sq = (x_click - elements_x_offset)**2 + (y_click - elem_y)**2
        
        if dist_sq < min_dist_sq:
            # Check if the vertical distance to element is within a reasonable 'clickable' range
            # This helps prioritize elements that are vertically aligned with the click,
            # even if another element is slightly closer in raw Euclidean distance but far vertically.
            if abs(y_click - elem_y) < clickable_radius_y * 1.5: # Generous vertical click area (1.5x radius)
                min_dist_sq = dist_sq
                found_element_info = {'coords': (elements_x_offset, elem_y), 'name': element_name.strip()}

    # After finding the closest by the above criteria, apply a final distance threshold.
    # If the closest element found is still too far (e.g., > 60% of ellipse width 'b'), ignore it.
    if found_element_info and min_dist_sq > (b * 0.6)**2: 
        return None

    return found_element_info


def on_canvas_click(event):
    """
    Handles mouse clicks on the Matplotlib canvas to interactively draw arrows.
    Manages a two-click process: first click on domain, second on codomain.
    """
    # Ignore clicks outside the plottable area or if critical parameters are missing
    if event.xdata is None or event.ydata is None: return
    if config.current_a is None or config.current_b is None or config.current_fig is None: return

    x, y = event.xdata, event.ydata
    a, b = config.current_a, config.current_b

    domain_elements = [e.strip() for e in domain_entry.get().split(',') if e.strip()]
    codomain_elements = [e.strip() for e in codomain_entry.get().split(',') if e.strip()]

    # Check if click is within the domain ellipse (centered at (0,0))
    # Ellipse equation: (x/b)^2 + (y/a)^2 = 1
    is_in_domain_ellipse = (x / b)**2 + (y / a)**2 <= 1.1 # Using 1.1 for a slightly larger clickable area

    # Check if click is within the codomain ellipse (centered at (3*b,0))
    codomain_center_x = 3 * b
    is_in_codomain_ellipse = ((x - codomain_center_x) / b)**2 + (y / a)**2 <= 1.1 # Using 1.1

    if config.arrow_start_point is None: # This is the potential first click (selecting arrow start)
        if is_in_domain_ellipse:
            # Find the specific element clicked on in the domain
            clicked_element_info = get_closest_element_in_ellipse(x, y, domain_elements, 0, a, b)
            if clicked_element_info:
                config.arrow_start_point = clicked_element_info
                # Visual feedback for selected start point
                ax = config.current_fig.gca()
                if config.selected_marker:
                    try:
                        config.selected_marker.remove()
                    except Exception:
                        pass
                config.selected_marker = ax.plot(
                    clicked_element_info['coords'][0],
                    clicked_element_info['coords'][1],
                    marker='o', markersize=10, markerfacecolor='none',
                    markeredgecolor='red', markeredgewidth=2
                )[0]
                refresh_canvas()
        # If not in domain or no element found, do nothing, wait for a valid start click.
    else: # This is the potential second click (selecting arrow end and drawing)
        if is_in_codomain_ellipse:
            # Find the specific element clicked on in the codomain
            clicked_element_info = get_closest_element_in_ellipse(x, y, codomain_elements, codomain_center_x, a, b)
            if clicked_element_info:
                start_info = config.arrow_start_point
                end_info = clicked_element_info

                x1_center, y1_center = start_info['coords']
                x2_center, y2_center = end_info['coords']

                # Apply a small offset from element centers for arrow start/end points for better visuals
                arrow_offset_x = 0.15 * b # Heuristic offset based on ellipse width
                x1_arrow = x1_center + arrow_offset_x 
                x2_arrow = x2_center - arrow_offset_x 

                ax = config.current_fig.gca()
                style = '<|-' if config.arrows_inverse else '-|>'
                arrow = FancyArrowPatch((x1_arrow, y1_center), (x2_arrow, y2_center),
                                        mutation_scale=15, arrowstyle=style, color="black", lw=1.0)
                ax.add_patch(arrow) # Add the new arrow to the plot
                refresh_canvas()

                # Update the relation_entry text field with the new relation
                fn = config.current_function_name
                new_relation_str = f"{fn}({start_info['name']})={end_info['name']}"
                current_relations = relation_entry.get()
                if current_relations:
                    relation_entry.insert(tk.END, f";{new_relation_str}")
                else:
                    relation_entry.delete(0, tk.END) # Clear if empty before inserting
                relation_entry.insert(0, new_relation_str)
        # Always reset arrow_start_point after the second click attempt, regardless of success.
        # Remove visual feedback marker if present.
        if config.selected_marker:
            try:
                config.selected_marker.remove()
            except Exception:
                pass
            config.selected_marker = None
        config.arrow_start_point = None
        # A full redraw might be needed if markers are left and not handled:
        # draw_only_ellipse()


def draw_arrows():
    """Draws arrows based on the text in relation_entry."""
    if not config.current_fig or config.current_a is None or config.current_b is None: 
        return
    ax = config.current_fig.gca()
    
    domain_elements_str = domain_entry.get()
    codomain_elements_str = codomain_entry.get()
    relation_str = relation_entry.get()

    if not domain_elements_str.strip() or not codomain_elements_str.strip() or not relation_str.strip(): 
        return # Nothing to draw if inputs are empty
    
    domain_elements = [e.strip() for e in domain_elements_str.split(',') if e.strip()]
    codomain_elements = [e.strip() for e in codomain_elements_str.split(',') if e.strip()]
    relations = [r.strip() for r in relation_str.split(';') if r.strip()]
    
    if not domain_elements or not codomain_elements or not relations: return

    # Call graphics.draw_arrow, which handles parsing relation strings and drawing
    # It recalculates 'a' internally, which is fine. Uses config.current_b for codomain_x_offset.
    draw_arrow(ax, domain_elements, codomain_elements, relations, 0, 3 * config.current_b)
    refresh_canvas()


def draw_arrows_and_clear_entry(event=None):
    """Callback for relation_entry <Return> key: draws arrows and clears the entry."""
    draw_arrows()
    relation_entry.delete(0, tk.END) # Clear the entry field
    if root: root.after(100, lambda: relation_entry.focus_set()) # Keep focus on the entry


def on_value_finalized(event=None): 
    """Callback for domain/codomain entry changes: redraws the ellipses."""
    draw_only_ellipse()


def update_fontsize(new_size):
    """Callback for font size scale: updates font size in config and redraws."""
    config.current_fontsize = int(new_size)
    if hasattr(config, 'current_fig') and config.current_fig:
        draw_only_ellipse()
        draw_arrows()


def initialize_gui():
    """Initializes the main Tkinter GUI window, frames, widgets, and event bindings."""
    global show_arrow_var, root, domain_entry, codomain_entry, relation_entry, right_frame
    global show_arrow_checkbox, relations_label_widget
    # canvas_tk_agg_obj is handled by draw_only_ellipse

    root = tk.Tk()
    root.title("Function Relation Illustrator")
    show_arrow_var = tk.IntVar(value=1) # Checkbox for showing main function arrow 'f'
    
    # Configure root window grid for responsiveness
    root.grid_rowconfigure(0, weight=1) 
    root.grid_columnconfigure(1, weight=1) # Allow right_frame (canvas area) to expand

    main_frame = tk.Frame(root)
    main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    
    # Configure main_frame grid (holds left controls and right canvas)
    main_frame.grid_columnconfigure(0, weight=0) # Left controls, fixed width
    main_frame.grid_columnconfigure(1, weight=1) # Right canvas, expandable
    main_frame.grid_rowconfigure(0, weight=1)    # Allow row to expand vertically

    # Left frame for input controls
    left_frame = tk.Frame(main_frame)
    left_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ns") # North-South sticky

    # Right frame for Matplotlib canvas
    right_frame = tk.Frame(main_frame)
    right_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew") # All-direction sticky
    right_frame.grid_rowconfigure(0, weight=1)    # Canvas row expands
    right_frame.grid_columnconfigure(0, weight=1) # Canvas col expands

    # Bottom frame for credits/links
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(side=tk.BOTTOM, pady=5, fill=tk.X)

    # --- Input Widgets in left_frame ---
    Label(left_frame, text="Domain (e.g. a,b,c):").grid(row=0, column=0, columnspan=2, pady=(5,0), sticky=tk.W)
    domain_entry = Entry(left_frame, width=30) # Increased width slightly
    domain_entry.grid(row=1, column=0, columnspan=2, pady=2, sticky=tk.EW)
    domain_entry.bind("<Return>", on_value_finalized)
    domain_entry.bind("<FocusOut>", on_value_finalized)

    Label(left_frame, text="Codomain (e.g. x,y,z):").grid(row=2, column=0, columnspan=2, pady=(5,0), sticky=tk.W)
    codomain_entry = Entry(left_frame, width=30)
    codomain_entry.grid(row=3, column=0, columnspan=2, pady=2, sticky=tk.EW)
    codomain_entry.bind("<Return>", on_value_finalized)
    codomain_entry.bind("<FocusOut>", on_value_finalized)

    # Fontsize Scale
    Label(left_frame, text="Font Size:").grid(row=4, column=0, pady=(10,0), sticky=tk.W)
    fontsize_scale = tk.Scale(left_frame, from_=10, to=40, orient=tk.HORIZONTAL, command=update_fontsize)
    fontsize_scale.set(config.current_fontsize) 
    fontsize_scale.grid(row=4, column=1, pady=(10,0), sticky=tk.EW)
    
    left_frame.grid_columnconfigure(0, weight=0) # Label column for font size
    left_frame.grid_columnconfigure(1, weight=1) # Scale column for font size (expandable)

    global relations_label_widget, show_arrow_checkbox

    relations_label_widget = Label(left_frame,
        text=f"Relations (e.g. {config.current_function_name}(a)=1;{config.current_function_name}(b)=2):")
    relations_label_widget.grid(row=5, column=0, columnspan=2, pady=(10,0), sticky=tk.W)
    relation_entry = Entry(left_frame, width=30)
    relation_entry.grid(row=6, column=0, columnspan=2, pady=2, sticky=tk.EW)
    relation_entry.bind('<Return>', draw_arrows_and_clear_entry)

    # --- Control Buttons and Checkboxes ---
    show_arrow_checkbox = tk.Checkbutton(left_frame,
                                         text=f"Show function Name ({config.current_function_name})",
                                         variable=show_arrow_var, command=toggle_arrow)
    show_arrow_checkbox.grid(row=7, column=0, columnspan=2, pady=(10,0), sticky=tk.W)

    inverse_button = tk.Button(left_frame, text="Inverse Arrows & Function Name", command=reverse_arrows_direction)
    inverse_button.grid(row=8, column=0, columnspan=2, pady=5, sticky=tk.EW)

    change_name_button = tk.Button(left_frame, text="Change Function Name", command=change_function_name)
    change_name_button.grid(row=9, column=0, columnspan=2, pady=5, sticky=tk.EW)

    remove_arrows_button = tk.Button(left_frame, text="Remove Relation Arrows", command=remove_arrows)
    remove_arrows_button.grid(row=10, column=0, columnspan=2, pady=5, sticky=tk.EW)
    
    # Spacer (using pady in buttons above/below achieves similar)
    # Label(left_frame, text="").grid(row=10, column=0, columnspan=2) 

    clip_button = tk.Button(left_frame, text="Copy to Clipboard", command=copy_to_clipboard, bg="#87CEEB")
    clip_button.grid(row=11, column=0, columnspan=2, pady=(15,5), sticky=tk.EW) # Added more top padding

    save_button = tk.Button(left_frame, text="Save as Image", command=save_as_image, bg="#98FB98")
    save_button.grid(row=12, column=0, columnspan=2, pady=5, sticky=tk.EW)
    
    # --- Bottom Frame Content (Credits) ---
    creator_label = tk.Label(bottom_frame, text="Made by Namgung Yeon @Sokcho 2023.10.6", font=("Arial", 10), fg="gray")
    creator_label.pack(side=tk.LEFT, padx=10)

    link_label = tk.Label(bottom_frame, text="https://namgungyeon.tistory.com/", font=("Arial", 10, "underline"), fg="blue", cursor="hand2")
    link_label.pack(side=tk.RIGHT, padx=10)
    link_label.bind("<Button-1>", open_link)

    # --- Initial Setup ---
    domain_entry.insert(0, "a,b,c,d") # Default domain
    codomain_entry.insert(0, "1,2,3")  # Default codomain
    
    on_value_finalized() # Initial draw of ellipses based on default values
    
    if root: root.after(100, lambda: relation_entry.focus_set()) # Focus on relation entry
    if root: root.mainloop()


if __name__ == '__main__':
    initialize_gui()
