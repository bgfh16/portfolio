import streamlit as st
import base64

def load_css(file_path):
    """Reads a CSS file and injects it into the Streamlit app.
    This is a context manager: open(file_path) opens the file 
    and returns a "file object" (a temporary handle representing that open file). 
    as f just gives a name to that returned object. The reason we use "with" here 
    instead of just f = open(file_path) is safety: if you open a file manually,
    you have to remember to call f.close() yourself afterward. "with" guarantees 
    the file gets closed automatically, even if something goes wrong inside the 
    block, so it's the standard, recommended way to work with files in Python.
    """
    with open(file_path) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def get_base64_image(image_path):
    """Converts an image file into a Base64 string for embedding in CSS.
    Why? When Streamlit injects our CSS into the page, the browser tries 
    to resolve 'hero-bg.jpg' relative to the app's URL (something like localhost:8501),
    not relative to our assets folder on disk. Streamlit doesn't automatically serve files 
    from our project folder as web-accessible URLs the way a normal website's file server 
    would. So the browser looks for the image at a URL that doesn't actually exist, fails 
    silently, and just shows nothing behind the overlay.

    open(image_path, "rb") — opens the file in binary read mode ("rb"). Note this differs 
    from our earlier open(file_path) for the CSS file, which read plain text. Images aren't 
    text, they're binary data, so we must tell Python to read raw bytes rather than trying to
    interpret it as text (which would fail/corrupt the data).

    base64.b64encode(image_file.read()) — reads the raw bytes and encodes them into Base64 format.

    .decode() — converts the result from bytes into a plain Python string, so we can easily insert 
    it into our CSS text.
    """
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return encoded


def get_base64_svg(svg_string):
    """Converts an SVG string into a Base64 string for embedding as a background image."""
    encoded = base64.b64encode(svg_string.encode('utf-8')).decode()
    return encoded
