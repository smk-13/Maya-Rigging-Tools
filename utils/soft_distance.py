from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import utils.helper
reload(utils.helper)






class SoftIK:
    """ just soft distance without the other effects. """

    def __init__(self, base_name, ctrl, ik_chain, start, end, master, ikh, primary_axis='X'):
        self.base_name = base_name
        self.ctrl = ctrl
        self.ik_chain = ik_chain
        self.start = start
        self.end = end
        self.master = master
        self.ikh = ikh
        self.primary_axis = primary_axis

        self.create_setup()
        self.soft_exp()

    def create_setup(self):

        # attrs
        self.soft_attr = 'soft'
        cmds.addAttr(self.ctrl, ln=self.soft_attr, at='double', min=0, max=10, dv=1, k=True)

        # current distance
        self.current_dist = cmds.createNode('distanceBetween', name=f'{self.base_name}_ctrl_DIST')
        cmds.connectAttr(f'{self.start}.worldMatrix[0]', f'{self.current_dist}.inMatrix1')
        cmds.connectAttr(f'{self.end}.worldMatrix[0]', f'{self.current_dist}.inMatrix2')

        # normalized direction vector
        self.start_dcm = cmds.createNode('decomposeMatrix', name=f'{self.base_name}_start_DCM')
        self.end_dcm = cmds.createNode('decomposeMatrix', name=f'{self.base_name}_end_DCM')
        cmds.connectAttr(f'{self.start}.worldMatrix[0]', f'{self.start_dcm}.inputMatrix')
        cmds.connectAttr(f'{self.end}.worldMatrix[0]', f'{self.end_dcm}.inputMatrix')

        self.direction_pma = cmds.createNode('plusMinusAverage', name=f'{self.base_name}_direction_PMA')
        cmds.setAttr(f'{self.direction_pma}.operation', 2)
        cmds.connectAttr(f'{self.start_dcm}.outputTranslate', f'{self.direction_pma}.input3D[1]')
        cmds.connectAttr(f'{self.end_dcm}.outputTranslate', f'{self.direction_pma}.input3D[0]')

        self.direction_vp = cmds.createNode('vectorProduct', name=f'{self.base_name}_direction_VP')
        cmds.setAttr(f'{self.direction_vp}.operation', 0)
        cmds.setAttr(f'{self.direction_vp}.normalizeOutput', 1)
        cmds.connectAttr(f'{self.direction_pma}.output3D', f'{self.direction_vp}.input1')

        # rest length
        self.master_dcm = cmds.createNode('decomposeMatrix', name=f'{self.master}_DCM')
        cmds.connectAttr(f'{self.master}.worldMatrix[0]', f'{ self.master_dcm}.inputMatrix')
        self.rest_length_mdl = cmds.createNode('multDoubleLinear', name=f'{self.base_name}_restLength_MDL')
        cmds.connectAttr(f'{self.master_dcm}.outputScaleX', f'{self.rest_length_mdl}.input1')
        self.upper_length = abs(cmds.getAttr(f'{self.ik_chain[1]}.translate{self.primary_axis}'))
        self.lower_length = abs(cmds.getAttr(f'{self.ik_chain[2]}.translate{self.primary_axis}'))
        self.total_length = self.upper_length + self.lower_length
        cmds.setAttr(f'{self.rest_length_mdl}.input2', self.total_length)

        # IMPORTANT
        cmds.setAttr(f'{self.ikh}.inheritsTransform', 0)


    def soft_exp_v1(self):
        """ """

        self.soft_exp = cmds.expression(name=f'{self.base_name}_EXP', s=f"""

            {self.ikh}.translateX = {self.end_dcm}.outputTranslateX;
            {self.ikh}.translateY = {self.end_dcm}.outputTranslateY;
            {self.ikh}.translateZ = {self.end_dcm}.outputTranslateZ;

            float $ctrlDist = {self.current_dist}.distance;
            float $softP = {self.ctrl}.{self.soft_attr} * {self.master}.scaleY;
            float $chainLen = {self.rest_length_mdl}.output;
            float $softDist = $chainLen;

            if ($ctrlDist > ($chainLen - $softP)){{
                if ($softP > 0){{

                    // the soft distance formula
                    $softDist = $chainLen - $softP * pow(2.718281828, -($ctrlDist - ($chainLen - $softP)) / $softP);

                    {self.ikh}.translateX = {self.start_dcm}.outputTranslateX + ({self.direction_vp}.outputX * $softDist);
                    {self.ikh}.translateY = {self.start_dcm}.outputTranslateY + ({self.direction_vp}.outputY * $softDist);
                    {self.ikh}.translateZ = {self.start_dcm}.outputTranslateZ + ({self.direction_vp}.outputZ * $softDist);

                }}
            }}

            """)


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

            {self.ikh}.translateX = {self.start_dcm}.outputTranslateX + ({self.direction_vp}.outputX * $softDist);
            {self.ikh}.translateY = {self.start_dcm}.outputTranslateY + ({self.direction_vp}.outputY * $softDist);
            {self.ikh}.translateZ = {self.start_dcm}.outputTranslateZ + ({self.direction_vp}.outputZ * $softDist);

            """)