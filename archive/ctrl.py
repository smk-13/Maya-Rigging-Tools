from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload


import utils.helper
reload(utils.helper)

import ctl.utils
reload(ctl.utils)




class Control:

    def __init__(self, base_name, shape='sphere', color=22, scale=1, hidden_attrs=None, offsets=None, target=None, position_only=False, parent=None, limits=None, hide=False):

        # naming
        self.base_name = base_name
        self.ctrl = f'{base_name}_ctl'
        self.offsets = [f'{base_name}_{token}' for token in ('grp', 'buffer')] if offsets is None else [f'{base_name}_{token}' for token in offsets]
        self.grp = self.ctrl if self.offsets == [] else self.offsets[0]

        # traits
        self.scale = scale
        self.color = color
        self.shape = shape
        self.hidden_attrs = ['v'] if hidden_attrs is None else hidden_attrs
        self.target = target
        self.position_only = position_only
        self.parent = parent
        self.limits = limits
        self.hide = hide

        self.instantiate_ctrl_shape()
        self.set_scale()
        self.set_color()
        self.set_hidden_attrs()
        self.create_offsets()
        self.match_transform()
        self.set_parent()
        self.set_limits()
        self.hide_ctrl()
        self.tag_as_ctrl()


    def instantiate_ctrl_shape(self):
        ctl.utils.create_new_curve(name=self.ctrl, shape=self.shape)

    def set_scale(self):
        cmds.xform(f'{self.ctrl}.cv[*]', os=True, r=True, scale=(self.scale, self.scale, self.scale))

    def set_color(self):
        for shp in cmds.listRelatives(self.ctrl, shapes=True):
            cmds.setAttr(f'{shp}.overrideEnabled', 1)
            cmds.setAttr(f'{shp}.overrideColor', self.color)

    def set_hidden_attrs(self):
        for attr in self.hidden_attrs:
            cmds.setAttr(f'{self.ctrl}.{attr}', lock=True, keyable=False, channelBox=False)

    def create_offsets(self):
        parent_offset = None
        for name in self.offsets:
            offset = cmds.createNode('transform', name=name)
            if parent_offset:
                cmds.parent(offset, parent_offset)
            parent_offset = offset
        if self.offsets != []:
            cmds.parent(self.ctrl, self.offsets[-1])

    def match_transform(self):
        if self.target:
            cmds.matchTransform(self.grp, self.target, position=True) if self.position_only else cmds.matchTransform(self.grp, self.target)
            # cmds.xform(self.grp, ws=True, m=cmds.xform(self.target, q=True, ws=True, m=True))

    def set_parent(self):
        if self.parent:
            cmds.parent(self.grp, self.parent)

    def set_limits(self):
        """ limits is a dict that needs to look like this: {'tx':[-1,1], 'etx': [True, True]} """
        if self.limits:
            cmds.transformLimits(self.ctrl, **self.limits)

    def hide_ctrl(self):
        """ """
        if self.hide:
            for shp in cmds.listRelatives(self.ctrl, shapes=True):
                cmds.setAttr(f'{shp}.visibility', 0)

    def tag_as_ctrl(self):
        """ """
        self.tag = cmds.createNode('controller', name=f'{self.ctrl}_tag')
        cmds.connectAttr(f'{self.ctrl}.message', f'{self.tag}.controllerObject')

    def create_annotation(self, jnt):
        """ """
        annotation_shp = cmds.annotate(self.ctrl, point=cmds.xform(jnt, query=True, ws=True, t=True), text='')
        cmds.parent(cmds.listRelatives(annotation_shp, parent=True)[0], self.ctrl)
        cmds.setAttr(f'{annotation_shp}.template', 1)
        cmds.connectAttr(f'{jnt}.worldMatrix[0]', f'{cmds.listRelatives(annotation_shp, parent=True)[0]}.offsetParentMatrix')
        utils.matrix.zero_out_transform(cmds.listRelatives(annotation_shp, parent=True)[0])
        cmds.rename(cmds.listRelatives(annotation_shp, parent=True)[0], f'{self.base_name}_annotation')  # do this at the end, because I don't reassign the name


    def place_along_pole_vector(self, elbow, distance):
        """ """
        shoulder_vec = OpenMaya.MVector(cmds.xform(cmds.listRelatives(elbow, parent=True)[0], query=True, ws=True, t=True))
        elbow_vec = OpenMaya.MVector(cmds.xform(elbow, query=True, ws=True, t=True))
        wrist_vec = OpenMaya.MVector(cmds.xform(cmds.listRelatives(elbow, children=True)[0], query=True, ws=True, t=True))

        arm_vec = wrist_vec - shoulder_vec
        upper_arm_vec = elbow_vec - shoulder_vec
        angle = arm_vec.angle(upper_arm_vec)
        mid_length = upper_arm_vec.length() * math.cos(angle)
        mid_dir = arm_vec.normal()
        mid_vec = shoulder_vec + mid_dir * mid_length
        dir_vec = (elbow_vec - mid_vec).normal()
        location_vec = elbow_vec + dir_vec * distance

        if angle == 0:
            cmds.matchTransform(self.grp, elbow)
            cmds.xform(self.grp, os=True, r=True, t=[0, -distance, 0])  # the orientaton that I like to use
            cmds.setAttr(f'{self.grp}.rx', 0)
            cmds.setAttr(f'{self.grp}.ry', 0)
            cmds.setAttr(f'{self.grp}.rz', 0)
        else:
            cmds.xform(self.grp, ws=True, t=location_vec )


    def add_counter_transform(self):
        """ This performs a full counter transformation. It requires 3 buffers not counting the top level grp offset, hence a minimum of 4 total. """
        if len(self.offsets) < 4:
            cmds.error('A full Countertransform requires 4 buffers. ')

        # not implemented yet




    def mirror_if_right_side(self, mirror_axis='X', right_side_token='R', left_side_token='L'):
        """ This is the new addition of the third implementation.
            The problem is that the target of the other side is usually not available. This function solves this problem by performing a search and replace action. 
            Since I only ever mirror to the right side, I can also inlcude the side checker here.
        """

        if self.base_name.partition('_')[0] == right_side_token:

            corresponding_target = self.ctrl.replace(f'{right_side_token}_', f'{left_side_token}_')  # sample ctrl, not jnt. This solves the pole vector script problem.

            # another option to reduce potential fails
            if not cmds.objExists(corresponding_target):
                corresponding_target = self.target.replace(f'{right_side_token}_', f'{left_side_token}_')

            temp_loc = cmds.createNode('transform', name=f'{self.base_name}_temp_loc')
            cmds.matchTransform(temp_loc, corresponding_target)  # I skip the option of position only for now

            temp_grp = cmds.createNode('transform', name=f'{self.base_name}_temp_grp')
            cmds.parent(temp_loc, temp_grp)
            cmds.setAttr(f'{temp_grp}.scale{mirror_axis}', -1)

            cmds.parent(temp_loc, w=True)

            cmds.delete(temp_grp)

            temp_loc_matrix = cmds.xform(temp_loc, query=True, ws=True, matrix=True)

            cmds.xform(self.grp, ws=True, matrix=temp_loc_matrix)

            cmds.delete(temp_loc)






