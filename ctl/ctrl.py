from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload
import os
import json

import utils.helper
reload(utils.helper)

CURRENT_DIRECTORY = os.path.dirname(__file__)
SHAPE_LIBRARY_PATH = os.path.abspath(f'{CURRENT_DIRECTORY}\\shapes')





def get_knots(crv_shape):
    sel = OpenMaya.MSelectionList()
    sel.add(crv_shape)
    obj = sel.getDependNode(0)
    if obj.hasFn(OpenMaya.MFn.kNurbsCurve):
        crv_fn = OpenMaya.MFnNurbsCurve(obj)
        return list(crv_fn.knots())


def get_shape(crv):
    """ returns a dataset to create a shape. Each shape can be represented by a dictionary with the
    following four keys: degree, knot, periodic and point. To account for composite shapes the
    the dataset returned by this function is a list of such dictionaries. """

    crvShapeList = list()

    for shp in cmds.listRelatives(crv, shapes=True):
        crvShapeDict = {
            'degree': cmds.getAttr(f'{shp}.degree'),
            'knot': get_knots(shp)
        }

        crvShapeDict['periodic'] = True if (cmds.getAttr(f'{shp}.form')) == 2 else False

        points = []
        for i in range(cmds.getAttr(f'{shp}.controlPoints', size=True)):
            points.append(cmds.getAttr(f'{shp}.controlPoints[{i}]')[0])
        crvShapeDict['point'] = points

        crvShapeList.append(crvShapeDict)

    return crvShapeList


def set_shape(crv, crvShapeList):
    """ deletes all shape nodes of a transform node and creates a set of new shapes for it.
        The color of the old shapes is retained.
    """
    if not cmds.objExists(crv):
        cmds.error('curve doesn\'t exist.')

    crvShapes = cmds.listRelatives(crv, shapes=True)

    oldColor = cmds.getAttr(f'{crvShapes[0]}.overrideColor')
    cmds.delete(crvShapes)

    for i, crvShapeDict in enumerate(crvShapeList):
        tmpCrv = cmds.curve(**crvShapeDict)
        newShape = cmds.listRelatives(tmpCrv, shapes=True)[0]
        cmds.parent(newShape, crv, relative=True, shape=True)
        cmds.delete(tmpCrv)
        newShape = cmds.rename(newShape, f'{crv}Shape{i}')
        cmds.setAttr(f'{newShape}.overrideEnabled', 1)
        cmds.setAttr(f'{newShape}.overrideColor', oldColor)
    cmds.select(cl=True)



def save_to_lib(crv, shape_name):
    """ get the shape data (with the get_shape function) and save it as a json file in the library. """
    path = os.path.join(SHAPE_LIBRARY_PATH, f'{shape_name}.json')

    with open(path, 'w') as f:
        json.dump(get_shape(shape_name), f, indent=4, sort_keys=True)
        OpenMaya.MGlobal.displayInfo('Shape successfully saved to library.')

    # TO DO: override warning


def load_from_lib(shape):
    """ returns the shape data from a json shape file of the library. """
    path = os.path.join(SHAPE_LIBRARY_PATH, f'{shape}.json')

    if os.path.isfile(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        cmds.error(f'The file {path} doesn\'t exist.')


def initialize_new_curve(name, shape):
    """ reads a dataset from the library and creates a completely new curve from it. """
    data = load_from_lib(shape=shape)
    crv = cmds.createNode('transform', name=name)
    for i, crvShapeDict in enumerate(data):
        tmpCrv = cmds.curve(**crvShapeDict)
        newShape = cmds.listRelatives(tmpCrv, shapes=True)[0]
        cmds.parent(newShape, crv, relative=True, shape=True)
        cmds.delete(tmpCrv)
        newShape = cmds.rename(newShape, f'{crv}Shape{i}')
    cmds.select(cl=True)
    return crv







class Control:

    def __init__(self, base_name, shape='sphere', color=22, scale=1, hidden_attrs=None,
        offsets=None, target=None, position_only=False, parent=None, limits=None, hide=False):

        self.base_name = base_name
        self.ctrl = f'{base_name}_ctl'
        self.offsets = [f'{base_name}_{token}' for token in ('grp', 'buffer')] if offsets is None else [f'{base_name}_{token}' for token in offsets]
        self.grp = self.ctrl if self.offsets == [] else self.offsets[0]

        self.scale = scale
        self.color = color
        self.shape = shape
        self.hidden_attrs = ['v'] if hidden_attrs is None else hidden_attrs
        self.target = target
        self.position_only = position_only
        self.parent = parent
        self.limits = limits
        self.hide = hide

        self.create_ctrl_shape()
        self.set_scale()
        self.set_color()
        self.set_hidden_attrs()
        self.create_offsets()
        self.match_transform()
        self.set_parent()
        self.set_limits()
        self.hide_ctrl()
        self.tag_as_ctrl()


    def create_ctrl_shape(self):
        initialize_new_curve(name=self.ctrl, shape=self.shape)

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

    def set_parent(self):
        if self.parent:
            cmds.parent(self.grp, self.parent)

    def set_limits(self):
        """ limits is a dict that needs to look like this: {'tx':[-1,1], 'etx': [True, True]} """
        if self.limits:
            cmds.transformLimits(self.ctrl, **self.limits)

    def hide_ctrl(self):
        if self.hide:
            for shp in cmds.listRelatives(self.ctrl, shapes=True):
                cmds.setAttr(f'{shp}.visibility', 0)

    def tag_as_ctrl(self):
        self.tag = cmds.createNode('controller', name=f'{self.ctrl}_tag')
        cmds.connectAttr(f'{self.ctrl}.message', f'{self.tag}.controllerObject')

    def create_annotation(self, jnt):
        annotation_shp = cmds.annotate(self.ctrl, point=cmds.xform(jnt, query=True, ws=True, t=True), text='')
        cmds.parent(cmds.listRelatives(annotation_shp, parent=True)[0], self.ctrl)
        cmds.setAttr(f'{annotation_shp}.template', 1)
        cmds.connectAttr(f'{jnt}.worldMatrix[0]', f'{cmds.listRelatives(annotation_shp, parent=True)[0]}.offsetParentMatrix')
        utils.matrix.zero_out_transform(cmds.listRelatives(annotation_shp, parent=True)[0])
        cmds.rename(cmds.listRelatives(annotation_shp, parent=True)[0], f'{self.base_name}_annotation')  # do this at the end, because I don't reassign the name


    def place_along_pole_vector(self, elbow, distance):
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






