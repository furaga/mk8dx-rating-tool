import base64
from pathlib import Path

import cv2
import numpy as np
import streamlit as st
from streamlit_image_select import image_select

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
        for course_name in constants.COURSE_NAMES[:48]
    ]

    images = []
    for path in image_paths:
        with open(path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
        img = f"data:image/jpeg;base64, {encoded}"
        images.append(img)
    return images


with st.sidebar:
    images = get_encoded_images()

    img = image_select(
        label="",
        images=images,
        captions=["" for _ in images],
    )


index = images.index(img)
print(f"{index=}")

if index >= 0:
    course = constants.COURSE_NAMES[index]

    item_boxes = list(Path(f"data/item_boxes/{course}").glob(f"{course}_*.jpg"))

    item_box = image_select(
        label="",
        images=item_boxes,
        captions=["" for _ in item_boxes],
    )

    print(item_box)

    st.image(str(item_box), caption="")

    name, idx = item_box.stem.split("_")
    idx = int(idx)
    item_table = Path(f"data/item_table/{name}.png")
    if not item_table.exists():
        item_table = Path(f"data/item_table/{name}_0.png")

    st.image(str(item_table), caption="")
