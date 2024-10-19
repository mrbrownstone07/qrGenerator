import os
import qrcode
import pyperclip
from PIL import Image
import streamlit as st
from io import BytesIO
from colorthief import ColorThief


# Function to extract color suggestions from an image
def get_image_colors(image_path, num_colors=6):
    color_thief = ColorThief(image_path)
    palette = color_thief.get_palette(color_count=num_colors)
    return palette

# Function to generate QR code with customizable colors and sizes
def generateQR(qr_string: str, image_path: str, fg_color: str, bg_color: str, qr_size: int, logo_size_factor: float):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=qr_size,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert('RGB')

    if image_path:
        logo = Image.open(image_path)

        # Resize the logo based on user input
        logo_size = (int(qr_img.size[0] * logo_size_factor), int(qr_img.size[1] * logo_size_factor))
        logo = logo.resize(logo_size)

        # Calculate position to center the logo on the QR code
        pos = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)
        qr_img.paste(logo, pos)

    return qr_img

def show_color_suggestion(i: int):
    color = "#{:02x}{:02x}{:02x}".format(*colors[i])
    st.color_picker(color,value=color, disabled=False)
    if st.button(f"📋", key=f"copy_hex_{color}"):
        pyperclip.copy(color)
        st.toast(f"🔥 Copied {color}")



# Streamlit app layout
st.title("💸 QR Code Generator")
st.markdown("🔗 mahdi mohammad shibli", unsafe_allow_html=True)

# Input for string
qr_string = st.text_input("Enter text for the QR Code", "")
uploaded_image = st.file_uploader("Upload an image (optional, for embedding)", type=["png", "jpg", "jpeg"])

# Initial default colors for QR code
default_fg_color = "#000000"
default_bg_color = "#FFFFFF"

# Variables to hold selected colors for foreground and background
if 'fg_color' not in st.session_state:
    st.session_state.fg_color = default_fg_color
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = default_bg_color


# Sliders to adjust QR code and logo sizes in sidebar
qr_size = st.sidebar.slider("QR Code Size", min_value=5, max_value=20, value=10)
logo_size_factor = st.sidebar.slider("Embedded Image Size", min_value=0.1, max_value=0.5, value=0.25)

# Display color suggestions if an image is uploaded
if uploaded_image:
    img = Image.open(uploaded_image)
    img_path = "temp_image.png"
    img.save(img_path)

    # Get six color suggestions from the image
    colors = get_image_colors(img_path)

    st.sidebar.write("Suggested Colors from the Image:")

    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        show_color_suggestion(0)
        show_color_suggestion(1)
    with col2:
        show_color_suggestion(2)
        show_color_suggestion(3)
    with col3:
        show_color_suggestion(4)
        show_color_suggestion(5)
        
    # Color pickers for foreground and background in sidebar
    st.session_state.fg_color = st.sidebar.color_picker("QR Foreground Color", value=default_fg_color)
    st.session_state.bg_color = st.sidebar.color_picker("QR Background Color", value=default_bg_color)
else:
    # If no image is uploaded, use color pickers for manual selection
    st.session_state.fg_color = st.sidebar.color_picker("QR Foreground Color", value=default_fg_color)
    st.session_state.bg_color = st.sidebar.color_picker("QR Background Color", value=default_bg_color)

# Realtime preview of the QR code in the main layout
if qr_string:
    if uploaded_image:
        qr_img = generateQR(qr_string, img_path, st.session_state.fg_color, st.session_state.bg_color, qr_size, logo_size_factor)
    else:
        qr_img = generateQR(qr_string, None, st.session_state.fg_color, st.session_state.bg_color, qr_size, logo_size_factor)

    st.image(qr_img, caption="Generated QR Code", width=300, use_column_width=False, output_format="auto")

    # Downloadable version
    buf = BytesIO()
    qr_img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download QR Code",
        data=byte_im,
        file_name="qr_code.png",
        mime="image/png"
    )

    # Cleanup the temporary file if created
    if uploaded_image:
        os.remove(img_path)
else:
    st.error("Please enter some text for the QR Code.")
pip 