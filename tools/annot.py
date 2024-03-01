from pathlib import Path

import matplotlib.pyplot as plt


class Annotate(object):
    def __init__(self, img_name, img_width, img_height):
        self.img_name = img_name
        self.img_width = img_width
        self.img_height = img_height
        self.ax = plt.gca()
        self.rect = plt.Rectangle(
            (0, 0), 1, 1, fill=False, edgecolor="red", linewidth=1
        )
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.is_press = False
        self.ax.add_patch(self.rect)
        self.ax.figure.canvas.mpl_connect("button_press_event", self.on_press)
        self.ax.figure.canvas.mpl_connect("button_release_event", self.on_release)
        self.ax.figure.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.ax.figure.canvas.mpl_connect("key_press_event", self.on_key)

    def on_press(self, event):
        print("press")
        self.is_press = True
        self.x0 = event.xdata
        self.y0 = event.ydata
        self.rect.set_width(1)
        self.rect.set_height(1)
        self.rect.set_xy((self.x0, self.y0))
        self.ax.figure.canvas.draw()

    def on_release(self, event):
        self.is_press = False
        if self.x0 is None or self.y0 is None:
            return
        #   if type(event.xdata) != float or type(event.ydata) != float:
        #      return
        inv = ax.transData.inverted()
        data_x, data_y = inv.transform([event.x, event.y])
        self.x1 = max(0, min(data_x, self.img_width))
        self.y1 = max(0, min(data_y, self.img_height))
        # print('release')
        self.rect.set_width(self.x1 - self.x0)
        self.rect.set_height(self.y1 - self.y0)
        self.rect.set_xy((self.x0, self.y0))
        self.ax.figure.canvas.draw()

    def on_motion(self, event):
        if self.x0 is None or self.y0 is None:
            return
        # if type(event.xdata) != float or type(event.ydata) != float:
        #     return
        inv = ax.transData.inverted()
        data_x, data_y = inv.transform([event.x, event.y])
        x1 = max(0, min(data_x, self.img_width))
        y1 = max(0, min(data_y, self.img_height))
        if self.is_press is True:
            self.rect.set_width(x1 - self.x0)
            self.rect.set_height(y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.ax.figure.canvas.draw()

    def on_key(self, event):
        if event.key == "enter":
            # text = f"{self.img_name},{int(self.x0)},{int(self.y0)},{int(self.x1)},{int(self.y1)}\n"
            # print(text, end="")
            if self.x0 > self.x1:
                self.x0, self.x1 = self.x1, self.x0
            if self.y0 > self.y1:
                self.y0, self.y1 = self.y1, self.y0
            text = f"{self.img_name},{int(self.x0)},{int(self.y0)},{int(self.x1)},{int(self.y1)}\n"
            print(text, end="")
            with open("crop.txt", "a", encoding="utf8") as f:
                f.write(text)


for img_path in list(Path("output_wave5/middle_frames").glob("*.jpg")):
    image = plt.imread(
        img_path
    )  # r"C:\Users\furag\Documents\prog\python\mk8dx-rating-tool\output_wave5\middle_frames\（716②）ぐつぐつハンバーグとビーチ！もう夏だね【マリオカート８DX】【リスナー参加型】【じゃむさん。】-RXRYkmqlzYg.jpg") # Enter your image path
    # image = np.random.rand(300,300)  # Random image for testing, replace this line
    fig, ax = plt.subplots()
    # fig.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)  # Add margins to the figure
    ax.imshow(image)
    print(image.shape)
    annotator = Annotate(img_path.stem, image.shape[1], image.shape[0])
    plt.show()
    plt.show()
