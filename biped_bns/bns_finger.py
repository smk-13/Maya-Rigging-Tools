from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload


import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)

import utils.matrix
reload(utils.matrix)






class Finger:
    """ Primitive, but I think this is good enough... the other version is very complicated. """


    def __init__(self, side, color):
        """ """
        self.side = side
        self.thumb_chain = [f'{side}_thumb{n}_jnt' for n in range(3)]
        self.index_chain = [f'{side}_index{n}_jnt' for n in range(4)]
        self.middle_chain = [f'{side}_middle{n}_jnt' for n in range(4)]
        self.ring_chain = [f'{side}_ring{n}_jnt' for n in range(4)]
        self.pinky_chain = [f'{side}_pinky{n}_jnt' for n in range(4)]
        self.wrist = f'{side}_wrist_jnt'
        self.master = 'master2_ctl'

        # self.ctl_dict = {
        #     'knuckle': {'shape': 'bone1', 'scale': 1.1, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'ry'], 'offsets': ['grp', 'buffer']},
        #     'meta': {'shape': 'meta', 'scale': 2.4, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz'], 'offsets': ['grp', 'buffer']},
        #     'small_thumb': {'shape': 'bone2', 'scale': 1, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'ry'], 'offsets': ['grp', 'buffer']},
        #     'big_thumb': {'shape': 'bone3', 'scale': 1, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'offsets': ['grp', 'buffer']},
        # }


        self.ctl_dict = {
            'knuckle': {'shape': 'bone1', 'scale': 1.1, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'ry'], 'offsets': ['grp', 'buffer']},
            'meta': {'shape': 'meta', 'scale': 2.4, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz'], 'offsets': ['grp', 'buffer']},
            'small_thumb': {'shape': 'bone2', 'scale': 1, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'ry'], 'offsets': ['grp', 'buffer']},
            'big_thumb': {'shape': 'bone3', 'scale': 1, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'offsets': ['grp', 'buffer']},
        }

        self.main()



    def main(self):
        """ """

        self.wrist_null = cmds.createNode('transform', name=f'{self.side}_wrist_null', parent=self.master)
        cmds.matchTransform(self.wrist_null, self.wrist)
        cmds.parentConstraint(self.wrist, self.wrist_null, mo=True)

        cmds.parent(self.thumb_chain[0], self.wrist_null)
        cmds.parent(self.index_chain[0], self.wrist_null)
        cmds.parent(self.middle_chain[0], self.wrist_null)
        cmds.parent(self.ring_chain[0], self.wrist_null)
        cmds.parent(self.pinky_chain[0], self.wrist_null)

        self.fk_script(joint_chain=self.thumb_chain, parent=self.wrist_null)
        self.fk_script(joint_chain=self.index_chain, parent=self.wrist_null)
        self.fk_script(joint_chain=self.middle_chain, parent=self.wrist_null)
        self.fk_script(joint_chain=self.ring_chain, parent=self.wrist_null)
        self.fk_script(joint_chain=self.pinky_chain, parent=self.wrist_null)


    def fk_script(self, joint_chain, parent=None):
        has_parent = parent
        for jnt in joint_chain:

            if jnt in [self.index_chain[0], self.middle_chain[0], self.ring_chain[0], self.pinky_chain[0]]:
                ctlObj = ctl.ctrl.Control(base_name=jnt.replace('_jnt', ''), target=jnt, **self.ctl_dict['meta'])
            elif jnt == self.thumb_chain[1]:
                ctlObj = ctl.ctrl.Control(base_name=jnt.replace('_jnt', ''), target=jnt, **self.ctl_dict['small_thumb'])
            elif jnt == self.thumb_chain[0]:
                ctlObj = ctl.ctrl.Control(base_name=jnt.replace('_jnt', ''), target=jnt, **self.ctl_dict['big_thumb'])
            else:
                ctlObj = ctl.ctrl.Control(base_name=jnt.replace('_jnt', ''), target=jnt, **self.ctl_dict['knuckle'])

            ctlObj.mirror_if_right_side()
            cmds.parentConstraint(ctlObj.ctrl, jnt)
            if has_parent:
                cmds.parent(ctlObj.grp, has_parent)
            has_parent = ctlObj.ctrl











class Finger_v1:
    """ WIP """


    def __init__(self, side, color):
        """ """
        self.side = side
        self.thumb_chain = [f'{side}_thumb{n}_jnt' for n in range(4)]
        self.index_chain = [f'{side}_index{n+1}_jnt' for n in range(3)]  # exception: the first one is not used
        self.middle_chain = [f'{side}_middle{n}_jnt' for n in range(4)]
        self.ring_chain = [f'{side}_ring{n}_jnt' for n in range(4)]
        self.pinky_chain = [f'{side}_pinky{n}_jnt' for n in range(4)]
        self.wrist = f'{side}_wrist_jnt'

        self.ctl_dict = {
            'knuckle': {'shape': 'bone1', 'scale': 0.6, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'offsets': ['grp']},
            'ROOT': {'shape': 'cube', 'scale': 2, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'offsets': ['grp']},
            'ROT': {'shape': 'sphere', 'scale': 2, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz'], 'offsets': ['grp']},
            'TRN': {'shape': 'cube', 'scale': 0.25, 'color': color, 'hidden_attrs':['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz', 'ty'], 'offsets': ['grp']}
        }


        self.finger_controller_layout()
        self.create_finger_expression()
        

    def fk_script(self, joint_chain, parent=None):
        """ not so simple...but I don't have a better idea right now. """
        has_parent = parent
        for jnt in joint_chain:
            ctlObj = ctl.ctrl.Control(base_name=jnt.replace('_jnt', ''), target=jnt, **self.ctl_dict['knuckle'])

            # this is the inelegant part
            if jnt in [f'{self.side}_{label}0_jnt' for label in ('thumb','middle', 'ring', 'pinky')]:
                cmds.xform(ctlObj.grp, os=True, r=True, t=[3,-1,0])

            ctlObj.mirror_if_right_side()
            if has_parent:
                cmds.parent(ctlObj.grp, has_parent)
            has_parent = ctlObj.ctrl


    def finger_controller_layout(self):

        self.fk_script(joint_chain=self.thumb_chain, parent=self.wrist)
        self.fk_script(joint_chain=self.index_chain, parent=f'{self.side}_thumb0_ctl')
        self.fk_script(joint_chain=self.middle_chain, parent=f'{self.side}_thumb0_ctl')
        self.fk_script(joint_chain=self.ring_chain, parent=f'{self.side}_thumb0_ctl')
        self.fk_script(joint_chain=self.pinky_chain, parent=f'{self.side}_thumb0_ctl')

        self.ROTCtlObj = ctl.ctrl.Control(base_name=f'{self.side}_finger_ROT', target=f'{self.side}_thumb0_ctl', parent=f'{self.side}_thumb0_ctl', **self.ctl_dict['ROT'])
        cmds.xform(self.ROTCtlObj.grp, os=True, r=True, t=[0,-6,1])
        self.ROTCtlObj.mirror_if_right_side()
        self.TRNCtlObj = ctl.ctrl.Control(base_name=f'{self.side}_finger_TRN', target=self.ROTCtlObj.ctrl, parent=self.ROTCtlObj.ctrl, **self.ctl_dict['TRN'])
        self.TRNCtlObj.mirror_if_right_side()

        if self.side == 'L':  # because of how I wrote the mirror script, the right side inherits this from the left side
            cmds.xform(f'{self.side}_thumb0_grp', os=True, r=True, t=[0,-2,0])
            cmds.xform(f'{self.side}_thumb1_grp', os=True, r=True, t=[0,-2,-2])




    def create_finger_expression(self):
        """ This is the full expression version based on the original BNS setup. Technically, this is a little bit messy, but works just fine and it's fast. """

        self.finger_exp = cmds.expression(name=f'{self.side}_finger_EXP', s=f"""

            $rtrn_tz  = 0.1  * {self.TRNCtlObj.ctrl}.translateZ + 1.0;
            $rtrn_mtz = 0.035* {self.TRNCtlObj.ctrl}.translateZ + 1.0;
            $rtrn_bx  = 0.1  * {self.TRNCtlObj.ctrl}.translateX + 1.0;
            $rtrn_rtz = 2.0 - $rtrn_tz;
            $rtrn_rmtz= 2.0 - $rtrn_mtz;


            // THUMB
            {self.side}_thumb0_jnt.rotateX = {self.side}_thumb0_ctl.rotateX;  // root ctrl
            {self.side}_thumb0_jnt.rotateY = {self.side}_thumb0_ctl.rotateY;  // root ctrl
            {self.side}_thumb0_jnt.rotateZ = {self.side}_thumb0_ctl.rotateZ;  // root ctrl

            {self.side}_thumb1_offset.rotateX = - {self.ROTCtlObj.ctrl}.rotateX;  // this offset is needed because of the different orientation

            {self.side}_thumb1_jnt.rotateX = {self.side}_thumb1_ctl.rotateX;
            {self.side}_thumb1_jnt.rotateY = {self.side}_thumb1_ctl.rotateY;
            {self.side}_thumb1_jnt.rotateZ = {self.side}_thumb1_ctl.rotateZ;
            {self.side}_thumb2_jnt.rotateZ = {self.side}_thumb2_ctl.rotateZ;
            {self.side}_thumb3_jnt.rotateZ = {self.side}_thumb3_ctl.rotateZ;

            // INDEX
            {self.side}_index1_jnt.rotateX = {self.side}_index1_ctl.rotateX;
            {self.side}_index1_jnt.rotateY = {self.side}_index1_ctl.rotateY - 0.8 * {self.ROTCtlObj.ctrl}.rotateY;
            {self.side}_index1_jnt.rotateZ = {self.side}_index1_ctl.rotateZ + 0.95 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_tz * $rtrn_bx;
            {self.side}_index2_jnt.rotateZ = {self.side}_index2_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_tz;
            {self.side}_index3_jnt.rotateZ = {self.side}_index3_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_tz * ( 2 - $rtrn_bx * 0.95 );

            // MIDDLE
            {self.side}_middle0_jnt.rotateX = {self.side}_middle0_ctl.rotateX + 0.2 * {self.ROTCtlObj.ctrl}.rotateX;
            {self.side}_middle0_jnt.rotateY = {self.side}_middle0_ctl.rotateY + 0.25 * {self.ROTCtlObj.ctrl}.rotateY;
            {self.side}_middle0_jnt.rotateZ = {self.side}_middle0_ctl.rotateZ + 0.05 * {self.ROTCtlObj.ctrl}.rotateZ;

            {self.side}_middle1_jnt.rotateX = {self.side}_middle1_ctl.rotateX;
            {self.side}_middle1_jnt.rotateY = {self.side}_middle1_ctl.rotateY;
            {self.side}_middle1_jnt.rotateZ = {self.side}_middle1_ctl.rotateZ + 0.95 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_mtz * $rtrn_bx;
            {self.side}_middle2_jnt.rotateZ = {self.side}_middle2_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_mtz;
            {self.side}_middle3_jnt.rotateZ = {self.side}_middle3_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_mtz * ( 2 - $rtrn_bx * 0.95 );

            // RING
            {self.side}_ring0_jnt.rotateX = {self.side}_ring0_ctl.rotateX - {self.side}_middle0_ctl.rotateX + 0.2 * {self.ROTCtlObj.ctrl}.rotateX;  // counterrotation
            {self.side}_ring0_jnt.rotateY = {self.side}_ring0_ctl.rotateY - {self.side}_middle0_ctl.rotateY + 0.2 * {self.ROTCtlObj.ctrl}.rotateY;  // counterrotation
            {self.side}_ring0_jnt.rotateZ = {self.side}_ring0_ctl.rotateZ - {self.side}_middle0_ctl.rotateZ + 0.1 * {self.ROTCtlObj.ctrl}.rotateZ;  // counterrotation

            {self.side}_ring1_jnt.rotateX = {self.side}_ring1_ctl.rotateX - 0.1 * {self.ROTCtlObj.ctrl}.rotateX;
            {self.side}_ring1_jnt.rotateY = {self.side}_ring1_ctl.rotateY + 0.9 * {self.ROTCtlObj.ctrl}.rotateY;
            {self.side}_ring1_jnt.rotateZ = {self.side}_ring1_ctl.rotateZ + 0.95 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_rmtz * $rtrn_bx;
            {self.side}_ring2_jnt.rotateZ = {self.side}_ring2_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_rmtz;
            {self.side}_ring3_jnt.rotateZ = {self.side}_ring3_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_rmtz * ( 2 - $rtrn_bx * 0.95 );

            // PINKY
            {self.side}_pinky0_jnt.rotateX = {self.side}_pinky0_ctl.rotateX - {self.side}_ring0_ctl.rotateX + 0.4 * {self.ROTCtlObj.ctrl}.rotateX;  // counterrotation
            {self.side}_pinky0_jnt.rotateY = {self.side}_pinky0_ctl.rotateY - {self.side}_ring0_ctl.rotateY + 0.3 * {self.ROTCtlObj.ctrl}.rotateY;  // counterrotation
            {self.side}_pinky0_jnt.rotateZ = {self.side}_pinky0_ctl.rotateZ - {self.side}_ring0_ctl.rotateZ - 0.15 * {self.ROTCtlObj.ctrl}.rotateX;  // counterrotation

            {self.side}_pinky1_jnt.rotateX = {self.side}_pinky1_ctl.rotateX - 0.3 * {self.ROTCtlObj.ctrl}.rotateX;
            {self.side}_pinky1_jnt.rotateY = {self.side}_pinky1_ctl.rotateY + 2.2 * {self.ROTCtlObj.ctrl}.rotateY;
            {self.side}_pinky1_jnt.rotateZ = {self.side}_pinky1_ctl.rotateZ + 0.95 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_rtz * $rtrn_bx;
            {self.side}_pinky2_jnt.rotateZ = {self.side}_pinky2_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_rtz;
            {self.side}_pinky3_jnt.rotateZ = {self.side}_pinky3_ctl.rotateZ + 1.0 * {self.ROTCtlObj.ctrl}.rotateZ * $rtrn_rtz * ( 2 - $rtrn_bx * 0.95 );


            """)


            # reference

            # $rtrn_tz  = 0.1  * finger_ratio_L_TRN.translateZ + 1.0;
            # $rtrn_mtz = 0.035* finger_ratio_L_TRN.translateZ + 1.0;
            # $rtrn_bx  = 0.1  * finger_ratio_L_TRN.translateX + 1.0;
            # $rtrn_rtz = 2.0 - $rtrn_tz;
            # $rtrn_rmtz= 2.0 - $rtrn_mtz;

            # l_thumb_chn.jointOrientX = 53.1051;
            # l_thumb_chn.jointOrientY = 0;
            # l_thumb_chn.jointOrientZ = 0;

            # l_thumb_chn.rotateX  = finger_base_L_ROT.rotateX;
            # l_thumb3_jnt.rotateX = -L_Thumb1.rotateX;
            # l_thumb3_jnt.rotateY = L_Thumb1.rotateY;
            # l_thumb3_jnt.rotateZ = -L_Thumb1.rotateZ;
            # l_thumb2_jnt.rotateX = -L_Thumb2.rotateX;
            # l_thumb2_jnt.rotateY = L_Thumb2.rotateY;
            # l_thumb2_jnt.rotateZ = -L_Thumb2.rotateZ;
            # l_thumb1_jnt.rotateZ = -L_Thumb3.rotateZ;
            # l_thumb_jnt.rotateX = -finger_base_L_OFFSET.rotateX;
            # l_thumb_jnt.rotateY = finger_base_L_OFFSET.rotateY;
            # l_thumb_jnt.rotateZ = -finger_base_L_OFFSET.rotateZ;

            # l_index_chn.rotateY  = -0.8 * finger_base_L_ROT.rotateY;
            # l_index3_jnt.rotateX = -L_Index1.rotateX;
            # l_index3_jnt.rotateY = L_Index1.rotateY;
            # l_index3_jnt.rotateZ = -L_Index1.rotateZ - 0.95* finger_base_L_ROT.rotateZ * $rtrn_tz * $rtrn_bx;
            # l_index2_jnt.rotateZ = -L_Index2.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_tz;
            # l_index1_jnt.rotateZ = -L_Index3.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_tz * ( 2 - $rtrn_bx * 0.95 );

            # l_middle_jnt.rotateX = -L_Middle0.rotateX - 0.2 * finger_base_L_ROT.rotateX;
            # l_middle_jnt.rotateY = L_Middle0.rotateY + 0.25* finger_base_L_ROT.rotateY;
            # l_middle_jnt.rotateZ = -L_Middle0.rotateZ - 0.05* finger_base_L_ROT.rotateZ;
            # l_middle3_jnt.rotateX = -L_Middle1.rotateX;
            # l_middle3_jnt.rotateY = L_Middle1.rotateY;
            # l_middle3_jnt.rotateZ = -L_Middle1.rotateZ - 0.95* finger_base_L_ROT.rotateZ * $rtrn_mtz * $rtrn_bx;
            # l_middle2_jnt.rotateZ = -L_Middle2.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_mtz;
            # l_middle1_jnt.rotateZ = -L_Middle3.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_mtz * ( 2 - $rtrn_bx * 0.95 );

            # l_ring_jnt.rotateX = -L_Ring0.rotateX + L_Middle0.rotateX - 0.2 * finger_base_L_ROT.rotateX;
            # l_ring_jnt.rotateY = L_Ring0.rotateY - L_Middle0.rotateY + 0.2 * finger_base_L_ROT.rotateY;
            # l_ring_jnt.rotateZ = -L_Ring0.rotateZ + L_Middle0.rotateZ - 0.1 * finger_base_L_ROT.rotateZ;
            # l_ring_chn.rotateX =  0.1 * finger_base_L_ROT.rotateX;
            # l_ring_chn.rotateY =  0.9 * finger_base_L_ROT.rotateY;
            # l_ring3_jnt.rotateX = -L_Ring1.rotateX;
            # l_ring3_jnt.rotateY = L_Ring1.rotateY;
            # l_ring3_jnt.rotateZ = -L_Ring1.rotateZ - 0.95* finger_base_L_ROT.rotateZ * $rtrn_rmtz * $rtrn_bx;
            # l_ring2_jnt.rotateZ = -L_Ring2.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_rmtz;
            # l_ring1_jnt.rotateZ = -L_Ring3.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_rmtz * ( 2 - $rtrn_bx * 0.95 );

            # l_pinky_jnt.rotateX = -L_Pinky0.rotateX + L_Ring0.rotateX - 0.4 * finger_base_L_ROT.rotateX;
            # l_pinky_jnt.rotateY = L_Pinky0.rotateY - L_Ring0.rotateY + 0.3 * finger_base_L_ROT.rotateY;
            # l_pinky_jnt.rotateZ = -L_Pinky0.rotateZ + L_Ring0.rotateZ - 0.15* finger_base_L_ROT.rotateX;

            # l_pinky_chn.rotateX =  0.3 * finger_base_L_ROT.rotateX;
            # l_pinky_chn.rotateY =  2.2 * finger_base_L_ROT.rotateY;
            # l_pinky3_jnt.rotateX = -L_Pinky1.rotateX;
            # l_pinky3_jnt.rotateY = L_Pinky1.rotateY;
            # l_pinky3_jnt.rotateZ = -L_Pinky1.rotateZ - 0.95* finger_base_L_ROT.rotateZ * $rtrn_rtz * $rtrn_bx;
            # l_pinky2_jnt.rotateZ = -L_Pinky2.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_rtz;
            # l_pinky1_jnt.rotateZ = -L_Pinky3.rotateZ - 1.0 * finger_base_L_ROT.rotateZ * $rtrn_rtz * ( 2 - $rtrn_bx * 0.95 );



