import obswebsocket
import numpy as np
import cv2
from pathlib import Path
import os

obs_ws_ = None


def init(obs_pass):
    global obs_ws_
    obs_host = "localhost"
    obs_port = 4444
    obs_password = obs_pass
    obs_ws_ = obswebsocket.obsws(obs_host, obs_port, obs_password)
    obs_ws_.connect()


def set_browser_url(source_name: str, url: str):
    obs_ws_.call(
        obswebsocket.requests.SetSourceSettings(
            sourceName=source_name, sourceSettings={"url": url}
        )
    )


def set_visible(source_name: str, visible: bool):
    obs_ws_.call(
        obswebsocket.requests.SetSceneItemProperties(item=source_name, visible=visible)
    )


def set_text(source_name: str, new_text: str):
    obs_ws_.call(
        obswebsocket.requests.SetSourceSettings(
            sourceName=source_name, sourceSettings={"text": new_text}
        )
    )


def get_text(source_name: str):
    return obs_ws_.call(
        obswebsocket.requests.GetSourceSettings(sourceName=source_name)
    ).datain["sourceSettings"]["text"]


def capture_game_screen(sourceName: str = "映像キャプチャデバイス") -> np.ndarray:
    #    sourceName = "2023-05-05 15-15-03 - Trim.mkv"
    out_path = Path(os.getcwd()) / "__tmp__.jpg"
    obs_ws_.call(
        obswebsocket.requests.TakeSourceScreenshot(
            sourceName=sourceName,
            embedPictureFormat="jpg",
            saveToFilePath=str(out_path).replace("\\", "/"),
        )
    )
    img = cv2.imread(str(out_path))
    return img
