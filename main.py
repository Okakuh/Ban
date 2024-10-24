from os import listdir, path, walk, remove
from shutil import copytree
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QFileDialog, QVBoxLayout, QLabel,\
    QRadioButton, QDialog, QMessageBox
import sys
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QKeyEvent, QPainter
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from json import load, dump

from vars import *
from functions import *


class FolderSelectorApp(QDialog):
    foldersSelected = pyqtSignal(str, list)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Выбор папкок для изменения")

        self.selected_find_folder_path = None
        self.selected_rp_dp_folders = None

        layout = QVBoxLayout(self)

        # Метка для отображения выбранной папки
        self.selected_folder_label = QLabel("Выбранная папка: ", self)
        layout.addWidget(self.selected_folder_label)

        # Кнопка для выбора папки
        select_folder_button = QPushButton("Выбрать папку", self)
        select_folder_button.clicked.connect(self.select_folder_to_find_in)
        layout.addWidget(select_folder_button)

    def select_folder_to_find_in(self):
        self.selected_find_folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку с вашим "
                                                                                "ресурспаком и датапаком", "")
        if self.selected_find_folder_path:
            self.selected_folder_label.setText("Выбранная папка: " + self.selected_find_folder_path)
            self.show_found_folder()
            self.adjustSize()  # Автоматическое изменение размеров окна

    def show_found_folder(self):
        layout = self.layout()
        layout_item_count = layout.count()

        if layout_item_count > 2:  # Удаляем предыдущий список папок, если он был
            for i in reversed(range(2, layout_item_count)):
                layout_item = layout.itemAt(i)
                if layout_item.widget():
                    layout_item.widget().setParent(None)
                else:
                    layout.removeItem(layout_item)

        folders = find_folders_for_edit(self.selected_find_folder_path)

        if folders:
            folders_label = QLabel("Выберите один из вариантов:", self)
            layout.addWidget(folders_label)

            radio_button_list = []

            for rp_folder, dp_folder in folders.items():
                radio_button = QRadioButton(f"{rp_folder}\n{dp_folder}", self)
                radio_button_list.append(radio_button)
                layout.addWidget(radio_button)

            select_button = QPushButton("Выбрать", self)
            select_button.clicked.connect(lambda: self.get_chosen_folders(radio_button_list))
            layout.addWidget(select_button)
        else:
            no_folders_label = QLabel("Ничего не найдено в этой папке", self)
            layout.addWidget(no_folders_label)

    def get_chosen_folders(self, radio_button_list):
        selected_folder = None
        for radio_button in radio_button_list:
            if radio_button.isChecked():
                selected_folder = radio_button.text()
                break
        if selected_folder:
            self.selected_rp_dp_folders = selected_folder.split("\n")
            self.close()


class PatternRedactor(QPushButton):
    chosen = []
    all = []
    default_start_point = {"x": -1, "y": -1}

    def __init__(self, parent, maket_button: QPushButton, default_icon: Path, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        PatternRedactor.all.append(self)

        self._default_icon = str(default_icon)
        self.icon = self._default_icon

        self._icon_width = maket_button.iconSize().width()
        self._icon_height = maket_button.iconSize().height()

        self.temp_icon = QPixmap(self._default_icon)

        self.start_point = dict(PatternRedactor.default_start_point)

        self._maket_button = maket_button
        self.setAcceptDrops(True)
        self.setGeometry(maket_button.geometry())
        self.setIconSize(QSize(maket_button.iconSize().width(), maket_button.iconSize().height()))
        self.setStyleSheet(self._maket_button.styleSheet())

        self.set_icon(self.temp_icon)
        self.clicked.connect(self._toggle)

    def _toggle(self) -> None:
        if self not in PatternRedactor.chosen:
            PatternRedactor.chosen.append(self)
            self.setStyleSheet(pattern_redactor_style_chosen)
        else:
            PatternRedactor.chosen.remove(self)
            self.setStyleSheet(self._maket_button.styleSheet())

    def dragEnterEvent(self, event) -> None:

        if "file:///" in event.mimeData().text():
            if event.mimeData().text().replace('file:', '').split('///')[1].strip().split('.')[-1].lower() == 'png':
                event.accept()
                return
        event.ignore()

    def dropEvent(self, event) -> None:
        first_file = event.mimeData().text().replace('file:', '').split('///')[1].strip()

        for kid in PatternRedactor.all:
            kid.icon = str(Path(first_file))
            kid.start_point = dict(PatternRedactor.default_start_point)
            kid.temp_icon = self.new_temp_icon()
            kid.set_icon(self.temp_icon)

    def new_temp_icon(self) -> QPixmap:
        new_image = QPixmap(20, 40)
        new_image.fill(Qt.GlobalColor.transparent)

        painter = QPainter(new_image)
        painter.drawPixmap(self.start_point["x"], self.start_point["y"], QPixmap(self.icon))
        painter.end()

        return new_image

    def set_icon(self, icon: QPixmap) -> None:
        self.setIcon(QIcon(icon.scaled(self._icon_width, self._icon_height)))

    def clear_and_set_default(self) -> None:
        self.icon = self._default_icon
        self.temp_icon = QPixmap(self._default_icon)
        self.set_icon(self.temp_icon)

        self.start_point = dict(PatternRedactor.default_start_point)

    def move_patternn(self, axis: str, where: int) -> None:
        if self.icon != self._default_icon:
            self.start_point[axis] += where

            self.temp_icon = self.new_temp_icon()
            self.set_icon(self.temp_icon)

    def has_pattern(self) -> bool:
        return self.icon != self._default_icon

    def get_pattern(self) -> QPixmap:
        return self.temp_icon


class BanAdder(QWidget):
    def __init__(self):
        super().__init__()
        self.folder_selector = None
        #  Настройки окна
        if True:
            self.ui = uic.loadUi(program_ui, self)
            self.setWindowTitle(f"{program_name} {program_version}")

            self.setMinimumSize(self.ui.geometry().width(), self.ui.geometry().height())
            self.setMaximumSize(self.ui.geometry().width(), self.ui.geometry().height())

        # Кнопки-редакторы. PatternRedactors
        if True:
            self.pattern_bunner = PatternRedactor(self,
                                                  self.maket_banner,
                                                  Path(f'{program_icons}user_pattern_empty.png'))

            self.pattern_shield = PatternRedactor(self,
                                                  self.maket_shield,
                                                  Path(f'{program_icons}user_pattern_empty.png'))
        # Buttons.clicked.connect
        if True:
            self.button_move_up.clicked.connect(lambda: move_pattern("y", -1, PatternRedactor))
            self.button_move_down.clicked.connect(lambda: move_pattern("y", 1, PatternRedactor))
            self.button_move_right.clicked.connect(lambda: move_pattern("x", 1, PatternRedactor))
            self.button_move_left.clicked.connect(lambda: move_pattern("x", -1, PatternRedactor))

            self.button_clear.clicked.connect(self.clear_everything)
            self.button_edit_previous.clicked.connect(self.edit_existed)
            self.button_create.clicked.connect(self.create_new)

        self.display_name.textEdited.connect(self.display_name_changed)
        self.id_name.textEdited.connect(self.id_name_changed)

    def create_new(self) -> None:
        save_folder = QFileDialog.getExistingDirectory(self, 'Выберите папку')
        if not save_folder:
            return

        folders = get_presets_name(Path(program_presets))

        if not folders:
            QMessageBox.critical(self, "Ошибка в пресетах!", f"Что-то не так с пресетами!",
                                 QMessageBox.StandardButton.Ok)
            return

        for preset_name in listdir(program_presets):
            if path.exists(f"{save_folder}/{preset_name}"):
                QMessageBox.critical(self,
                                     'Ошибка',
                                     f"Файл '{save_folder}/{preset_name}' уже существует.",
                                     QMessageBox.StandardButton.Ok)
                return

        for preset_name in listdir(program_presets):
            preset_path = f"{program_presets}{preset_name}"
            copytree(preset_path, f"{save_folder}/{preset_name}")

        self.start({"rp": f"{save_folder}/{folders['rp']}", "dp": f"{save_folder}/{folders['dp']}"})

    def display_name_changed(self) -> None:
        text = self.display_name.text()
        text = text.replace("\\", "").replace("№", "").replace("?", "").replace("§", "")
        self.display_name.setText(text)

    def id_name_changed(self) -> None:
        text: str = self.id_name.text()
        text = text.replace(" ", "_")
        text = text.lower()
        for char in text:
            if char not in "qwertyuiopasdfghjklzxcvbnm_":
                text = text.replace(char, "")
        self.id_name.setText(text)

    def clear_everything(self) -> None:
        for kid in PatternRedactor.all:
            kid.clear_and_set_default()

        self.author.setText("")
        self.display_name.setText("")
        self.id_name.setText("")


    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()

        if key == ord('A') or key == ord('Ф') or key == ord('Ф'):
            move_pattern("x", -1, PatternRedactor)
        elif key == ord('D') or key == ord('В') or key == ord('В'):
            move_pattern("x", 1, PatternRedactor)
        elif key == ord('W') or key == ord('Ц') or key == ord('Ц'):
            move_pattern("y", -1, PatternRedactor)
        elif key == ord('S') or key == ord('Ы') or key == ord('І'):
            move_pattern("y", 1, PatternRedactor)

    def edit_existed(self):
        self.folder_selector = FolderSelectorApp()
        self.folder_selector.exec()

        if not self.folder_selector.selected_rp_dp_folders or not self.folder_selector.selected_find_folder_path:
            return

        selected_folder = self.folder_selector.selected_find_folder_path
        rp_folder = self.folder_selector.selected_rp_dp_folders[0]
        dp_folder = self.folder_selector.selected_rp_dp_folders[1]

        self.start({"rp": f"{selected_folder}/{rp_folder}", "dp": f"{selected_folder}/{dp_folder}"})

    def start(self, rp_dp_folders: dict):
        author = self.author.text()
        display_name = make_unicode(self.display_name.text(), unicode_convertor_ignore)
        id_name = self.id_name.text()
        patern_item = self.pattern_item.currentText()

        # --------------------------------------------------------------------------------------------------------
        # -----------------------------------------   Resource Pack   --------------------------------------------
        # --------------------------------------------------------------------------------------------------------

        if author != "":
            with open(file=f"{rp_dp_folders['rp']}/ATTRIBUTIONS.md", mode="a", encoding="utf-8") as fl:
                fl.write("\n\n")
                fl.write(f"-banner/{id_name}.png\n"
                         f"   -{author}\n\n"
                         f"-shield/{id_name}.png\n"
                         f"   -{author}")

        colors = {
            "black": "Black",
            "blue": "Blue",
            "brown": "Brown",
            "cyan": "Cyan",
            "gray": "Gray",
            "green": "Green",
            "light_blue": "Light Blue",
            "light_gray": "Light Gray",
            "lime": "Lime",
            "magenta": "Magenta",
            "orange": "Orange",
            "pink": "Pink",
            "purple": "Purple",
            "red": "Red",
            "white": "White",
            "yellow": "Yellow",
        }

        if id_name != "":
            with open(file=f"{rp_dp_folders['rp']}/assets/mmb/lang/en_us.json", mode="r", encoding="utf-8") as fl:
                fl = load(fl)
                for color_id, color_display in colors.items():
                    fl[f'block.minecraft.banner.mmb.{id_name}.{color_id}'] = f"{color_display} {display_name}"

            with open(file=f"{rp_dp_folders['rp']}/assets/mmb/lang/en_us.json", mode="w", encoding="utf-8") as sett:
                dump(fl, sett, indent=3)

        if self.pattern_bunner.has_pattern() and self.pattern_shield.has_pattern() and id_name != "":
            png_for_banner = f"{rp_dp_folders['rp']}/assets/mmb/textures/entity/banner/{id_name}.png"
            png_for_sheild = f"{rp_dp_folders['rp']}/assets/mmb/textures/entity/shield/{id_name}.png"

            create_png_for_banner_and_shield(self.pattern_bunner.get_pattern(),
                                             self.pattern_shield.get_pattern(),
                                             Path(png_for_banner),
                                             Path(png_for_sheild)
                                             )

        # --------------------------------------------------------------------------------------------------------
        # -------------------------------------------   Data Pack   ----------------------------------------------
        # --------------------------------------------------------------------------------------------------------
        if author != "":
            with open(file=f"{rp_dp_folders['dp']}/ATTRIBUTIONS.md", mode="a", encoding="utf-8") as fl:
                fl.write("\n\n")
                fl.write(f"-banner/{id_name}.png\n"
                         f"   -{author}\n\n"
                         f"-shield/{id_name}.png\n"
                         f"   -{author}")

        if id_name != "":
            patern_item_path = f"{rp_dp_folders['dp']}/" \
                               f"data/minecraft/tags/banner_pattern/pattern_item/{patern_item}.json"
            with open(file=patern_item_path, mode="r", encoding="utf-8") as fl:
                fl = load(fl)
                fl["values"].append(f"mmb:{id_name}")

            with open(file=patern_item_path, mode="w", encoding="utf-8") as sett:
                dump(fl, sett, indent=3)

            qwe = f"{rp_dp_folders['dp']}/data/mmb/banner_pattern/{id_name}.json"

            d = {"asset_id": f"mmb:{id_name}",
                 "translation_key": f"block.minecraft.banner.mmb.{id_name}"}

            with open(file=qwe, mode="w", encoding="utf-8") as sett2:
                dump(d, sett2, indent=3)


def main() -> None:
    app = QApplication(sys.argv)
    banadder = BanAdder()
    banadder.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
