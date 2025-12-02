# Global variable to store the current font size for drawing elements
current_fontsize = 27

# Name of the function currently displayed (default 'f').
current_function_name = 'f'

# Names for domain and codomain sets (default 'X' and 'Y')
domain_name = 'X'
codomain_name = 'Y'

# Whether arrows are currently shown in inverse direction.
arrows_inverse = False

# Matplotlib artist for the displayed function name text.  Allows easy update
# or removal when toggling settings.
function_text_artist = None

# --- Interactive Arrow Drawing State ---
# Stores information about the starting point of an arrow being drawn interactively.
# Format: {'coords': (x, y), 'name': 'element_name_str'} or None if no arrow drawing is in progress.
arrow_start_point = None

# Visual feedback marker when selecting an element for arrow drawing
selected_marker = None

# --- Ellipse Parameters ---
# These store the semi-major (a) and semi-minor (b) axes lengths of the currently displayed ellipses.
# They are updated whenever the ellipses are redrawn (e.g., due to element changes or window resize).
# Used for click detection within ellipses and for scaling arrow offsets.
current_a = None  # Semi-major axis (height for the ellipses)
current_b = None  # Semi-minor axis (width for the ellipses)

# Matplotlib figure object currently being displayed.  Many GUI functions rely on
# this reference when redrawing or saving the canvas.
current_fig = None
