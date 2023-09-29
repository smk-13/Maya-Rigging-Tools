from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)


def orient_joint_chain(joint_chain=None, aim_vec=[1,0,0], up_vec=[0,0,1]):
    """ """

    if joint_chain is None:
        joint_chain = utils.helper.select_by_root_joint()

    chain_len = len(joint_chain)

    for n, jnt in enumerate(joint_chain):
        children = cmds.listRelatives(children=True)
        if children:
            for child in children:
                cmds.parent(child, world=True)

        if n == chain_len-2:
            cnst = cmds.aimConstraint(joint_chain[n+1], jnt, worldUpType='object', aimVector=aim_vec, upVector=up_vec, worldUpObject=joint_chain[0], worldUpVector=up_vec, mo=False)[0]
            cmds.delete(cnst)
            cmds.makeIdentity(jnt, apply=True)
        elif n == chain_len-1:
            cmds.makeIdentity(jnt, apply=True)
            cmds.joint(jnt, edit=True, orientation=[0,0,0])
        else:
            cnst = cmds.aimConstraint(joint_chain[n+1], jnt, worldUpType='object', aimVector=aim_vec, upVector=up_vec, worldUpObject=joint_chain[n+2], worldUpVector=up_vec, mo=False)[0]
            cmds.delete(cnst)
            cmds.makeIdentity(jnt, apply=True)

        if children:
            for child in children:
                cmds.parent(child, jnt)


def orient_single_joint(joint, aim_vec=[1,0,0], up_vec=[0,0,1]):
    """ """



