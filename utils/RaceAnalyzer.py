import cv2
import mk8dx_digit_ocr


def get_black_ratio(img):
    h, w = img.shape[:2]
    thr = 32
    black = cv2.inRange(img, (0, 0, 0), (thr, thr, thr))
    br = cv2.countNonZero(black) / (h * w)
    return br


def get_white_ratio(img):
    h, w = img.shape[:2]
    thr = 190
    white = cv2.inRange(img, (thr, thr, thr), (255, 255, 255))
    wr = cv2.countNonZero(white) / (h * w)
    return wr


def is_pre_race_screen(img):
    black_ratio = get_black_ratio(img)
    # print("black_ratio", black_ratio)
    if black_ratio < 0.22:
        return False

    white_ratio = get_white_ratio(img)
    # print("white_ratio", white_ratio)
    if white_ratio < 0.13:
        return False

    return True


def detect_number(img, verbose):
    coin_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, value = mk8dx_digit_ocr.detect_digit(coin_img, verbose)
    # print(ret, value)
    return ret, value


# コイン枚数
def detect_coin(img):
    h, w = img.shape[:2]
    x1 = int(133 / 1920 * w)
    x2 = int(214 / 1920 * w)
    y1 = int(972 / 1080 * h)
    y2 = int(1032 / 1080 * h)
    ret, num = detect_number(img[y1:y2, x1:x2], False)
    if ret and 0 <= num <= 10:
        return ret, num
    return False, -1


# 何周目か
def detect_lap(img, max_lap=3):
    h, w = img.shape[:2]
    x1 = int(300 / 1920 * w)
    x2 = int(347 / 1920 * w)
    y1 = int(970 / 1080 * h)
    y2 = int(1037 / 1080 * h)
    ret, num = detect_number(img[y1:y2, x1:x2], False)
    if ret and 1 <= num <= max_lap:
        return ret, num
    return False, -1


def detect_timer(img):
    h, w = img.shape[:2]

    ms_rect = [1141, 40, 1231, 80]
    s_rect = [1078, 40, 1137, 80]
    m_rect = [1040, 40, 1071, 80]

    ms_lim = [0, 1000]
    s_lim = [0, 60]
    m_lim = [0, 2]

    timer = []
    cnt = 0
    for [rx1, ry1, rx2, ry2], [t_min, t_max] in zip(
        [ms_rect, s_rect, m_rect], [ms_lim, s_lim, m_lim]
    ):
        cnt += 1
        x1 = int(rx1 / 1280 * w)
        x2 = int(rx2 / 1280 * w)
        y1 = int(ry1 / 720 * h)
        y2 = int(ry2 / 720 * h)

        cropped = img[y1:y2, x1:x2]
        # Shear: 上辺をx軸方向に3pxだけずらず
        import numpy as np

        shear_mat = np.array([[1, 0.1, 0], [0, 1, 0]]).astype(np.float32)
        cropped = cv2.warpAffine(
            cropped, shear_mat, (cropped.shape[1], cropped.shape[0])
        )
        # 周囲に10pxマージンをつける。数字が切れている場合に備える
        cropped = cv2.copyMakeBorder(
            cropped, 10, 10, 10, 10, cv2.BORDER_REPLICATE, value=(255, 255, 255)
        )

        ret, num = detect_number(cropped, False)  ## cnt == 1)
        cv2.imshow(f"img{cnt}", cropped)
        if ret and t_min <= num < t_max:
            timer.append(num)

    if len(timer) == 3:
        return True, f"{timer[2]:01d}:{timer[1]:02d}.{timer[0]:03d}"

    return False, ""
