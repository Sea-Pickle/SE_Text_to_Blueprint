import string,colorsys,math,json,os
import PySimpleGUI as sg
from SE_blueprint_tools import blueprint_file, cube_grid 
from vector_class import vec3
CONFIG_FILE_PATH = "config.json"
DEFAULT_CONFIG = {
    "window_size":("350","450"),
    "rainbow_multipliers":("0.1","0.8","0.9"),
    "tab_length":"2",
    "blueprint_name":"Generated",
    "add_block_to_empty_lines":True
}
def generate_config_file(d):
    with open(CONFIG_FILE_PATH,"w") as f:
        f.write(json.dumps(d,indent=4))

if os.path.isfile(CONFIG_FILE_PATH):
    with open(CONFIG_FILE_PATH) as f:
        data = f.read()
        if data:
            config = json.loads(data)
        else:
            config = DEFAULT_CONFIG
            generate_config_file(DEFAULT_CONFIG)
else:
    config = DEFAULT_CONFIG
    generate_config_file(DEFAULT_CONFIG)
def config_value(name):
    return config.get(name,DEFAULT_CONFIG[name])
#==Config Values==#
WINDOW_SIZE = [int(i) for i in config_value("window_size")]
RAINBOW_MODE_MULTIPLIERS = [float(i) for i in config_value("rainbow_multipliers")]
TAB_LENGTH = int(config_value("tab_length"))
BLUEPRINT_NAME = config_value("blueprint_name")
ADD_BLOCK_TO_EMPTY_LINES = config_value("add_block_to_empty_lines")
#=====#
text = ""
fg_color = "a9a9a9"
bg_color = "222222"
use_rainbow_mode = False
selected_grid_size = "Small"
skin = "Weldless"
remove_sbcb5 = True
#=====#
FILE_TYPES = (("Text Files", "*.txt"),)
GRID_SIZES = ["Large","Small"]
DEFAULT_PROGRESS_BAR_COMPUTE = ('#000000', '#000000')
THEME_DICT ={
    "BACKGROUND": "#2c2c2c",
    "TEXT": "#ff2e6e",
    "INPUT": "#232323",
    "TEXT_INPUT": "#ff2e6e",
    "SCROLL": "#1c1c1c",
    "BUTTON": ("#df0080", "#323232"),
    "PROGRESS": DEFAULT_PROGRESS_BAR_COMPUTE,
    "BORDER": 1,
    "SLIDER_DEPTH": 0,
    "PROGRESS_DEPTH": 0,
    "ACCENT1": "#ff0000",
    "ACCENT2": "#00ffff",
    "ACCENT3": "#0000ff",
    }

sg.theme_add_new("gloop",THEME_DICT)
sg.theme("gloop")
layout = [
    [sg.Input(fg_color,key="fg_color",enable_events=True,size=(7,1)),sg.ColorChooserButton("Text Color"),],
    [sg.Input(bg_color,key="bg_color",enable_events=True,size=(7,1)),sg.ColorChooserButton("Background Color")],
    
    [sg.Frame("",[[sg.Text("Text Sample",key="sampletext",text_color="#"+fg_color,background_color="#"+bg_color)]],key="frame")],
    [sg.Checkbox("Rainbow Mode",key="rainbow_mode",enable_events=True,default=False),],
    [sg.Text("Grid Size"),sg.Listbox(GRID_SIZES,size=(5, 2),enable_events=True, key="grid_size",pad=10,no_scrollbar=True)],

    [sg.Multiline("",key="text_input",enable_events=True,size=(30,10)),sg.Text("uwu",text_color="#3f2a3a",pad=(12,0))],

    [
        sg.FileBrowse("Browse for file..",file_types=FILE_TYPES,enable_events=True,target="file_read"),
        sg.InputText(size=(1, 1), disabled=True,visible=False, enable_events=True, key="file_read")
    ],

    [sg.Button("Create Blueprint",key="create_bp")]
]



def gen_rainbow_color(n):
    hue = n*RAINBOW_MODE_MULTIPLIERS.x
    sat,val = RAINBOW_MODE_MULTIPLIERS[1:]
    color = vec3(colorsys.hsv_to_rgb(hue,sat,val))
    color = math.floor(color * 255)
    return color
def hex_to_rgb(h):
    return vec3([int(h[i : i + 2], 16) for i in range(0, 6, 2)])
CHAR_DICT = (
    
    {char: f"Symbol{char.upper()}" for char in string.ascii_letters} | 
    {char: f"Symbol{char}" for char in string.digits} |
    {
        "-": "SymbolHyphen",
        "_": "SymbolUnderscore",
        ".": "SymbolDot",
        ",": "SymbolApostrophe",
        "'": "SymbolApostrophe",
        "&": "SymbolAnd",
        ":": "SymbolColon",
        "!": "SymbolExclamationMark",
        "?": "SymbolQuestionMark",
        "<": "SymbolV",
        ">": "SymbolV",
    }
)
CHAR_ROTATION_DICT = {
    ",":[2,0],
    "<":[1,0],
    ">":[3,0]
}

def create_blueprint_from_text(text):
    print(fg_color,bg_color)
    fgcolor_bp = hex_to_rgb(fg_color)
    bgcolor_bp = hex_to_rgb(bg_color)
    bp = blueprint_file(name=BLUEPRINT_NAME)
    cg = cube_grid(bp,grid_size=selected_grid_size)
    cursor = vec3(0,0,0)
    index = 0
    lines = text.splitlines()
    for l_index,line in enumerate(lines):
        cursor.x = 0
        if 0<l_index<len(lines)-1 and ADD_BLOCK_TO_EMPTY_LINES:
            min_length = max(1,min(len(lines[l_index-1]),len(lines[l_index+1])))
            for i in range(min_length):
                cg.create_block(vec3(i,-1,cursor.z+1),bgcolor_bp)
        cursor.z +=1
        for char in line:
            if char=="\t":
                for _ in range(TAB_LENGTH):
                    cg.create_block(cursor-vec3(0,1,0),bgcolor_bp)
                    cursor.x += 1

            block_color = fgcolor_bp
            if use_rainbow_mode:
                block_color = gen_rainbow_color(index)

            block_type = CHAR_DICT.get(char,None)
            if block_type is not None:
                new_block = cg.create_block(cursor,block_color,type=block_type)
                index += 1

            if char in CHAR_ROTATION_DICT:
                new_block.set_rotation(CHAR_ROTATION_DICT[char])

            cg.create_block(cursor-vec3(0,1,0),bgcolor_bp)
            cursor.x += 1
            
    bp.save()

window = sg.Window("SE Text-to-Blueprint",layout,icon="Images\\icon.ico",size=WINDOW_SIZE)
while True:

    event, values = window.read()
    window.refresh()
    
    if event == sg.WINDOW_CLOSED:   
        break
    elif event == "text_input":
        text = values[event]

    elif event == "create_bp":
        create_blueprint_from_text(text)
    elif event == "fg_color":
        try:
            new_color = values[event].replace("#","")
            window["fg_color"].update(new_color)
            fg_color = new_color.ljust(6,"0")
            window["sampletext"].update(text_color="#"+(new_color.ljust(6,"0")))
        except Exception:
            pass
    elif event == "bg_color":
        try:
            new_color = values[event].replace("#","")
            window["bg_color"].update(new_color)
            bg_color = new_color.ljust(6,"0")
            window["sampletext"].update(background_color="#"+(new_color.ljust(6,"0")))
        except Exception:
            pass
    elif event == "rainbow_mode":
        use_rainbow_mode = values[event]
    elif event == "file_read":
        try:
            filename = values[event]
            with open(filename) as f:
                text = f.read()
                window["text_input"].update(text)
        except Exception:
            pass
    elif event=="grid_size":
        selection = values[event]
        if selection:
            selected_grid_size = selection[0]

