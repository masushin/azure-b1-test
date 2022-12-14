from typing import Dict
from fire import Fire

from nicegui import ui

from PIL import Image, ImageDraw
from pathlib import Path
import fitz

INCH_MM = 25.4

CROP_AREA = {
    "id": (0, 150, 115, (150 + 275)),
    "id2": (3960, 150, (115 + 3960), 150 + 275),
    "note": (160, 70, (160 + 2620), (70 + 360)),
    "area": (2985, 170, (2985 + 450), (170 + 255)),
    "office": (3495, 258, (3495 + 402), (258 + 165)),
    "map": (8, 443, 4184 - 8, 3228),  # w = 4168
    "map_left": (8, 443, 2092, 3228),
    "map_right": (2092, 443, 4184 - 8, 3228),
    "map_top": (8, 443, 4184 - 8, 1836),
    "map_bottom": (8, 1836, 4184 - 8, 3228 - 4),
}

PASTE_POS = {
    "id": (8, 445),
    "id2": (4184 - 115 - 8, 445),
    "id_bottom": (8, 3228-4-275),
    "note": (160, 70),
    "area": (2985, 170),
    "office": (3495, 258),
    "map_left_top": (8, 443),
    "map_right_top": (2092, 443),
    "map_left_bottom": (8, 1836 - 5),
    "map_right_bottom": (2092, 1836 - 5),
}

RECT_POS = {
    "id": (8, 443, 115 + 8, 443 + 275),
    "id2": (4184 - 115 - 8, 443, 4184 - 8, 443 + 275),
    "id_bottom": (8, 3228 -4 - 275, 115 + 8, 3228-4),
    "map": (8, 443, 4184 - 8, 3228 - 4),
}

LINE_POS = {"v": (2092, 443, 2092, 4148), "h": (8, 1836 - 5, 4184 - 8, 1836 - 5)}


def getCropArea(dpi: int = 400, part: str = "all"):
    crop = {}
    for key in CROP_AREA:
        crop[key] = tuple(map(lambda x: int(x * (dpi / 400)), CROP_AREA[key]))

    if part == "all":
        return crop
    return crop[part]


def getRectPos(dpi: int = 400, part: str = "all"):
    rect = {}
    for key in RECT_POS:
        rect[key] = tuple(map(lambda x: int(x * (dpi / 400)), RECT_POS[key]))

    if part == "all":
        return rect
    return rect[part]


def getPastePosition(dpi: int = 400, part: str = "all"):
    pos = {}
    for key in PASTE_POS:
        pos[key] = tuple(map(lambda x: int(x * (dpi / 400)), PASTE_POS[key]))

    if part == "all":
        return pos
    return pos[part]


def getLinePosition(dpi: int = 400, part: str = "all"):
    line = {}
    for key in LINE_POS:
        line[key] = tuple(map(lambda x: int(x * (dpi / 400)), LINE_POS[key]))

    if part == "all":
        return line
    return line[part]


class RosenkaImage:
    def __init__(self, pdfFile: str, dpi=400) -> None:

        self.DPI = dpi
        self.CROP = getCropArea(dpi=dpi)

        filePath = Path(pdfFile)

        self.imagePart: Dict[str, Image.Image] = {}

        with fitz.open(filePath) as doc:
            self.page = doc.load_page(0)
            self.pixmap = self.page.get_pixmap(dpi=self.DPI)
            self.pilImage = Image.frombytes(
                mode="RGB",
                size=(self.pixmap.w, self.pixmap.h),
                data=self.pixmap.samples,
            )

        self.imagePart["all"] = self.pilImage.convert(mode="L")
        for key in getCropArea():
            self.imagePart[key] = self.pilImage.crop(box=getCropArea(dpi, key)).convert(
                mode="L"
            )


class RosenkaMergeHorizontal:
    def __init__(self, leftImageFile: str, rightImageFile: str, dpi=400) -> None:
        self.rosenkaImages: Dict[str, RosenkaImage] = {
            "left": RosenkaImage(leftImageFile, dpi=dpi),
            "right": RosenkaImage(rightImageFile, dpi=dpi),
        }
        self.image: Image = None

    def merge(self) -> Image:
        leftImage = self.rosenkaImages["left"]
        rightImage = self.rosenkaImages["right"]
        self.image = Image.new(mode="L", size=leftImage.pilImage.size, color=255)

        crop = getCropArea(leftImage.DPI, "all")
        paste = getPastePosition(leftImage.DPI, "all")

        self.image.paste(leftImage.pilImage.crop(crop["note"]), box=paste["note"])
        self.image.paste(leftImage.pilImage.crop(crop["office"]), box=paste["office"])
        self.image.paste(
            leftImage.pilImage.crop(crop["map_right"]), box=paste["map_left_top"]
        )
        self.image.paste(
            rightImage.pilImage.crop(crop["map_left"]), box=paste["map_right_top"]
        )
        self.image.paste(leftImage.pilImage.crop(crop["id"]), box=paste["id"])
        self.image.paste(leftImage.pilImage.crop(crop["id2"]), box=paste["id2"])
        draw = ImageDraw.ImageDraw(self.image)
        draw.rectangle(xy=getRectPos(leftImage.DPI, "id"), outline=0, width=2)
        draw.rectangle(xy=getRectPos(leftImage.DPI, "id2"), outline=0, width=2)
        draw.rectangle(xy=getRectPos(leftImage.DPI, "map"), outline=0, width=2)
        draw.line(xy=getLinePosition(leftImage.DPI, "v"), fill=200, width=1)
        return self.image


class RosenkaMergeVertical:
    def __init__(self, topImageFile: str, bottomImageFile: str, dpi=400) -> None:
        self.rosenkaImages: Dict[str, RosenkaImage] = {
            "top": RosenkaImage(topImageFile, dpi=dpi),
            "bottom": RosenkaImage(bottomImageFile, dpi=dpi),
        }
        self.image: Image = None

    def merge(self) -> Image:
        topImage = self.rosenkaImages["top"]
        bottomImage = self.rosenkaImages["bottom"]
        self.image = Image.new(mode="L", size=topImage.pilImage.size, color=255)

        crop = getCropArea(topImage.DPI, "all")
        paste = getPastePosition(topImage.DPI, "all")

        self.image.paste(topImage.pilImage.crop(crop["note"]), box=paste["note"])
        self.image.paste(topImage.pilImage.crop(crop["office"]), box=paste["office"])

        self.image.paste(
            topImage.pilImage.crop(crop["map_bottom"]), box=paste["map_left_top"]
        )
        self.image.paste(
            bottomImage.pilImage.crop(crop["map_top"]), box=paste["map_left_bottom"]
        )
        self.image.paste(topImage.pilImage.crop(crop["id"]), box=paste["id"])
        self.image.paste(bottomImage.pilImage.crop(crop["id2"]), box=paste["id_bottom"])
        draw = ImageDraw.ImageDraw(self.image)
        draw.rectangle(xy=getRectPos(topImage.DPI, "id"), outline=0, width=2)
        draw.rectangle(xy=getRectPos(topImage.DPI, "id_bottom"), outline=0, width=2)
        draw.rectangle(xy=getRectPos(topImage.DPI, "map"), outline=0, width=2)
        draw.line(xy=getLinePosition(topImage.DPI, "h"), fill=200, width=1)
        return self.image


class RosenkaMerge4:
    def __init__(self) -> None:
        pass


class Command(object):
    def mergeh(self, left: str, right: str, dpi: int = 400):
        rosenkaMerge = RosenkaMergeHorizontal(
            Path(left).absolute(), Path(right).absolute(), dpi=dpi
        )
        rosenkaMerge.merge().show()

    def mergev(self, top:str, bottom:str, dpi:int = 400):
        rosenkaMerge = RosenkaMergeVertical(
            Path(top).absolute(), Path(bottom).absolute(), dpi=dpi
        )
        rosenkaMerge.merge().show()


    def merge4(self):
        pass


if __name__ == "__main__":
    Fire(Command)
