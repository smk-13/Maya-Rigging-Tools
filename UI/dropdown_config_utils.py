from maya import cmds
from maya.api import OpenMaya
import os
from importlib import reload
import json




CURRENT_DIRECTORY = os.path.dirname(__file__)
DROPDOWN_CONFIGS_PATH = os.path.abspath(f'{CURRENT_DIRECTORY}\\dropdown_configs')




curve_dropdown_dict = {
    'sphere': 'sphere',
    'box': 'box',
    'diamond': 'diamond',
    'brackets': 'brackets',
    'circleX': 'circleX',
    'circleY': 'circleY',
    'circleZ': 'cricleZ',
    'cricle pointer': 'circle_pointer',
    'square': 'square',
    'sledgehammer': 'slegdehammer',
    'rotate sphere': 'rotate_sphere',
    'arrow': 'arrow',
    'double arrow': 'double_arrow',
    'emblem': 'emblem',
    'three sided pyramide': 'three_sided_pyramide',
    'four sided pyramide': 'four_sided_pyramide',
    'circle cross arrow': 'circle_cross_arrow',
    'locator': 'locator',
    'pin': 'pin',
    'star': 'star'
}


def save_to_lib(data, file_name):
    """ This function can be used to initialize a dropdown config file. """
    path = os.path.join(DROPDOWN_CONFIGS_PATH, f'{file_name}.json')

    with open(path, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)
        OpenMaya.MGlobal.displayInfo('dropdown config successfully saved to library.')


def get_lib_data(file_name):
    """ returns the dropdown config data from a json file of the library. """
    path = os.path.join(DROPDOWN_CONFIGS_PATH, f'{file_name}.json')

    if os.path.isfile(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        cmds.error(f'The file {path} doesn\'t exist.')
