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



def get_creation_skeleton_data(joints=None):

    if joints is None:
        joints = utils.helper.select_by_root_joint()

    creation_data = list()

    for jnt in joints:

        cmds.makeIdentity(jnt, apply=True) # the rotation channel itself is not queried

        jnt_dict = dict()

        pos = cmds.xform(jnt, q=True, ws=True, translation=True)
        rot = cmds.xform(jnt, q=True, ws=True, rotation=True)
        segScaleComp = cmds.getAttr(f'{jnt}.segmentScaleCompensate')

        jnt_dict['position'] = pos
        jnt_dict['orientation'] = rot
        jnt_dict['name'] = jnt
        jnt_dict['scaleCompensate'] = segScaleComp

        creation_data.append(jnt_dict)

    return creation_data


def get_parent_jnt(joints=None):
    """ """

    if joints is None:
        joints = utils.helper.select_by_root_joint()

    parent_dict = dict()

    for jnt in joints:

        parent_jnt = cmds.listRelatives(jnt, parent=True)
        if parent_jnt:
            parent_jnt = parent_jnt[0]

        parent_dict[jnt] = parent_jnt

    return parent_dict


def get_preferred_angle(joints=None):
    """ """
    if joints is None:
        joints = utils.helper.select_by_root_joint()

    pa_dict = dict()

    for jnt in joints:
        pa =  cmds.getAttr(f'{jnt}.preferredAngle')

        pa_dict[jnt] = pa[0]

    return pa_dict


def collect_jnt_data(joints=None):
    """ This function combines the three functions above and stores the values in a dict, which
        can be unpacked in the create_joints function. """

    creation_data = get_creation_skeleton_data(joints)
    parent_data = get_parent_jnt(joints)
    prefAngle_data = get_preferred_angle(joints)

    skeleton_data = dict()

    skeleton_data['creation_data'] = creation_data
    skeleton_data['parent_data'] = parent_data
    skeleton_data['prefAngle_data'] = prefAngle_data

    return skeleton_data


def create_joints(creation_data, parent_data, prefAngle_data):
    """ """
    for data in creation_data:
        cmds.select(cl=True)
        cmds.joint(**data)

    for jnt, parent_jnt in parent_data.items():
        if parent_jnt:
            cmds.parent(jnt, parent_jnt)

    for jnt, pa in prefAngle_data.items():
        cmds.setAttr(f'{jnt}.preferredAngle', *pa)



### storing the data in json files

def save_to_lib(file_name, joints=None):
    """ """
    path = os.path.join(SKELETON_LIBRARY_PATH, f'{file_name}.json')

    with open(path, 'w') as f:
        skeleton_data = collect_jnt_data(joints=joints)
        json.dump(skeleton_data, f, indent=4, sort_keys=True)
        OpenMaya.MGlobal.displayInfo('Skeleton successfully saved to library.')

    # TO DO: override warning


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
    create_joints(**skeleton_data)



