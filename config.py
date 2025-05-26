# Global variable to store the current font size for drawing elements
current_fontsize = 27

# --- Interactive Arrow Drawing State ---
# Stores information about the starting point of an arrow being drawn interactively.
# Format: {'coords': (x, y), 'name': 'element_name_str'} or None if no arrow drawing is in progress.
arrow_start_point = None

# --- Ellipse Parameters ---
# These store the semi-major (a) and semi-minor (b) axes lengths of the currently displayed ellipses.
# They are updated whenever the ellipses are redrawn (e.g., due to element changes or window resize).
# Used for click detection within ellipses and for scaling arrow offsets.
current_a = None  # Semi-major axis (height for the ellipses)
current_b = None  # Semi-minor axis (width for the ellipses)
