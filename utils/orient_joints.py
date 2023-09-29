from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)


def orient_joint_chain(joint_chain=None, aim_vec=[1,0,0], up_vec=[0,0,1]):
    """ Orients the first three joints of joint chain, so that they are oriented perpendicular to
        the plane they define. Subsequent joints stay untoched. The axis that is perpendicular to
        the construction plane is neither the aim vector nor the up vector, but the third vector. """

    if joint_chain is None:
        joint_chain = utils.helper.select_by_root_joint()

    for n, jnt in enumerate(joint_chain):
        children = cmds.listRelatives(children=True)
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


def orient_single_joint(joint, aim_vec=[1,0,0], up_vec=[0,0,1]):
    """ """



