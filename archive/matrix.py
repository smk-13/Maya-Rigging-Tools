from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import om.utility
reload(om.utility)

import ctl.control
reload(ctl.control)







def zero_out_transform(transform_node):
    if cmds.objectType(transform_node, isType='joint'):
        cmds.joint(transform_node, edit=True, orientation=[0,0,0])
    cmds.xform(transform_node, os=True, m=list(OpenMaya.MMatrix()))
    cmds.setAttr(f'{transform_node}.inheritsTransform', 0)

def get_offset_matrix(transform1, transform2):
    mat1 = OpenMaya.MMatrix(cmds.xform(transform1, query=True, ws=True, matrix=True))
    mat2 = OpenMaya.MMatrix(cmds.xform(transform2, query=True, ws=True, matrix=True))
    mat2_inv = mat2.inverse()
    return list(mat1 * mat2_inv)


def create_aim_matrix(driven, input_transform, aim_transform, up_transform, aim_axis=[1,0,0], up_axis=[0,0,1], up_mode=2):
    """ For the eye, this needs an offset for the input_transform. This is very common. """

    am = cmds.createNode('aimMatrix', name=f'{driven}_AM')
    cmds.connectAttr(f'{input_transform}.worldMatrix[0]', f'{am}.inputMatrix')
    cmds.connectAttr(f'{aim_transform}.worldMatrix[0]', f'{am}.primaryTargetMatrix')
    cmds.connectAttr(f'{up_transform}.worldMatrix[0]', f'{am}.secondaryTargetMatrix')

    cmds.setAttr(f'{am}.primaryInputAxis', *aim_axis, type='double3')
    cmds.setAttr(f'{am}.secondaryInputAxis', *up_axis, type='double3')

    cmds.setAttr(f'{am}.secondaryMode', up_mode) # 1 is aim, and 2 is align

    cmds.connectAttr(f'{am}.outputMatrix', f'{driven}.offsetParentMatrix')
    zero_out_transform(driven)


def create_direct_matrix_constraint(driver, driven):
    cmds.connectAttr(f'{driver}.worldMatrix[0]', f'{driven}.offsetParentMatrix')
    zero_out_transform(driven)

def create_matrix_constraint_with_offset(driver, driven):
    offset_mat = get_offset_matrix(transform1=driven, transform2=driver)
    mult_mat_node = cmds.createNode('multMatrix', name=f'{driven}_offset_MMAT')
    cmds.setAttr(f'{mult_mat_node}.matrixIn[0]', offset_mat, type='matrix')
    cmds.connectAttr(f'{driver}.worldMatrix[0]', f'{mult_mat_node}.matrixIn[1]')
    cmds.connectAttr(f'{mult_mat_node}.matrixSum', f'{driven}.offsetParentMatrix')
    zero_out_transform(driven)

def create_blendmatrix(driven, input_transform, target_transform, target_transform_weights):
    """ target_transform_weights is a dict: {'translateWeight': 0, 'rotateWeight': 1, 'scaleWeight': 0} """
    bm = cmds.createNode('blendMatrix', name=f'{driven}_BM')
    cmds.connectAttr(f'{input_transform}.worldMatrix[0]', f'{bm}.inputMatrix')
    cmds.connectAttr(f'{target_transform}.worldMatrix[0]', f'{bm}.target[0].targetMatrix')
    for k, v in target_transform_weights.items():
        cmds.setAttr(f'{bm}.target[0].{k}', v)
    cmds.connectAttr(f'{bm}.outputMatrix', f'{driven}.offsetParentMatrix')
    zero_out_transform(driven)


