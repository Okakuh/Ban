from os import listdir, path
from pathlib import Path
from PyQt6.QtGui import QPixmap, QTransform, QPainter
from PyQt6.QtCore import Qt

from vars import *


def move_pattern(axis: str, where: int, parent) -> None:
    for kid in parent.chosen:
        kid.move_patternn(axis, where)


def create_png_for_banner_and_shield(user_pattern_banner: QPixmap,
                                     user_pattern_shield: QPixmap,
                                     save_banner_path: Path,
                                     save_shield_path: Path) -> None:
    save_banner_path = str(save_banner_path)
    save_shield_path = str(save_shield_path)

    png64_banner = QPixmap(64, 64)
    png64_banner.fill(Qt.GlobalColor.transparent)

    painter = QPainter(png64_banner)
    painter.drawPixmap(1, 1, QPixmap(user_pattern_banner))
    painter.drawPixmap(22, 1, QPixmap(user_pattern_banner.transformed(QTransform().scale(-1, 1))))
    painter.end()

    png64_banner.save(save_banner_path, "png", 100)

    png64_shield = QPixmap(64, 64)
    png64_shield.fill(Qt.GlobalColor.transparent)

    painter = QPainter(png64_shield)
    painter.drawPixmap(1, 1, QPixmap(user_pattern_shield))
    painter.end()

    png64_shield.save(save_shield_path, "png", 100)


def get_presets_name(folder: Path) -> dict:
    presets = {
        # "dp": None, "rp": None
    }
    if len(listdir(folder)) != 2:
        return presets

    presets_in_folder = listdir(folder)
    if not presets_in_folder[0].removesuffix(rp_key) == presets_in_folder[1].removesuffix(rp_key):
        return presets

    if presets_in_folder[0][-len(rp_key):] == rp_key:
        presets["rp"] = presets_in_folder[0]
        presets["dp"] = presets_in_folder[1]
    else:
        presets["dp"] = presets_in_folder[0]
        presets["rp"] = presets_in_folder[1]

    return presets


def find_folders_for_edit(save_folder: Path) -> dict:
    folders = {
        # "rp": "dp",
    }
    for i in listdir(save_folder):
        if Path(f"{save_folder}/{i}").is_dir():
            if len(i) >= len(rp_key) + 1:
                if i[-len(rp_key):] == rp_key:
                    folders[i] = ""

    if folders.keys():
        for resourecepack in folders.keys():
            if path.exists(f"{save_folder}/{resourecepack.removesuffix(rp_key)}"):
                folders[resourecepack] = resourecepack.removesuffix(rp_key)
            else:
                folders.pop(resourecepack)

    return folders


def make_unicode(text: str, symbols_not_to_convert: str) -> str:
    result = ""
    for char in text:
        if char not in symbols_not_to_convert:
            result += r'\u{:04X}'.format(ord(char))
        else:
            result += char
    return result
