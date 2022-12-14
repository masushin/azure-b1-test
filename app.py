import os
from nicegui import ui

@ui.page('/rosenka2')
def pageRosenka2():
    ui.markdown('''
## 路線価図2
*****
    ''')

@ui.page('/rosenka4')
def pageRosenka4():
    ui.markdown('''
## 路線価図4
*****
    ''')

ui.markdown('''
# PDF Tools
*****
### 路線価図
''')
ui.link("２枚の路線価図をつなげる",pageRosenka2)
ui.link("４枚の路線価図をつなげる",pageRosenka4)

print(os.environ['PORT'])
ui.run(port=int(os.environ['PORT']))

