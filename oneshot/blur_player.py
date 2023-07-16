# import cv2
# from pathlib import Path

# img_dir = r"C:\Users\furag\Documents\doc\youtube\shorts\imgs\player_screens\original"

# players_roi1 = [
#     93 / 1920 + 0.01,
#     84 / 1080 + 0.01,
#     0.3,
#     870 / 1080 - 0.01,
# ]

# players_roi2 = [
#     0.51,
#     84 / 1080,
#     1827 / 1920 - 0.2,
#     870 / 1080 - 0.01,
# ]


# for img_path in Path(img_dir).glob("*.jpg"):
#     img = cv2.imread(str(img_path))
#     H, W = img.shape[:2]

#     for roi in [players_roi1, players_roi2]:
#         x1 = int(roi[0] * W)
#         y1 = int(roi[1] * H)
#         x2 = int(roi[2] * W)
#         y2 = int(roi[3] * H)
#         img[y1:y2, x1:x2] = cv2.GaussianBlur(img[y1:y2, x1:x2], (31, 31), 0)

#     cv2.imshow("img", img)
#     if ord("q") == cv2.waitKey(0):
#         break
#     cv2.imwrite(str(img_path.parent.parent / img_path.name), img)

vid_dict = {}

with open("../output_wave5/count_mirror_200cc_edit.csv", "r", encoding="utf8") as f:
    lines = f.readlines()
    for line in lines:
        tokens = line.strip().split(",")

        video_name = tokens[0].split("@")[0]
        if video_name not in vid_dict:
            vid_dict[video_name] = f"video{len(vid_dict):02d}"

        vid = vid_dict[video_name]

        row = [vid]
        if len(tokens) > 20:
            row += tokens[1:3]
            row += tokens[5:17]
        else:
            row += tokens[1:15]

        print(','.join(row))
