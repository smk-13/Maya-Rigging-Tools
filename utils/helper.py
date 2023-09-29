from maya import cmds
from maya.api import OpenMaya



def convert_enum_names(enum_names: list):
    """ Turns the list ['A, 'B', 'C'] into the string 'A:B:C' """
    enum = ''
    for i in enum_names:
        enum += f'{i}:'
    return enum[:-1]


def create_even_parameter_list(number, max_num=1):
    """ Returns an evenly spaced parameter list from 0 to max_num,
        for exmaple: if number=5 and max_num=1, it returns [0, 0.25, 0.5, 0.75, 1] """
    if number < 2:
        cmds.error('Number should be at least 2.')
    return [max_num / (number - 1) * i for i in range(number)]


def select_by_root_joint():
    """ Returns the selected joint and all joints that sit below it in the hierarchy. """
    root = cmds.ls(sl=True, type='joint')[0]
    sel = cmds.listRelatives(root, ad=True, type='joint')
    sel.append(root)
    sel.reverse()
    return sel


