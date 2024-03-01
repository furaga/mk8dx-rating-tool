from pathlib import Path
import cv2
import numpy as np

names = [
    "マリオカートスタジアム",
    "ウォーターパーク",
    "スイーツキャニオン",
    "ドッスンいせき",
    "マリオサーキット",
    "キノピオハーバー",
    "ねじれマンション",
    "ヘイホーこうざん",
    "サンシャインくうこう",
    "ドルフィンみさき",
    "エレクトロドリーム",
    "ワリオスノーマウンテン",
    "スカイガーデン",
    "ホネホネさばく",
    "クッパキャッスル",
    "新レインボーロード",
    "ヨッシーサーキット",
    "エキサイトバイク",
    "ドラゴンロード",
    "ミュートシティ",
    "ベビィパーク",
    "チーズランド",
    "ネイチャーロード",
    "どうぶつの森",
    "モーモーカントリー",
    "GBAマリオサーキット",
    "プクプクビーチ",
    "キノピオハイウェイ",
    "カラカラさばく",
    "ドーナツへいや",
    "ピーチサーキット",
    "DKジャングル",
    "ワリオスタジアム",
    "シャーベットランド",
    "ミュージックパーク",
    "ヨッシーバレー",
    "チクタクロック",
    "パックンスライダー",
    "グラグラかざん",
    "N64レインボーロード",
    "ワリオこうざん",
    "SFCレインボーロード",
    "ツルツルツイスター",
    "ハイラルサーキット",
    "ネオクッパシティ",
    "リボンロード",
    "リンリンメトロ",
    "ビッグブルー",
]

n_boxes = {
    "ワリオスノーマウンテン": 8,
    "ホネホネさばく": 4,
    "ベビィパーク": 2,
    "モーモーカントリー": 2,
    "キノピオハイウェイ": 5,
    "ドーナツへいや": 2,
    "ヨッシーバレー": 4,
    "チクタクロック": 4,
    "パックンスライダー": 4,
    "N64レインボーロード": 6,
    "リンリンメトロ": 4,
    "ビッグブルー": 8,
}

all_img_paths = list(Path(r"C:\Users\furag\Videos").glob("*.png"))

offset = 0

def imread_safe(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None


def imwrite_safe(filename, img, params=None):
    try:
        import os

        ext = os.path.splitext(filename)[1]
        result, n = cv2.imencode(ext, img, params)

        if result:
            with open(filename, mode="w+b") as f:
                n.tofile(f)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


for name in names:
    n = n_boxes.get(name, 3)
    for i in range(n):
        path = all_img_paths[offset + i]
        new_path = Path(f"data/{name}") /f"{name}_{i}.jpg"
        print(f"Renaming {path} to {new_path}")
        new_path.parent.mkdir(parents=True, exist_ok=True)
        img = imread_safe(str(path))
        img = cv2.resize(img, (16 * 50, 9 * 50))
        imwrite_safe(str(new_path), img)
    offset += n
