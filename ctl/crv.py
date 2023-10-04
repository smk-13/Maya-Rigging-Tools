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
SHAPE_SETS_LIBRARY_PATH = os.path.abspath(f'{CURRENT_DIRECTORY}\\shape_sets')



# TO DO: code works, but I may have to clean up the naming


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


def save_to_lib(crv, shape_name):
    """ get the shape data (with the get_shape function) and save it as a json file in the library. """
    path = os.path.join(SHAPE_LIBRARY_PATH, f'{shape_name}.json')

    shape_data = get_shape(shape_name)

    with open(path, 'w') as f:
        json.dump(shape_data, f, indent=4, sort_keys=True)
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


def create_new_curve_from_shape_data(name, shape_data):
    """ the shape data is directly passed in, instead of being read from the lib. """
    crv = cmds.createNode('transform', name=name)
    for i, crvShapeDict in enumerate(shape_data):
        tmpCrv = cmds.curve(**crvShapeDict)
        newShape = cmds.listRelatives(tmpCrv, shapes=True)[0]
        cmds.parent(newShape, crv, relative=True, shape=True)
        cmds.delete(tmpCrv)
        newShape = cmds.rename(newShape, f'{crv}Shape{i}')
    cmds.select(cl=True)
    return crv


def create_new_curve_from_lib(name, file_name):
    """ reads a dataset from the library and creates a completely new curve from it. """
    data = load_from_lib(shape=file_name)
    crv = create_new_curve_from_shape_data(name=name, shape_data=data)
    return crv






# SHAPE SETS

def get_shape_set(crvs=None):
    if crvs is None:
        crvs = cmds.ls(sl=True, type='transform')

    shape_set_list = list()

    for crv in crvs:
        crv_dict = dict()
        crv_dict['name'] = crv
        crv_dict['shape_data'] = get_shape(crv=crv)
        crv_dict['color'] = cmds.getAttr(f'{cmds.listRelatives(crv, shapes=True)[0]}.overrideColor')
        crv_dict['matrix'] = cmds.xform(crv, q=True, ws=True, matrix=True)
        shape_set_list.append(crv_dict)

    return shape_set_list


def save_shape_set_to_lib(file_name, crvs=None):
    """ """
    path = os.path.join(SHAPE_SETS_LIBRARY_PATH, f'{file_name}.json')

    shape_set_data = get_shape_set(crvs)

    with open(path, 'w') as f:
        json.dump(shape_set_data, f, indent=4, sort_keys=True)
        OpenMaya.MGlobal.displayInfo('Shape set successfully saved to library.')


def load_shape_set_from_lib(file_name):
    """ """
    path = os.path.join(SHAPE_SETS_LIBRARY_PATH, f'{file_name}.json')

    if os.path.isfile(path):
        with open(path, 'r') as f:
            return json.load(f)
    else:
        cmds.error(f'The file {path} doesn\'t exist.')


def create_shape_set_from_lib(file_name):
    shape_set_list = load_shape_set_from_lib(file_name)
    for data in shape_set_list:
        Shape(**data)


class Shape:

    def __init__(self, name, shape_data, color, matrix):
        self.name = name
        self.shape_data = shape_data
        self.color = color
        self.matrix = matrix

        self.create_new_curve()
        self.set_color()
        self.set_matrix()

    def create_new_curve(self):
        create_new_curve_from_shape_data(name=self.name, shape_data=self.shape_data)

    def set_color(self):
        for shp in cmds.listRelatives(self.name, shapes=True):
            cmds.setAttr(f'{shp}.overrideEnabled', 1)
            cmds.setAttr(f'{shp}.overrideColor', self.color)

    def set_matrix(self):
        cmds.xform(self.name, ws=True, matrix=self.matrix)


































