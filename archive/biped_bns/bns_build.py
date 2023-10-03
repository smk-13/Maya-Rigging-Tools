from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)

import BNS.bns_master
reload(BNS.bns_master)

import BNS.bns_spine
reload(BNS.bns_spine)

import BNS.bns_neck
reload(BNS.bns_neck)

import BNS.bns_finger
reload(BNS.bns_finger)

import BNS.bns_leg
reload(BNS.bns_leg)

import BNS.bns_arm
reload(BNS.bns_arm)

import BNS.bns_eyes
reload(BNS.bns_eyes)

import BNS.bns_jaw
reload(BNS.bns_jaw)





class Biped:

    def __init__(self):
        """ """

        self.rig_name = 'Asari_Rig'

        BNS.bns_master.Master(name=self.rig_name)
        BNS.bns_spine.Spine()
        BNS.bns_neck.Neck()
        BNS.bns_leg.Leg(side='L', color=13)
        BNS.bns_leg.Leg(side='R', color=6)
        BNS.bns_arm.Arm(side='L', color=13)
        BNS.bns_arm.Arm(side='R', color=6)
        BNS.bns_finger.Finger(side='L', color=13)
        BNS.bns_finger.Finger(side='R', color=6)
        BNS.bns_eyes.Eyes()
        BNS.bns_jaw.Jaw()

        self.create_export_skeleton()
        self.create_display_layers()
        self.optimize_constraints()
        self.initialize_skinning()

    def create_export_skeleton(self):
        """ NAME: [PARENT, DRIVER] """

        self.export_skeleton_dict = {
            'root_exp': ['skeleton_grp', 'master2_ctl'],
            'pelvis_exp': ['root_exp', 'pelvis_jnt'],
            'spine1_exp': ['pelvis_exp', 'spine1_jnt'],
            'spine2_exp': ['spine1_exp', 'spine2_jnt'],
            'chest_exp': ['spine2_exp', 'chest_jnt'],
            'neck_exp': ['chest_exp', 'neck_jnt'],
            'head_exp': ['neck_exp', 'head_jnt'],

            'L_eye_exp': ['head_exp', 'L_eye_jnt'],
            'R_eye_exp': ['head_exp', 'R_eye_jnt'],
            'jaw_exp': ['head_exp', 'jaw_jnt'],

            'L_butt_exp' : ['pelvis_exp', 'L_butt_jnt'], 
            'L_thigh0_exp': ['L_butt_exp', 'L_thigh_roll_start'],
            'L_thigh1_exp': ['L_thigh0_exp', 'L_thigh_roll_0'],
            'L_thigh2_exp': ['L_thigh1_exp', 'L_thigh_roll_1'],
            'L_thigh3_exp': ['L_thigh2_exp', 'L_thigh_roll_2'],
            'L_thigh4_exp': ['L_thigh3_exp', 'L_thigh_roll_end'],
            'L_shin0_exp': ['L_thigh4_exp', 'L_knee_jnt'],
            'L_shin1_exp': ['L_shin0_exp','L_shin_roll_0'],
            'L_shin2_exp': ['L_shin1_exp', 'L_shin_roll_1'],
            'L_shin3_exp': ['L_shin2_exp', 'L_shin_roll_2'],
            'L_shin4_exp': ['L_shin3_exp', 'L_shin_roll_end'],
            'L_ankle_exp': ['L_shin4_exp', 'L_ankle_jnt'],
            'L_ball_exp': ['L_ankle_exp', 'L_ball_jnt'],

            'R_butt_exp' : ['pelvis_exp', 'R_butt_jnt'], 
            'R_thigh0_exp': ['R_butt_exp', 'R_thigh_roll_start'],
            'R_thigh1_exp': ['R_thigh0_exp', 'R_thigh_roll_0'],
            'R_thigh2_exp': ['R_thigh1_exp', 'R_thigh_roll_1'],
            'R_thigh3_exp': ['R_thigh2_exp', 'R_thigh_roll_2'],
            'R_thigh4_exp': ['R_thigh3_exp', 'R_thigh_roll_end'],
            'R_shin0_exp': ['R_thigh4_exp', 'R_knee_jnt'],
            'R_shin1_exp': ['R_shin0_exp','R_shin_roll_0'],
            'R_shin2_exp': ['R_shin1_exp', 'R_shin_roll_1'],
            'R_shin3_exp': ['R_shin2_exp', 'R_shin_roll_2'],
            'R_shin4_exp': ['R_shin3_exp', 'R_shin_roll_end'],
            'R_ankle_exp': ['R_shin4_exp', 'R_ankle_jnt'],
            'R_ball_exp': ['R_ankle_exp', 'R_ball_jnt'],

            'L_shoulder_exp': ['chest_exp', 'L_shoulder_jnt'], 
            'L_upperArm0_exp': ['L_shoulder_exp', 'L_upperArm_roll_start'],
            'L_upperArm1_exp': ['L_upperArm0_exp', 'L_upperArm_roll_0'],
            'L_upperArm2_exp': ['L_upperArm1_exp', 'L_upperArm_roll_1'],
            'L_upperArm3_exp': ['L_upperArm2_exp', 'L_upperArm_roll_2'],
            'L_upperArm4_exp': ['L_upperArm3_exp', 'L_upperArm_roll_end'],
            'L_forearm0_exp': ['L_upperArm4_exp', 'L_forearm_jnt'],
            'L_forearm1_exp': ['L_forearm0_exp', 'L_forearm_roll_0'],
            'L_forearm2_exp': ['L_forearm1_exp', 'L_forearm_roll_1'],
            'L_forearm3_exp': ['L_forearm2_exp', 'L_forearm_roll_2'],
            'L_forearm4_exp': ['L_forearm3_exp', 'L_forearm_roll_end'],
            'L_wrist_exp': ['L_forearm4_exp', 'L_wrist_jnt'],

            'R_shoulder_exp': ['chest_exp', 'R_shoulder_jnt'], 
            'R_upperArm0_exp': ['R_shoulder_exp', 'R_upperArm_roll_start'],
            'R_upperArm1_exp': ['R_upperArm0_exp', 'R_upperArm_roll_0'],
            'R_upperArm2_exp': ['R_upperArm1_exp', 'R_upperArm_roll_1'],
            'R_upperArm3_exp': ['R_upperArm2_exp', 'R_upperArm_roll_2'],
            'R_upperArm4_exp': ['R_upperArm3_exp', 'R_upperArm_roll_end'],
            'R_forearm0_exp': ['R_upperArm4_exp', 'R_forearm_jnt'],
            'R_forearm1_exp': ['R_forearm0_exp', 'R_forearm_roll_0'],
            'R_forearm2_exp': ['R_forearm1_exp', 'R_forearm_roll_1'],
            'R_forearm3_exp': ['R_forearm2_exp', 'R_forearm_roll_2'],
            'R_forearm4_exp': ['R_forearm3_exp', 'R_forearm_roll_end'],
            'R_wrist_exp': ['R_forearm4_exp', 'R_wrist_jnt'],

            'L_thumb0_exp': ['L_wrist_exp', 'L_thumb0_jnt'],
            'L_thumb1_exp': ['L_thumb0_exp', 'L_thumb1_jnt'],
            'L_thumb2_exp': ['L_thumb1_exp', 'L_thumb2_jnt'],
            'L_index0_exp': ['L_wrist_exp', 'L_index0_jnt'],
            'L_index1_exp': ['L_index0_exp', 'L_index1_jnt'],
            'L_index2_exp': ['L_index1_exp', 'L_index2_jnt'],
            'L_index3_exp': ['L_index2_exp', 'L_index3_jnt'],
            'L_middle0_exp': ['L_wrist_exp', 'L_middle0_jnt'],
            'L_middle1_exp': ['L_middle0_exp', 'L_middle1_jnt'],
            'L_middle2_exp': ['L_middle1_exp', 'L_middle2_jnt'],
            'L_middle3_exp': ['L_middle2_exp', 'L_middle3_jnt'],
            'L_ring0_exp': ['L_wrist_exp', 'L_ring0_jnt'],
            'L_ring1_exp': ['L_ring0_exp', 'L_ring1_jnt'],
            'L_ring2_exp': ['L_ring1_exp', 'L_ring2_jnt'],
            'L_ring3_exp': ['L_ring2_exp', 'L_ring3_jnt'],
            'L_pinky0_exp': ['L_wrist_exp', 'L_pinky0_jnt'],
            'L_pinky1_exp': ['L_pinky0_exp', 'L_pinky1_jnt'],
            'L_pinky2_exp': ['L_pinky1_exp', 'L_pinky2_jnt'],
            'L_pinky3_exp': ['L_pinky2_exp', 'L_pinky3_jnt'],

            'R_thumb0_exp': ['R_wrist_exp', 'R_thumb0_jnt'],
            'R_thumb1_exp': ['R_thumb0_exp', 'R_thumb1_jnt'],
            'R_thumb2_exp': ['R_thumb1_exp', 'R_thumb2_jnt'],
            'R_index0_exp': ['R_wrist_exp', 'R_index0_jnt'],
            'R_index1_exp': ['R_index0_exp', 'R_index1_jnt'],
            'R_index2_exp': ['R_index1_exp', 'R_index2_jnt'],
            'R_index3_exp': ['R_index2_exp', 'R_index3_jnt'],
            'R_middle0_exp': ['R_wrist_exp', 'R_middle0_jnt'],
            'R_middle1_exp': ['R_middle0_exp', 'R_middle1_jnt'],
            'R_middle2_exp': ['R_middle1_exp', 'R_middle2_jnt'],
            'R_middle3_exp': ['R_middle2_exp', 'R_middle3_jnt'],
            'R_ring0_exp': ['R_wrist_exp', 'R_ring0_jnt'],
            'R_ring1_exp': ['R_ring0_exp', 'R_ring1_jnt'],
            'R_ring2_exp': ['R_ring1_exp', 'R_ring2_jnt'],
            'R_ring3_exp': ['R_ring2_exp', 'R_ring3_jnt'],
            'R_pinky0_exp': ['R_wrist_exp', 'R_pinky0_jnt'],
            'R_pinky1_exp': ['R_pinky0_exp', 'R_pinky1_jnt'],
            'R_pinky2_exp': ['R_pinky1_exp', 'R_pinky2_jnt'],
            'R_pinky3_exp': ['R_pinky2_exp', 'R_pinky3_jnt']
        }

        for exp_jnt in self.export_skeleton_dict.keys():
            cmds.select(cl=True)
            cmds.joint(name=exp_jnt)

        for exp_jnt, data in self.export_skeleton_dict.items():
            cmds.parent(exp_jnt, data[0])
            cmds.matchTransform(exp_jnt, data[1])
            cmds.makeIdentity(exp_jnt, apply=True)
            cnst = cmds.parentConstraint(data[1], exp_jnt)[0]
            cmds.parent(cnst, 'constraint_grp')

        # hide all non exp jnts
        for jnt in cmds.listRelatives('master_ctl', children=True, ad=True, type='joint'):
            cmds.setAttr(f'{jnt}.drawStyle', 2)

    def create_display_layers(self):
        ctl_layer = 'ctl_layer'
        exp_layer = 'skeleton_layer'
        geo_layer = 'geo_layer'
        if not cmds.objExists(ctl_layer): cmds.createDisplayLayer(cmds.ls('*_ctl'), noRecurse=True, name=ctl_layer)
        if not cmds.objExists(exp_layer): cmds.createDisplayLayer(cmds.ls('*_exp'), noRecurse=True, name=exp_layer)
        if not cmds.objExists(geo_layer): cmds.createDisplayLayer(cmds.ls('*_geo'), noRecurse=True, name=geo_layer)
        cmds.setAttr(f'{exp_layer}.visibility', 0)
        cmds.setAttr(f'{geo_layer}.displayType', 2)


    def optimize_constraints(self):
        all_cnsts = cmds.ls(type='constraint')
        for cnst in all_cnsts:
            utils.helper.optimize_constraint(constraint=cnst)


    def initialize_skinning(self):

        body_jnts = [jnt for jnt in self.export_skeleton_dict.keys() if jnt not in ['root_exp', 'L_eye_exp', 'R_eye_exp', 'jaw_exp']]

        cmds.skinCluster(body_jnts, 'asari_body_geo', name='asari_body_geo_skc', toSelectedBones=True)
        cmds.skinCluster(['L_eye_exp', 'R_eye_exp'], 'asari_eyes_geo', name='asari_eyes_geo_skc', toSelectedBones=True, maximumInfluences=1)
        cmds.skinCluster(['neck_exp', 'head_exp', 'jaw_exp'], 'asari_head_geo', name='asari_head_geo_skc', toSelectedBones=True)

