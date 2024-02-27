import cv2
import numpy as np

# 動画ファイルの読み込み
video = cv2.VideoCapture("input_video.mkv")

# 動画のフレームレートを取得
fps = int(video.get(cv2.CAP_PROP_FPS))

# 動画のフレームサイズを取得

ox, oy = 1528, 150

# マスク画像の読み込み
mask = cv2.imread("mask.png", cv2.IMREAD_GRAYSCALE)[:oy, ox:]

# frame_size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
frame_size = (mask.shape[1], mask.shape[0])

# 出力動画ファイルの設定
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output_video.mp4", fourcc, fps, frame_size)

cnt = 0
while True:
    ret, frame = video.read()
    if not ret:
        break

    cnt += 1
    if cnt < 380:
        continue

    frame = frame[:oy, ox:]
    if cnt % 1000 == 0:
        print(cnt)
    # マスク画像を適用して動画を切り抜く
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask)
    masked_frame[mask == 0, 1] = 255

    # 出力動画にフレームを書き込む
    out.write(masked_frame)

    # # フレームを表示する (オプション)
    # cv2.imshow('masked_frame', masked_frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# リソースを解放
video.release()
out.release()
cv2.destroyAllWindows()
