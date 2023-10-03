from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)




def joint_match_parent_freeze(name, pos, rot, parent):
    cmds.select(cl=True)
    jnt = cmds.joint(name=name, radius=1)
    cmds.matchTransform(jnt, pos, position=True)
    cmds.matchTransform(jnt, rot, rotation=True)
    cmds.parent(jnt, parent)
    cmds.makeIdentity(jnt, apply=True)
    return jnt


def create_inbetween_joints(base_name, roll_start, roll_end, parent, inbetween_count):
    """ """
    weights = utils.helper.create_even_parameter_list(number=inbetween_count+2)[1:-1]
    inv_weights = [1-w for w in weights]

    for n, (w, inv_w) in enumerate(zip(weights, inv_weights)):
        jnt = joint_match_parent_freeze(name=f'{base_name}_{n}', pos=roll_start, rot=roll_start, parent=parent)
        cmds.pointConstraint(roll_start, roll_end, jnt)
        cmds.pointConstraint(roll_start, jnt, edit=True, weight=inv_w)
        cmds.pointConstraint(roll_end, jnt, edit=True, weight=w)

        cnst = cmds.orientConstraint(roll_start, roll_end, jnt)[0]
        cmds.setAttr(f'{cnst}.interpType', 2)
        cmds.orientConstraint(roll_start, jnt, edit=True, weight=inv_w)
        cmds.orientConstraint(roll_end, jnt, edit=True, weight=w)


class RollBoneUpperArm:

    def __init__(self, side, shoulder, upperArm, forearm, inbetween_count=3):
        self.base_name = f'{side}_upperArm_roll'
        self.shoulder = shoulder
        self.upperArm = upperArm
        self.forearm = forearm 
        self.inbetween_count = inbetween_count
        self.aim_vec = [1,0,0] if side == 'L' else [-1,0,0]

        self.roll_start = joint_match_parent_freeze(name=f'{self.base_name}_start', pos=self.upperArm, rot=self.upperArm, parent=self.shoulder)
        cmds.aimConstraint(self.forearm, self.roll_start, worldUpType='none', aimVector=self.aim_vec)

        self.roll_end = joint_match_parent_freeze(name=f'{self.base_name}_end', pos=self.forearm, rot=self.upperArm, parent=self.roll_start)
        cmds.pointConstraint(self.forearm, self.roll_end)
        cmds.orientConstraint(self.upperArm, self.roll_end)

        create_inbetween_joints(base_name=self.base_name, roll_start=self.roll_start, roll_end=self.roll_end, parent=self.roll_start, inbetween_count=self.inbetween_count)


class RollBoneForearm:
    """ """

    def __init__(self, side, forearm, wrist, inbetween_count=3):
        self.base_name = f'{side}_forearm_roll'
        self.forearm = forearm
        self.wrist = wrist
        self.inbetween_count = inbetween_count
        self.aim_vec = [-1,0,0] if side == 'L' else [1,0,0]

        self.roll_end = joint_match_parent_freeze(name=f'{self.base_name}_end', pos=self.wrist, rot=self.forearm, parent=self.wrist)
        cmds.aimConstraint(self.forearm, self.roll_end, worldUpType='none', aimVector=self.aim_vec)

        create_inbetween_joints(base_name=self.base_name, roll_start=self.forearm, roll_end=self.roll_end, parent=self.wrist, inbetween_count=self.inbetween_count)


class RollBoneThigh:
    """ """

    def __init__(self, side, pelvis, hip, knee, inbetween_count=3):
        self.base_name = f'{side}_thigh_roll'
        self.pelvis = pelvis
        self.hip = hip
        self.knee = knee 
        self.inbetween_count = inbetween_count
        self.aim_vec = [1,0,0] if side == 'L' else [-1,0,0]

        self.roll_start = joint_match_parent_freeze(name=f'{self.base_name}_start', pos=self.hip, rot=self.hip, parent=self.pelvis)
        cmds.aimConstraint(self.knee, self.roll_start, worldUpType='none', aimVector=self.aim_vec)

        self.roll_end = joint_match_parent_freeze(name=f'{self.base_name}_end', pos=self.knee, rot=self.hip, parent=self.roll_start)
        cmds.pointConstraint(self.knee, self.roll_end)
        cmds.orientConstraint(self.hip, self.roll_end)

        create_inbetween_joints(base_name=self.base_name, roll_start=self.roll_start, roll_end=self.roll_end, parent=self.roll_start, inbetween_count=self.inbetween_count)


class RollBoneShin:
    """ """

    def __init__(self, side, knee, ankle, inbetween_count=3):
        self.base_name = f'{side}_shin_roll'
        self.knee = knee
        self.ankle = ankle
        self.inbetween_count = inbetween_count
        self.aim_vec = [-1,0,0] if side == 'L' else [1,0,0]

        self.roll_end = joint_match_parent_freeze(name=f'{self.base_name}_end', pos=self.ankle, rot=self.knee, parent=self.ankle)
        cmds.aimConstraint(self.knee, self.roll_end, worldUpType='none', aimVector=self.aim_vec)

        create_inbetween_joints(base_name=self.base_name, roll_start=self.knee, roll_end=self.roll_end, parent=self.ankle, inbetween_count=self.inbetween_count)
