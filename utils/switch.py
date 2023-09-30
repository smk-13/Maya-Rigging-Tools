from maya import cmds
from maya.api import OpenMaya
import math
from enum import Enum, auto

from importlib import reload

import utils.helper
reload(utils.helper)





class IKFKSwitch:

    def __init__(self, base_name, bind_chain, ik_chain, ikCtlObjs, fkCtlObjs, fk_chain=None, ikfk_attr='FK', additionalCtlObjs=None):
        """ """

        self.base_name = base_name

        self.bind_chain = bind_chain
        self.ik_chain = ik_chain
        self.fk_chain = fk_chain

        self.ikCtlObjs = ikCtlObjs
        self.fkCtlObjs = fkCtlObjs
        self.additionalCtlObjs = [] if additionalCtlObjs is None else additionalCtlObjs

        self.ikfk_attr = ikfk_attr

        self.main()

    def main(self):

        # this is a shortcut
        if self.fk_chain is None:
            self.fk_chain = [fkCtlObj.ctrl for fkCtlObj in self.fkCtlObjs]

        # attr and proxy attrs
        if not isinstance(self.additionalCtlObjs, (tuple, list)):
            self.additionalCtlObjs = [self.additionalCtlObjs]

        cmds.addAttr(self.ikCtlObjs[0].ctrl, ln=self.ikfk_attr, at='double', dv=0, min=0, max=1, k=True)
        for obj in self.ikCtlObjs[1:] + self.fkCtlObjs + self.additionalCtlObjs:
            cmds.addAttr(obj.ctrl, proxy=f'{self.ikCtlObjs[0].ctrl}.{self.ikfk_attr}', ln=self.ikfk_attr)

        # joint chain switch
        for ik, fk, b in zip(self.ik_chain, self.fk_chain, self.bind_chain):
            bm = cmds.createNode('blendMatrix', name=f'{b}_BM')

            cmds.connectAttr(f'{ik}.worldMatrix[0]', f'{bm}.inputMatrix')
            cmds.connectAttr(f'{fk}.worldMatrix[0]', f'{bm}.target[0].targetMatrix')
            cmds.connectAttr(f'{self.ikCtlObjs[0].ctrl}.{self.ikfk_attr}', f'{bm}.target[0].weight')

            cmds.connectAttr(f'{bm}.outputMatrix', f'{b}.offsetParentMatrix')

            utils.helper.zero_out_transform(b)
            if cmds.objectType(ik, isType='joint'):
                cmds.setAttr(f'{ik}.drawStyle', 2)
            if cmds.objectType(fk, isType='joint'):
                cmds.setAttr(f'{fk}.drawStyle', 2)

        # visibility switch
        reverse = cmds.createNode('reverse', name=f'{self.base_name}_vis_REV')
        cmds.connectAttr(f'{self.ikCtlObjs[0].ctrl}.{self.ikfk_attr}', f'{reverse}.inputX')
        for obj in self.fkCtlObjs:
            cmds.connectAttr(f'{self.ikCtlObjs[0].ctrl}.{self.ikfk_attr}', f'{obj.grp}.visibility')
        for obj in self.ikCtlObjs:
            cmds.connectAttr(f'{reverse}.outputX', f'{obj.grp}.visibility')








class SpaceSwitch:

    def __init__(self, base_name, buffer, ctrl, space_dict):
        """ The ctrl holds the switch attr. The buffer is the transform node that is switched. The key of the space dict is the label and the value is the transform node it represents. """

        self.base_name = base_name
        self.buffer = buffer
        self.ctrl = ctrl
        self.space_dict = space_dict
        self.space_attr = 'Space'

        self.main()


    def main(self):

        cmds.addAttr(self.ctrl, ln=self.space_attr, at='enum', enumName=utils.helper.convert_enum_names(self.space_dict.keys()), k=True)

        offset_choice = cmds.createNode('choice', name=f'{self.base_name}_offset_CHOICE')
        space_choice = cmds.createNode('choice', name=f'{self.base_name}_driver_CHOICE')
        mmtx = cmds.createNode('multMatrix', name=f'{self.base_name}_result_MMTX')

        cmds.connectAttr(f'{self.ctrl}.{self.space_attr}', f'{offset_choice}.selector')
        cmds.connectAttr(f'{self.ctrl}.{self.space_attr}', f'{space_choice}.selector')

        for n, (label, space) in enumerate(self.space_dict.items()):
            offset_mat = utils.helper.get_offset_matrix(self.buffer, space)
            offset_attr = f'{self.base_name}_{label}_Offset'  # I added the base_name, because I encountered a failing point.
            cmds.addAttr(self.ctrl, ln=offset_attr, at='matrix')
            cmds.setAttr(f'{self.ctrl}.{offset_attr}', offset_mat, type='matrix')
            cmds.connectAttr(f'{self.ctrl}.{offset_attr}', f'{offset_choice}.input[{n}]')
            cmds.connectAttr(f'{space}.worldMatrix[0]', f'{space_choice}.input[{n}]')

        cmds.connectAttr(f'{offset_choice}.output', f'{mmtx}.matrixIn[0]')
        cmds.connectAttr(f'{space_choice}.output', f'{mmtx}.matrixIn[1]')
        cmds.connectAttr(f'{mmtx}.matrixSum', f'{self.buffer}.offsetParentMatrix')

        utils.helper.zero_out_transform(self.buffer)  # apparently this needs to be done at the end



class RotationSpaceSwitch:

    def __init__(self, base_name, buffer, ctrl, space_dict):
        self.base_name = base_name
        self.buffer = buffer
        self.ctrl = ctrl
        self.space_dict = space_dict
        self.space_attr = 'Rotation_Space'

        self.main()

    def main(self):

        cmds.addAttr(self.ctrl, ln=self.space_attr, at='enum', enumName=utils.helper.convert_enum_names(self.space_dict.keys()), k=True)

        offset_choice = cmds.createNode('choice', name=f'{self.base_name}_offset_CHOICE')
        space_choice = cmds.createNode('choice', name=f'{self.base_name}_driver_CHOICE')
        mmtx_result = cmds.createNode('multMatrix', name=f'{self.base_name}_result_MMTX')
        mmtx_base = cmds.createNode('multMatrix', name=f'{self.base_name}_base_MMTX')
        bm_result = cmds.createNode(f'blendMatrix', name=f'{self.base_name}_result_BM')

        cmds.connectAttr(f'{self.ctrl}.{self.space_attr}', f'{offset_choice}.selector')
        cmds.connectAttr(f'{self.ctrl}.{self.space_attr}', f'{space_choice}.selector')

        for n, (label, space) in enumerate(self.space_dict.items()):
            offset_mat = utils.helper.get_offset_matrix(self.buffer, space)
            offset_attr = f'{self.base_name}_{label}_Offset'  # I added the base_name, because I encountered a failing point.
            cmds.addAttr(self.ctrl, ln=offset_attr, at='matrix')
            cmds.setAttr(f'{self.ctrl}.{offset_attr}', offset_mat, type='matrix')
            cmds.connectAttr(f'{self.ctrl}.{offset_attr}', f'{offset_choice}.input[{n}]')
            cmds.connectAttr(f'{space}.worldMatrix[0]', f'{space_choice}.input[{n}]')

            # as the base case, which controls everything except what is switched upon (rotation), the first entry of the space dict will be used.
            if n == 0:
                cmds.connectAttr(f'{self.ctrl}.{offset_attr}', f'{mmtx_base}.matrixIn[0]')
                cmds.connectAttr(f'{space}.worldMatrix[0]', f'{mmtx_base}.matrixIn[1]')

        cmds.connectAttr(f'{offset_choice}.output', f'{mmtx_result}.matrixIn[0]')
        cmds.connectAttr(f'{space_choice}.output', f'{mmtx_result}.matrixIn[1]')
        cmds.connectAttr(f'{mmtx_result}.matrixSum', f'{bm_result}.inputMatrix')
        cmds.connectAttr(f'{mmtx_base}.matrixSum', f'{bm_result}.target[0].targetMatrix')
        cmds.setAttr(f'{bm_result}.target[0].rotateWeight', 0)

        cmds.connectAttr(f'{bm_result}.outputMatrix', f'{self.buffer}.offsetParentMatrix')
        utils.helper.zero_out_transform(self.buffer)



class Blender:
    """ This case is literally just a blendmatrix node. Sometimes it is an advantage to create the offsets manually to easily have access to them without going the route of a class. """

    def __init__(self, base_name, buffer, ctrl, base_space, space_dict):
        self.base_name = base_name
        self.buffer = buffer
        self.ctrl = ctrl
        self.base_space = base_space  # separated, because an alias for the base space is never used.
        self.space_dict = space_dict

        self.main()

    def main(self):

        bm = cmds.createNode('blendMatrix', name=f'{self.base_name}_switch_BM')

        cmds.connectAttr(f'{self.base_space}.worldMatrix[0]', f'{bm}.inputMatrix')

        for n, (blender, space) in enumerate(self.space_dict.items()):
            cmds.addAttr(self.ctrl, ln=blender, at='double', dv=0, min=0, max=1, k=True)
            cmds.connectAttr(f'{space}.worldMatrix[0]', f'{bm}.target[{n}].targetMatrix')
            cmds.connectAttr(f'{self.ctrl}.{blender}', f'{bm}.target[{n}].weight')

        cmds.connectAttr(f'{bm}.outputMatrix', f'{self.buffer}.offsetParentMatrix')
        utils.helper.zero_out_transform(self.buffer)





class OffsetBlender:

    def __init__(self, base_name, buffer, ctrl, space_dict):
        self.base_name = base_name
        self.buffer = buffer
        self.ctrl = ctrl
        self.space_dict = space_dict

        self.main()

    def main(self):

        bm = cmds.createNode('blendMatrix', name=f'{self.base_name}_switch_BM')

        for n, (alias, space) in enumerate(self.space_dict.items()):
            offset_mat = utils.helper.get_offset_matrix(transform1=self.buffer, transform2=space)
            mmat = cmds.createNode('multMatrix', name=f'{self.base_name}_{alias}_offset_MMAT')
            cmds.setAttr(f'{mmat}.matrixIn[0]', offset_mat, type='matrix')
            cmds.connectAttr(f'{space}.worldMatrix[0]', f'{mmat}.matrixIn[1]')

            if n == 0:  # the base case is the first entry of the dict
                cmds.connectAttr(f'{mmat}.matrixSum', f'{bm}.inputMatrix')
            else:
                # print(f'{n}: {alias}')
                cmds.addAttr(self.ctrl, ln=alias, at='double', min=0, max=1, dv=0, k=True)
                cmds.connectAttr(f'{mmat}.matrixSum', f'{bm}.target[{n-1}].targetMatrix')
                cmds.connectAttr(f'{self.ctrl}.{alias}', f'{bm}.target[{n-1}].weight')

        cmds.connectAttr(f'{bm}.outputMatrix', f'{self.buffer}.offsetParentMatrix')
        utils.helper.zero_out_transform(self.buffer)


    def set_blend_value(self, alias, value):
        cmds.setAttr(f'{self.ctrl}.{alias}', value)

















