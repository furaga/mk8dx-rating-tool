from pathlib import Path
import cv2
import numpy as np

path = Path(r"C:\Users\furag\Documents\prog\python\mk8dx_tools\mirror_200cc_analyzer\data\thumbnails_2")
for img_path in path.glob("*.png"):
    Path(img_path.stem.split('_')[0]).mkdir(exist_ok=True, parents=True)
