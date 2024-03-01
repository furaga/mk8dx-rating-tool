import base64
import streamlit as st
from streamlit_image_select import image_select
from PIL import Image
from pathlib import Path
import cv2
import numpy as np
from utils import constants


def imread_safe(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

# キャッシュデコレータを利用した関数定義
@st.cache_resource()
def get_encoded_images():
    print("LOAD IMAGES")
    image_paths = [
        list((Path("data/courses") / course_name).glob("*.png"))[0]
        for course_name in constants.COURSE_NAMES[:48]]

    images = []
    for path in image_paths:
        img = imread_safe(str(path))
        ratio = 80 / img.shape[0]
        img = cv2.resize(img, (0, 0), fx=ratio, fy=ratio)
        size = max(img.shape[:2])
        thumb = np.zeros((size, size, 3), np.uint8)
        thumb.fill(128)
        offset_y = (size - img.shape[0]) // 2
        thumb[offset_y:offset_y + img.shape[0]] = img
        thumb = thumb[:,:,::-1]
        images.append(thumb)

    return images

with st.sidebar:
    images = get_encoded_images()

    img = image_select(
        label="",
        images=images,
        captions=["" for _ in images],
    )


# main_image_container = st.empty()

# clicked = clickable_images(
#     images,
#     titles=[f"Image #{str(i)}" for i in range(5)],
#     div_style={"display": "flex", "justify-content": "center", "flex-wrap": "wrap", "max-width": "800px"},
#     img_style={"margin": "5px", "width": "120px"},
# )

# st.markdown(f"Image #{clicked} clicked" if clicked > -1 else "No image clicked")


# # クリックされた画像があれば、対応する大きい画像を表示
# if clicked is not None and clicked >= 0:
    
#     clicked_course = constants.COURSE_NAMES[clicked]
    
#     item_box_path = Path("data/item_boxes") / clicked_course / f"{clicked_course}_{0}.jpg"
#  #   item_box_enc = encode_image(item_box_path)
    
# #    item_table_path = Path("data/item_table") / f"{clicked_course}.png"
#  #   item_table_enc = encode_image(item_table_path)

#     image_display_size = 720
#     main_image_container.image(str(item_box_path), caption=f"Image {clicked + 1}", width=image_display_size)
