import os
from nicegui import ui
import tempfile

class ControlImage:
    def __init__(self) -> None:
        self.ready: bool = False
        self.tempDir = tempfile.TemporaryDirectory()
        ui.add_static_files("/static", "static")
        ui.add_static_files("/temp", self.tempDir.name)
        self.imageFile = None

    def uploadFile(self, e):
        with open(self.tempDir.name + "/test.png",mode="w+b") as fileImage:
            fileImage.write(e.files[0].content)
        self.ready = True

controlImage = ControlImage()

@ui.page("/rosenka2")
def pageRosenka2():
    ui.markdown(
        """
## 路線価図2
*****
    """
    )


@ui.page("/rosenka4")
def pageRosenka4():
    ui.markdown(
        """
## 路線価図4
*****
    """
    )


@ui.page("/test")
def pageTest():
    controlImage.ready = False
    ui.label("Hogeng")
    ui.upload(
        on_upload=controlImage.uploadFile, file_picker_label="Imokamo"
    )
    ui.image("/temp/test.png").bind_visibility(controlImage, "ready")


ui.markdown(
    """
# PDF Tools
*****
### 路線価図
"""
)
ui.link("２枚の路線価図をつなげる", pageRosenka2)
ui.link("４枚の路線価図をつなげる", pageRosenka4)

ui.markdown(
    """
# Test
*****
"""
)
ui.link("Test", pageTest)
ui.image("/static/tamashii.png").style('width:20%')
ui.label(controlImage.tempDir.name)

print(os.environ["PORT"])
ui.run(port=int(os.environ["PORT"]))
