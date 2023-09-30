from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)


class SoftDistance:


    def __init__(self, base_name, target_transform, end_dcm, start_dcm, direction_vp, current_dist, rest_length_mdl, ctrl, soft_attr, master_dcm):
        self.base_name = base_name
        self.target_transform = target_transform
        self.end_dcm = end_dcm
        self.start_dcm = start_dcm
        self.direction_vp = direction_vp
        self.current_dist = current_dist
        self.rest_length_mdl = rest_length_mdl  # if multiplyDivide is used instead of multDoubleLinear change output to outputX
        self.ctrl = ctrl
        self.soft_attr = soft_attr
        self.master_dcm = master_dcm

        self.soft_exp()



    def soft_exp(self):

        self.soft_exp = cmds.expression(name=f'{self.base_name}_softDistance_EXP', s=f"""

            float $ctrlDist = {self.current_dist}.distance;
            float $softP = {self.ctrl}.{self.soft_attr} * {self.master_dcm}.outputScaleX;
            float $chainLen = {self.rest_length_mdl}.output;
            float $softDist = $ctrlDist;

            if ($ctrlDist > ($chainLen - $softP)){{
                if ($softP > 0){{

                    // the soft distance formula
                    $softDist = $chainLen - $softP * pow(2.718281828, -($ctrlDist - ($chainLen - $softP)) / $softP);

                }}
                else {{
                    $softDist = $chainLen;
                }}
            }}

            {self.target_transform}.translateX = {self.start_dcm}.outputTranslateX + ({self.direction_vp}.outputX * $softDist);
            {self.target_transform}.translateY = {self.start_dcm}.outputTranslateY + ({self.direction_vp}.outputY * $softDist);
            {self.target_transform}.translateZ = {self.start_dcm}.outputTranslateZ + ({self.direction_vp}.outputZ * $softDist);

            """)







class IKEffects:


    def __init__(self, base_name, ik_chain, main_ctrl, pv_ctrl, base, master, ikh, effector, primary_axis='X'):

        self.base_name = f'{base_name}_ikEffects'  # e.g. L_arm
        self.ik_chain = ik_chain
        self.main_ctrl = main_ctrl
        self.pv_ctrl = pv_ctrl
        self.base = base  # this is either the base ctrl or the base jnt (if the clavicle is translation based, it needs to be the jnt)
        self.master = master # the lowest ranked master ctrl
        self.ikh = ikh
        self.primary_axis = primary_axis
        self.effector = effector  # this can be main_ctrl or in a rev chain setup, the end of the rev chain. This is not the best name, because ikh buffer is also an effector...

        self.main()

    def main(self):
        """ """

        # attrs
        self.stretch_attr = 'stretch'
        self.soft_attr = 'soft'
        self.lock_attr = 'lock'
        self.slide_attr = 'slide'
        cmds.addAttr(self.main_ctrl, ln=self.stretch_attr, at='double', min=0, max=1, dv=0, k=True)
        cmds.addAttr(self.main_ctrl, ln=self.soft_attr, at='double', min=0, max=1, dv=0, k=True)
        cmds.addAttr(self.main_ctrl, ln=self.lock_attr, at='double', min=0, max=1, dv=0, k=True)
        cmds.addAttr(self.main_ctrl, ln=self.slide_attr, at='double', min=-1, max=1, dv=0, k=True)

        # buffers
        self.start_buffer = cmds.createNode('transform', name=f'{self.base_name}_startBuffer', parent=self.base)
        self.mid_buffer = cmds.createNode('transform', name=f'{self.base_name}_midBuffer', parent=self.pv_ctrl)
        self.end_buffer = cmds.createNode('transform', name=f'{self.base_name}_endBuffer', parent=self.effector)
        cmds.matchTransform(self.start_buffer, self.ik_chain[0])
        cmds.matchTransform(self.mid_buffer, self.pv_ctrl)
        cmds.matchTransform(self.end_buffer, self.ik_chain[2])

        self.soft_transform = cmds.createNode('transform', name=f'{self.base_name}_softTransform', parent=self.master)
        cmds.setAttr(f'{self.soft_transform}.inheritsTransform', 0)

        self.ikh_buffer = cmds.createNode('transform', name=f'{self.base_name}_ikhBuffer')
        cmds.matchTransform(self.ikh_buffer, self.ikh)
        ikh_original_parent = cmds.listRelatives(self.ikh, parent=True)
        if ikh_original_parent:
            cmds.parent(self.ikh_buffer, ikh_original_parent)
        cmds.parent(self.ikh, self.ikh_buffer)

        # distances
        self.ctrl_dist = cmds.createNode('distanceBetween', name=f'{self.base_name}_ctrl_DIST')
        cmds.connectAttr(f'{self.start_buffer}.worldMatrix[0]', f'{self.ctrl_dist}.inMatrix1')
        cmds.connectAttr(f'{self.end_buffer}.worldMatrix[0]', f'{self.ctrl_dist}.inMatrix2')

        self.upperLock_dist = cmds.createNode('distanceBetween', name=f'{self.base_name}_upperLock_DIST')
        cmds.connectAttr(f'{self.start_buffer}.worldMatrix[0]', f'{self.upperLock_dist}.inMatrix1')
        cmds.connectAttr(f'{self.mid_buffer}.worldMatrix[0]', f'{self.upperLock_dist}.inMatrix2')

        self.lowerLock_dist = cmds.createNode('distanceBetween', name=f'{self.base_name}_lowerLock_DIST')
        cmds.connectAttr(f'{self.mid_buffer}.worldMatrix[0]', f'{self.lowerLock_dist}.inMatrix1')
        cmds.connectAttr(f'{self.effector}.worldMatrix[0]', f'{self.lowerLock_dist}.inMatrix2')


        self.soft_dist = cmds.createNode('distanceBetween', name=f'{self.base_name}_soft_DIST')
        cmds.connectAttr(f'{self.start_buffer}.worldMatrix[0]', f'{self.soft_dist}.inMatrix1')
        cmds.connectAttr(f'{self.soft_transform}.worldMatrix[0]', f'{self.soft_dist}.inMatrix2')


        # rest length
        if not cmds.objExists(f'{self.master}_DCM'):
            self.master_dcm = cmds.createNode('decomposeMatrix', name=f'{self.master}_DCM')
            cmds.connectAttr(f'{self.master}.worldMatrix[0]', f'{ self.master_dcm}.inputMatrix')
        else:
            self.master_dcm = f'{self.master}_DCM'

        self.rest_length_mdl = cmds.createNode('multDoubleLinear', name=f'{self.base_name}_restLength_MDL')
        cmds.connectAttr(f'{self.master_dcm}.outputScaleX', f'{self.rest_length_mdl}.input1')
        self.upper_length = abs(cmds.getAttr(f'{self.ik_chain[1]}.translate{self.primary_axis}'))
        self.lower_length = abs(cmds.getAttr(f'{self.ik_chain[2]}.translate{self.primary_axis}'))
        self.total_length = self.upper_length + self.lower_length
        cmds.setAttr(f'{self.rest_length_mdl}.input2', self.total_length)


        # normalized direction vector
        self.start_dcm = cmds.createNode('decomposeMatrix', name=f'{self.base_name}_startBuffer_DCM')  # the naming could be better
        self.end_dcm = cmds.createNode('decomposeMatrix', name=f'{self.base_name}_endBuffer_DCM')  # the naming could be better
        cmds.connectAttr(f'{self.start_buffer}.worldMatrix[0]', f'{self.start_dcm}.inputMatrix')
        cmds.connectAttr(f'{self.end_buffer}.worldMatrix[0]', f'{self.end_dcm}.inputMatrix')

        self.direction_pma = cmds.createNode('plusMinusAverage', name=f'{self.base_name}_direction_PMA')
        cmds.setAttr(f'{self.direction_pma}.operation', 2)
        cmds.connectAttr(f'{self.start_dcm}.outputTranslate', f'{self.direction_pma}.input3D[1]')
        cmds.connectAttr(f'{self.end_dcm}.outputTranslate', f'{self.direction_pma}.input3D[0]')

        self.direction_vp = cmds.createNode('vectorProduct', name=f'{self.base_name}_direction_VP')
        cmds.setAttr(f'{self.direction_vp}.operation', 0)
        cmds.setAttr(f'{self.direction_vp}.normalizeOutput', 1)
        cmds.connectAttr(f'{self.direction_pma}.output3D', f'{self.direction_vp}.input1')


        # soft expression
        SoftDistance(base_name=self.base_name, target_transform=self.soft_transform, end_dcm=self.end_dcm, start_dcm=self.start_dcm, direction_vp=self.direction_vp,
            current_dist=self.ctrl_dist, rest_length_mdl=self.rest_length_mdl, ctrl=self.main_ctrl, soft_attr=self.soft_attr, master_dcm=self.master_dcm)


        # stretch
        self.stretchFactor_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_stretchFactor_MD')
        cmds.connectAttr(f'{self.ctrl_dist}.distance', f'{self.stretchFactor_md}.input1X')
        cmds.connectAttr(f'{self.soft_dist}.distance', f'{self.stretchFactor_md}.input2X')
        cmds.setAttr(f'{self.stretchFactor_md}.operation', 2)

        self.stretch_cnd = cmds.createNode('condition', name=f'{self.base_name}_stretch_COND')
        cmds.setAttr(f'{self.stretch_cnd}.operation', 2)
        cmds.setAttr(f'{self.stretch_cnd}.secondTerm', 1)
        cmds.connectAttr(f'{self.stretchFactor_md}.outputX', f'{self.stretch_cnd}.firstTerm')
        cmds.connectAttr(f'{self.stretchFactor_md}.outputX', f'{self.stretch_cnd}.colorIfTrueR')

        self.stretch_bta = cmds.createNode('blendTwoAttr', name=f'{self.base_name}_stretch_BTA')
        cmds.setAttr(f'{self.stretch_bta}.input[0]', 1)
        cmds.connectAttr(f'{self.stretch_cnd}.outColorR', f'{self.stretch_bta}.input[1]')
        cmds.connectAttr(f'{self.main_ctrl}.{self.stretch_attr}', f'{self.stretch_bta}.attributesBlender')



        # blendmatrix between soft transform and ctrl buffer
        self.soft_stretch_bm = cmds.createNode('blendMatrix', name=f'{self.base_name}_softStretch_BM')
        cmds.connectAttr(f'{self.soft_transform}.worldMatrix[0]', f'{self.soft_stretch_bm}.inputMatrix')
        cmds.connectAttr(f'{self.end_buffer}.worldMatrix[0]', f'{self.soft_stretch_bm}.target[0].targetMatrix')
        cmds.connectAttr(f'{self.main_ctrl}.{self.stretch_attr}', f'{self.soft_stretch_bm}.target[0].weight')
        cmds.connectAttr(f'{self.soft_stretch_bm}.outputMatrix', f'{self.ikh_buffer}.offsetParentMatrix')
        cmds.setAttr(f'{self.soft_stretch_bm}.target[0].rotateWeight', 0)
        utils.helper.zero_out_transform(self.ikh_buffer)

        # slide
        self.slide_posOrNeg_cnd = cmds.createNode('condition', name=f'{self.base_name}_posOrNeg_COND')  # the naming could be better
        cmds.setAttr(f'{self.slide_posOrNeg_cnd}.colorIfTrueR', self.lower_length)
        cmds.setAttr(f'{self.slide_posOrNeg_cnd}.colorIfFalseR', self.upper_length)
        cmds.setAttr(f'{self.slide_posOrNeg_cnd}.operation', 2)
        cmds.connectAttr(f'{self.main_ctrl}.{self.slide_attr}', f'{self.slide_posOrNeg_cnd}.firstTerm')

        # calculate value that is added/subtracted by slide
        self.multBySlide_mdl = cmds.createNode('multDoubleLinear', name=f'{self.base_name}_multBySlide_MDL')
        cmds.connectAttr(f'{self.main_ctrl}.{self.slide_attr}', f'{self.multBySlide_mdl}.input1')
        cmds.connectAttr(f'{self.slide_posOrNeg_cnd}.outColorR', f'{self.multBySlide_mdl}.input2')

        self.multByNegOne_mdl = cmds.createNode('multDoubleLinear', name=f'{self.base_name}_multByNegOne_MDL')
        cmds.connectAttr(f'{self.multBySlide_mdl}.output', f'{self.multByNegOne_mdl}.input1')
        cmds.setAttr(f'{self.multByNegOne_mdl}.input2', -1)

        # add/subtract value to rest length of individual limb
        self.upperLimbRestLength_mdl = cmds.createNode('addDoubleLinear', name=f'{self.base_name}_upperLimbRestLength_ADL')
        cmds.setAttr(f'{self.upperLimbRestLength_mdl}.input1', self.upper_length)
        cmds.connectAttr(f'{self.multBySlide_mdl}.output', f'{self.upperLimbRestLength_mdl}.input2')

        self.lowerLimbRestLength_mdl = cmds.createNode('addDoubleLinear', name=f'{self.base_name}_lowerLimbRestLength_ADL')
        cmds.setAttr(f'{self.lowerLimbRestLength_mdl}.input1', self.lower_length)
        cmds.connectAttr(f'{self.multByNegOne_mdl}.output', f'{self.lowerLimbRestLength_mdl}.input2')

        # multiply stretch and slide components together
        self.upperLimbStretchedLength_mdl = cmds.createNode('multDoubleLinear', name=f'{self.base_name}_upperLimbStretchedLength_MDL')
        cmds.connectAttr(f'{self.upperLimbRestLength_mdl}.output', f'{self.upperLimbStretchedLength_mdl}.input1')
        cmds.connectAttr(f'{self.stretch_bta}.output', f'{self.upperLimbStretchedLength_mdl}.input2')

        self.lowerLimbStretchedLength_mdl = cmds.createNode('multDoubleLinear', name=f'{self.base_name}_lowerLimbStretchedLength_MDL')
        cmds.connectAttr(f'{self.lowerLimbRestLength_mdl}.output', f'{self.lowerLimbStretchedLength_mdl}.input1')
        cmds.connectAttr(f'{self.stretch_bta}.output', f'{self.lowerLimbStretchedLength_mdl}.input2')

        # lock
        self.upperLimbLock_bta = cmds.createNode('blendTwoAttr', name=f'{self.base_name}_upperLimbLock_BTA')
        cmds.connectAttr(f'{self.main_ctrl}.{self.lock_attr}', f'{self.upperLimbLock_bta}.attributesBlender')
        cmds.connectAttr(f'{self.upperLimbStretchedLength_mdl}.output', f'{self.upperLimbLock_bta}.input[0]')
        cmds.connectAttr(f'{self.upperLock_dist}.distance', f'{self.upperLimbLock_bta}.input[1]')

        self.lowerLimbLock_bta = cmds.createNode('blendTwoAttr', name=f'{self.base_name}_lowerLimbLock_BTA')
        cmds.connectAttr(f'{self.main_ctrl}.{self.lock_attr}', f'{self.lowerLimbLock_bta}.attributesBlender')
        cmds.connectAttr(f'{self.lowerLimbStretchedLength_mdl}.output', f'{self.lowerLimbLock_bta}.input[0]')
        cmds.connectAttr(f'{self.lowerLock_dist}.distance', f'{self.lowerLimbLock_bta}.input[1]')


        # right side is negative
        if cmds.getAttr(f'{self.ik_chain[1]}.translate{self.primary_axis}') < 1:
            self.multByNegOne2_md = cmds.createNode('multiplyDivide', name=f'{self.base_name}_multByNegOne2_MD')
            cmds.connectAttr(f'{self.upperLimbLock_bta}.output', f'{self.multByNegOne2_md}.input1X')
            cmds.connectAttr(f'{self.lowerLimbLock_bta}.output', f'{self.multByNegOne2_md}.input1Y')
            cmds.setAttr(f'{self.multByNegOne2_md}.input2X', -1)
            cmds.setAttr(f'{self.multByNegOne2_md}.input2Y', -1)
            cmds.connectAttr(f'{self.multByNegOne2_md}.outputX', f'{self.ik_chain[1]}.translateX')
            cmds.connectAttr(f'{self.multByNegOne2_md}.outputY', f'{self.ik_chain[2]}.translateX')
        else:
            cmds.connectAttr(f'{self.upperLimbLock_bta}.output', f'{self.ik_chain[1]}.translateX')
            cmds.connectAttr(f'{self.lowerLimbLock_bta}.output', f'{self.ik_chain[2]}.translateX')









