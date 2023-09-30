from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)

import utils.matrix
reload(utils.matrix)

import om.utility
reload(om.utility)









class StretchyIKSpline:

    def __init__(self, base_name, joints, curve, master, ctrls):
        """ """
        self.base_name = base_name
        self.joints = joints
        self.curve = curve
        self.master = master
        self.ctrls = ctrls

        self.main()

    def main(self):
        """ """

        crv_info = cmds.createNode('curveInfo', name=f'{self.base_name}_crvInfo')
        cmds.connectAttr(f'{cmds.listRelatives(self.curve, shapes=True)[0]}.worldSpace[0]', f'{crv_info}.inputCurve')

        master_dcm = cmds.createNode('decomposeMatrix', name=f'{self.base_name}_master_DCM')
        cmds.connectAttr(f'{self.master}.worldMatrix[0]', f'{master_dcm}.inputMatrix')

        scale_compensate_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_scaleCompensate_MD')
        cmds.connectAttr(f'{master_dcm}.outputScaleX', f'{scale_compensate_md}.input2X')
        cmds.setAttr(f'{scale_compensate_md}.input1X', cmds.getAttr(f'{crv_info}.arcLength'))

        ratio_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_ratio_MD')
        cmds.setAttr(f'{ratio_md}.operation', 2)
        cmds.connectAttr(f'{crv_info}.arcLength', f'{ratio_md}.input1X')
        cmds.connectAttr(f'{scale_compensate_md}.outputX', f'{ratio_md}.input2X')

        # squash and stretch
        inverse_ratio_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_inverseRatio_MD')
        cmds.connectAttr(f'{ratio_md}.outputX', f'{inverse_ratio_md}.input2X')
        cmds.setAttr(f'{inverse_ratio_md}.input1X', 1)
        cmds.setAttr(f'{inverse_ratio_md}.operation', 2)

        stretch_attr, self.ctrls = utils.helper.add_float_attribute(attr_name='stretch', ctrls=self.ctrls, dv_value=0)
        stretch_bc = cmds.createNode('blendColors', name=f'{self.base_name}_stretchSwitch_BC')
        cmds.connectAttr(f'{self.ctrls[0]}.{stretch_attr}', f'{stretch_bc}.blender')

        # if turned on, the returned scale is modified by the calculated ratios.
        cmds.connectAttr(f'{ratio_md}.outputX', f'{stretch_bc}.color1R')
        cmds.connectAttr(f'{inverse_ratio_md}.outputX', f'{stretch_bc}.color1G')

        # if turned off, the returned scale is 1
        cmds.setAttr(f'{stretch_bc}.color2R', 1)
        cmds.setAttr(f'{stretch_bc}.color2G', 1)
 
        # squash goes through another checkpoint (it has to pass both checkpoints, that way if stretch is off, everything if off)
        squash_attr, self.ctrls = utils.helper.add_float_attribute(attr_name='volumetric', ctrls=self.ctrls, dv_value=0)
        squash_bc = cmds.createNode('blendColors', name=f'{self.base_name}_squashSwitch_BC')
        cmds.connectAttr(f'{self.ctrls[0]}.{squash_attr}', f'{squash_bc}.blender')

        # if turned on, the returned scale is modified by the calculated inverse ratio
        cmds.connectAttr(f'{stretch_bc}.outputG', f'{squash_bc}.color1G')

        # if turned off, the returned scale is 1
        cmds.setAttr(f'{squash_bc}.color2G', 1)

        for jnt in self.joints:
            cmds.connectAttr(f'{stretch_bc}.outputR', f'{jnt}.scaleX')
            cmds.connectAttr(f'{squash_bc}.outputG', f'{jnt}.scaleY')
            cmds.connectAttr(f'{squash_bc}.outputG', f'{jnt}.scaleZ')






class IKSplineStretch:

    """ not connected yet. """

    def __init__(self, base_name, joint_chain, curve, master, primary_axis):
        self.base_name = base_name
        self.joint_chain = joint_chain
        self.curve = curve
        self.master = master  # to accomodate for global scale
        self.primary_axis = primary_axis.capitalize()
        axis_dict = {'X': ['Y', 'Z'], 'Y': ['X', 'Z'], 'Z': ['X', 'Y']}  # determines which axis is stretch and which is squash, needed when connecting to jnts
        self.secondary_axis = axis_dict[primary_axis][0]
        self.tertiary_axis = axis_dict[primary_axis][1]


    def create_stretch_network(self):
        """ Creates the basic network for stretch which calculates the stretch ratio. """

        crv_info = cmds.createNode('curveInfo', name=f'{self.base_name}_crvInfo')
        cmds.connectAttr(f'{cmds.listRelatives(self.curve, shapes=True)[0]}.worldSpace[0]', f'{crv_info}.inputCurve')

        master_dcm = cmds.createNode('decomposeMatrix', name=f'{self.base_name}_master_DCM')
        cmds.connectAttr(f'{self.master}.worldMatrix[0]', f'{master_dcm}.inputMatrix')

        scale_compensate_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_scaleCompensate_MD')
        cmds.connectAttr(f'{master_dcm}.outputScaleX', f'{scale_compensate_md}.input2X')
        cmds.setAttr(f'{scale_compensate_md}.input1X', cmds.getAttr(f'{crv_info}.arcLength'))

        self.ratio_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_ratio_MD')
        cmds.setAttr(f'{self.ratio_md}.operation', 2)
        cmds.connectAttr(f'{crv_info}.arcLength', f'{self.ratio_md}.input1X')
        cmds.connectAttr(f'{scale_compensate_md}.outputX', f'{self.ratio_md}.input2X')


    def add_squash_to_network(self):
        """ Extends the stretch network by another multiply divide node containing the inverse ratio needed for squash. """
        self.inverse_ratio_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_inverseRatio_MD')
        cmds.connectAttr(f'{self.ratio_md}.outputX', f'{self.inverse_ratio_md}.input2X')
        cmds.setAttr(f'{self.inverse_ratio_md}.input1X', 1)
        cmds.setAttr(f'{self.inverse_ratio_md}.operation', 2)

    def connect_joints(self):
        for jnt in self.joint_chain:
            pass




class IKSplineStretchWAttr(IKSplineStretch):
    """ This is the class used for the rail spine with full functionality: stretch, squash and switch attrs for both """

    def __init__(self, base_name, joint_chain, curve, master, primary_axis, ctrls):
        super().__init__(base_name, joint_chain, curve, master, primary_axis)
        self.ctrls = ctrls

        super().create_stretch_network()
        super().add_squash_to_network()
        self.add_switch_attributes()
        self.connect_joints()

    def add_switch_attributes(self):
        self.stretch_attr, self.ctrls = utils.helper.add_float_attribute(attr_name='stretch', ctrls=self.ctrls)
        self.stretch_bc = cmds.createNode('blendColors', name=f'{self.base_name}_stretchSwitch_BC')
        cmds.connectAttr(f'{self.ctrls[0]}.{self.stretch_attr}', f'{self.stretch_bc}.blender')

        # if turned on, the returned scale is modified by the calculated ratios.
        cmds.connectAttr(f'{self.ratio_md}.outputX', f'{self.stretch_bc}.color1R')
        cmds.connectAttr(f'{self.inverse_ratio_md}.outputX', f'{self.stretch_bc}.color1G')

        # if turned off, the returned scale is 1
        cmds.setAttr(f'{self.stretch_bc}.color2R', 1)
        cmds.setAttr(f'{self.stretch_bc}.color2G', 1)
 
        # squash goes through another checkpoint (it has to pass both checkpoints, that way if stretch is off, everything if off)
        self.squash_attr, self.ctrls = utils.helper.add_float_attribute(attr_name='volumetric', ctrls=self.ctrls)
        self.squash_bc = cmds.createNode('blendColors', name=f'{self.base_name}_squashSwitch_BC')
        cmds.connectAttr(f'{self.ctrls[0]}.{self.squash_attr}', f'{self.squash_bc}.blender')

        # if turned on, the returned scale is modified by the calculated inverse ratio
        cmds.connectAttr(f'{self.stretch_bc}.outputG', f'{self.squash_bc}.color1G')

        # if turned off, the returned scale is 1
        cmds.setAttr(f'{self.squash_bc}.color2G', 1)

    def connect_joints(self):
        for jnt in self.joint_chain:
            cmds.connectAttr(f'{self.stretch_bc}.outputR', f'{jnt}.scale{self.primary_axis}')
            cmds.connectAttr(f'{self.squash_bc}.outputG', f'{jnt}.scale{self.secondary_axis}')
            cmds.connectAttr(f'{self.squash_bc}.outputG', f'{jnt}.scale{self.tertiary_axis}')







class IKSplineHourglassStretch(IKSplineStretch):
    """ This is the class used for the head. It doesn't have a switch. """

    def __init__(self, base_name, joint_chain, curve, master, primary_axis):
        super().__init__(base_name, joint_chain, curve, master, primary_axis)

        super().create_stretch_network()
        super().add_squash_to_network()
        self.add_hourglass_multiplier()
        self.connect_joints()

    def add_hourglass_multiplier(self):
        """ For the hourglass effect multiply the inverse ratio by another factor. This multiplier is here set to quadratic. """
        self.hourglass_multiplier_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_inverseRatioMultiplier_MD')
        cmds.connectAttr(f'{self.inverse_ratio_md}.outputX', f'{self.hourglass_multiplier_md}.input1X')
        cmds.connectAttr(f'{self.inverse_ratio_md}.outputX', f'{self.hourglass_multiplier_md}.input2X')

    def connect_joints(self):
        for jnt in self.joint_chain:
            cmds.connectAttr(f'{self.ratio_md}.outputX', f'{jnt}.scale{self.primary_axis}')

            if jnt in [self.joint_chain[0], self.joint_chain[-1]]:
                continue
            elif jnt in [self.joint_chain[1], self.joint_chain[3]]:
                cmds.connectAttr(f'{self.inverse_ratio_md}.outputX', f'{jnt}.scale{self.secondary_axis}')
                cmds.connectAttr(f'{self.inverse_ratio_md}.outputX', f'{jnt}.scale{self.tertiary_axis}')
            else:
                cmds.connectAttr(f'{self.hourglass_multiplier_md}.outputX', f'{jnt}.scale{self.secondary_axis}')
                cmds.connectAttr(f'{self.hourglass_multiplier_md}.outputX', f'{jnt}.scale{self.tertiary_axis}')




























