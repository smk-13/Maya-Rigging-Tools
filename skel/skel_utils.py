from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload
import os
import json

import utils.helper
reload(utils.helper)

CURRENT_DIRECTORY = os.path.dirname(__file__)
SKELETON_LIBRARY_PATH = os.path.abspath(f'{CURRENT_DIRECTORY}\\skeletons')




def get_skeleton_data(joints=None):
    """ """

    if joints is None:
        joints = cmds.ls(sl=True, type='joint')

    skel_data = list()

    for jnt in joints:

        cmds.makeIdentity(jnt, apply=True) # the rotation channel itself is not used

        jnt_dict = dict()

        # on creation data
        pos = cmds.xform(jnt, q=True, ws=True, translation=True)
        rot = cmds.xform(jnt, q=True, ws=True, rotation=True)
        scaleCompensate = cmds.getAttr(f'{jnt}.segmentScaleCompensate')
        radius = cmds.getAttr(f'{jnt}.radius')

        jnt_dict['name'] = jnt
        jnt_dict['position'] = pos
        jnt_dict['orientation'] = rot
        jnt_dict['scaleCompensate'] = scaleCompensate
        jnt_dict['radius'] = radius

        # rotate order
        roo_index = cmds.getAttr(f'{jnt}.rotateOrder')
        roo_list = ['xyz', 'yzx', 'zxy', 'zyx', 'yxz', 'xzy']
        jnt_dict['rotationOrder'] = roo_list[roo_index]

        # parent
        parent_jnt = cmds.listRelatives(jnt, parent=True)
        if parent_jnt:
            parent_jnt = parent_jnt[0]
        jnt_dict['parent'] = parent_jnt

        # preferred Angle
        pa =  cmds.getAttr(f'{jnt}.preferredAngle')
        jnt_dict['preferredAngle'] = pa[0]

        skel_data.append(jnt_dict)

    return skel_data


def create_from_skeleton_data(skeleton_data):
    """ """

    # prevent name clashing
    jnt_names = [jnt_dict['name'] for jnt_dict in skeleton_data]
    for jnt in jnt_names:
        if cmds.objExists(jnt):
            OpenMaya.MGlobal.displayInfo('stopped, because at least one joint with a specified name already exists.')
            cmds.error()

    creation_data_keys = ['position', 'orientation', 'name', 'scaleCompensate', 'radius',
        'rotationOrder']

    for jnt_dict in skeleton_data:
        creation_dict = {key:value for key, value in jnt_dict.items() if key in creation_data_keys}
        cmds.select(cl=True)
        jnt = cmds.joint(**creation_dict)

    for jnt_dict in skeleton_data:
        if jnt_dict['parent']:
            try:
                cmds.parent(jnt_dict['name'], jnt_dict['parent'])  # try except block because the parent may not exist
            except:
                pass

        cmds.setAttr(f'{jnt}.preferredAngle', *jnt_dict['preferredAngle'])



def save_to_lib(file_name, joints=None):
    """ """
    path = os.path.join(SKELETON_LIBRARY_PATH, f'{file_name}.json')

    # overwrite warning
    if utils.helper.validate_path(path) == 0:
        return

    skeleton_data = get_skeleton_data(joints=joints)

    with open(path, 'w') as f:
        json.dump(skeleton_data, f, indent=4, sort_keys=True)
        OpenMaya.MGlobal.displayInfo('Skeleton successfully saved to library.')



def load_from_lib(file_name):
    """ """
    path = os.path.join(SKELETON_LIBRARY_PATH, f'{file_name}.json')

    if os.path.isfile(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        cmds.error(f'The file {path} doesn\'t exist.')


def create_skeleton_from_lib(file_name):
    """ """
    skeleton_data = load_from_lib(file_name=file_name)
    create_from_skeleton_data(skeleton_data)



