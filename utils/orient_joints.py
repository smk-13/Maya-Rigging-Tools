from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)


def orient_three_joints(joint_chain=None, aim_vec=[1,0,0], up_vec=[0,0,1]):
    """ Orients the first three joints of a joint chain, so that they are oriented perpendicular to
        the plane they define. Subsequent joints stay untouched. The axis that is perpendicular to
        the construction plane is neither the aim vector nor the up vector, but the third vector. """

    if joint_chain is None:
        joint_chain = utils.helper.select_by_root_joint()

    if len(joint_chain) < 3:
        cmds.error('joint chain must have a length of three joints.')

    for n, jnt in enumerate(joint_chain):
        children = cmds.listRelatives(jnt, children=True)
        if children:
            for child in children:
                cmds.parent(child, world=True)

        if n == 0:
            cnst = cmds.aimConstraint(joint_chain[n+1], jnt, worldUpType='object', aimVector=aim_vec,
                upVector=up_vec, worldUpObject=joint_chain[n+2], worldUpVector=up_vec, mo=False)[0]
            cmds.delete(cnst)
            cmds.makeIdentity(jnt, apply=True)
        elif n == 1:
            cnst = cmds.aimConstraint(joint_chain[n+1], jnt, worldUpType='object', aimVector=aim_vec,
                upVector=up_vec, worldUpObject=joint_chain[0], worldUpVector=up_vec, mo=False)[0]
            cmds.delete(cnst)
            cmds.makeIdentity(jnt, apply=True)
        elif n == 2:
            cmds.makeIdentity(jnt, apply=True)
            cmds.joint(jnt, edit=True, orientation=[0,0,0])

        if children:
            for child in children:
                cmds.parent(child, jnt)


def orient_single_joint(aim_vec=[1,0,0], up_vec=[0,0,1]):
    """ Orients a single joint with an aim object and an up object. Select the joint that will
    be oriented first, the aim object second, and the up object last. """

    sel = cmds.ls(sl=True, flatten=True)

    if cmds.objectType(sel[0])!='joint':
        cmds.error('The first object of the selection must be a joint.')

    children = cmds.listRelatives(sel[0], children=True)
    if children:
        for child in children:
            cmds.parent(child, world=True)

    cnst = cmds.aimConstraint(sel[1], sel[0], worldUpType='object', aimVector=aim_vec,
        upVector=up_vec, worldUpObject=sel[2], worldUpVector=up_vec, mo=False)[0]
    cmds.delete(cnst)
    cmds.makeIdentity(sel[0], apply=True)

    if children:
        for child in children:
            cmds.parent(child, sel[0])


# def orient_joint_chain(joint_chain=None, aim_vec=[1,0,0], up_vec=[0,0,1]):
#     """ right now, worldUpType is just set to None. Up_vec is not used. """
    
#     if joint_chain is None:
#         joint_chain = utils.helper.select_by_root_joint()

#     for n, jnt in enumerate(joint_chain):
#         children = cmds.listRelatives(jnt, children=True)
#         if children:
#             for child in children:
#                 cmds.parent(child, world=True)

#         if jnt == joint_chain[-1]:
#             cmds.makeIdentity(jnt, apply=True)
#             cmds.joint(jnt, edit=True, orientation=[0,0,0])
#         else:
#             cnst = cmds.aimConstraint(joint_chain[n+1], jnt, worldUpType='None', aimVector=aim_vec,
#                 worldUpVector=up_vec, mo=False)[0]
#             cmds.delete(cnst)
#             cmds.makeIdentity(jnt, apply=True)

#         if children:
#             for child in children:
#                 cmds.parent(child, jnt)

#     cmds.select(joint_chain[0])







