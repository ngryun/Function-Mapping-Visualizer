# Function-Mapping-Visualizer

This tool provides an interactive GUI to visualize relations between elements of
sets.  The application uses Matplotlib for rendering and supports drawing arrows
between elements by clicking on them.

## Requirements

Install the dependencies listed in `requirements.txt` using `pip install -r requirements.txt`.

## Font configuration

If you enter non‑ASCII characters (for example Korean text) you may see
warnings about missing glyphs.  The code now attempts to select a font that can
display Hangul characters automatically.  Ensure that at least one of the
following fonts is installed on your system:

- AppleGothic
- Malgun Gothic
- NanumGothic
- DejaVu Sans

If none of these fonts are available, you may still see the warnings.
