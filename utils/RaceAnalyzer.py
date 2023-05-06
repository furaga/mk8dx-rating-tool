import cv2
import pandas as pd

from utils import OBS
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
    x2 = int(345 / 1920 * w)
    y1 = int(972 / 1080 * h)
    y2 = int(1032 / 1080 * h)
    ret, num = detect_number(img[y1:y2, x1:x2], False)
    if ret and 1 <= num <= max_lap:
        return ret, num
    return False, -1
