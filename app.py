import streamlit as st
from PIL import Image, ImageSequence
import numpy as np
import tempfile
import os
from urllib.parse import quote

# === Custom CSS ===
st.markdown("""
<style>
    .main {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    h1 {
        color: #e63946;
        font-weight: 1500;
        margin-bottom: 0;
    }
    .stButton>button {
        background-color: #2a9d8f;
        color: white;
        border-radius: 12px;
        font-weight: bold;
        padding: 0.6rem 2rem;
    }
    .stButton>button:hover {
        background-color: #21867a;
    }
    div[data-testid="stButton"] button[kind="secondary"] {
        background: none;
        border: none;
        color: #2a9d8f;
        text-decoration: underline;
        font-weight: normal;
        padding: 0;
        box-shadow: none;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        color: #21867a;
        background: none;
    }
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Chimp Barber", page_icon="🐒", layout="centered")

# === Header ===
col1, col2 = st.columns([1, 2])
with col1:
    try:
        st.image("wbwPFP.gif", width=180)
    except:
        st.image("https://via.placeholder.com/180x180/e63946/ffffff?text=Chimp", width=180)

with col2:
    st.markdown("<h1>Chimp Barber</h1>", unsafe_allow_html=True)

st.markdown("---")

# === Main content ===
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

st.write("Upload the GIF you want to add the beard to.")

BEARD_PATH = "beard.gif"

uploaded_file = st.file_uploader("Your GIF", type=["gif"], label_visibility="collapsed")

# Advanced options (hidden by default)
if "show_advanced" not in st.session_state:
    st.session_state.show_advanced = False

if st.button("Advanced generation", type="secondary"):
    st.session_state.show_advanced = not st.session_state.show_advanced

if st.session_state.show_advanced:
    col_a, col_b = st.columns(2)
    with col_a:
        dx = st.slider("X Offset", -150, 150, 0)
    with col_b:
        dy = st.slider("Y Offset", -150, 150, 0)
else:
    dx = 0
    dy = 0

if st.button("Add the beard", type="primary") and uploaded_file is not None:
    if not os.path.exists(BEARD_PATH):
        st.error("beard.gif file is missing on the server")
    else:
        with st.spinner("Generating..."):
            beard = Image.open(BEARD_PATH)
            target = Image.open(uploaded_file)

            beard_frames = [np.array(f.convert("RGB")) for f in ImageSequence.Iterator(beard)]
            target_frames = [np.array(f.convert("RGB")) for f in ImageSequence.Iterator(target)]

            if len(beard_frames) != len(target_frames):
                st.error(f"The GIF must have {len(beard_frames)} frames")
            else:
                result_frames = []
                for b_arr, t_arr in zip(beard_frames, target_frames):
                    t_arr = t_arr.copy()
                    mask = ~np.all(b_arr == [255, 255, 255], axis=2)
                    ys, xs = np.where(mask)

                    for y, x in zip(ys, xs):
                        ty = int(y + dy)
                        tx = int(x + dx)
                        if 0 <= ty < t_arr.shape[0] and 0 <= tx < t_arr.shape[1]:
                            t_arr[ty, tx] = b_arr[y, x]

                    result_frames.append(Image.fromarray(t_arr))

                # Prepare files
                first_frame = result_frames[0]
                png_path = tempfile.mktemp(suffix=".png")
                first_frame.save(png_path, "PNG")

                gif_path = tempfile.mktemp(suffix=".gif")
                result_frames[0].save(
                    gif_path,
                    save_all=True,
                    append_images=result_frames[1:],
                    duration=beard.info.get("duration", 100),
                    loop=0,
                    optimize=True
                )

                # Tabs (GIF is first = default)
                tab_gif, tab_static = st.tabs(["GIF", "Static"])

                with tab_gif:
                    st.image(gif_path)
                    with open(gif_path, "rb") as f:
                        st.download_button(
                            "Download",
                            f,
                            file_name="chimpBarber.gif",
                            mime="image/gif",
                            key="download_gif"
                        )

                with tab_static:
                    st.image(png_path)
                    with open(png_path, "rb") as f:
                        st.download_button(
                            "Download",
                            f,
                            file_name="chimpBarber.png",
                            mime="image/png",
                            key="download_png"
                        )

                # Message under the downloads
                st.markdown("<p style='text-align: center; font-size: 1.1rem; margin-top: 1rem;'>Have a chimptastic day! 🐵</p>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)