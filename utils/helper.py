from maya import cmds
from maya.api import OpenMaya
import os




### general functions




def create_unique_name(base_name):
    """ if the name already exist, it increments until it finds a unique name. """
    count = 1
    new_name = base_name
    while cmds.objExists(new_name):
        new_name = f'{base_name}_{count}'
        count += 1
    return new_name

def convert_enum_names(enum_names: list):
    """ Turns the list ['A, 'B', 'C'] into the string 'A:B:C' """
    enum = ''
    for i in enum_names:
        enum += f'{i}:'
    return enum[:-1]

def create_even_parameter_list(number, max_num=1):
    """ Returns an evenly spaced parameter list from 0 to max_num,
        for exmaple: if number=5 and max_num=1, it returns [0, 0.25, 0.5, 0.75, 1] """
    if number < 2:
        cmds.error('Number should be at least 2.')
    return [max_num / (number - 1) * i for i in range(number)]


def select_by_root_joint():
    """ Returns the selected joint and all joints that sit below it in the hierarchy. """
    root = cmds.ls(sl=True, type='joint')[0]
    sel = cmds.listRelatives(root, ad=True, type='joint')
    if sel is None:
        sel = list()
    sel.append(root)
    sel.reverse()
    return sel

def ik_handle(start_joint, end_joint, base_name=None, solver='ikRPsolver'):
    """ Creates an ik handle, renames the effector, hides the ik handle and parents the ikh. """
    if base_name is None:
        base_name = end_joint
    ikh, eff = cmds.ikHandle(sj=start_joint, ee=end_joint, sol=solver, name=f'{base_name}_ikh')
    eff = cmds.rename(eff, f'{base_name}_eff')
    cmds.setAttr(f'{ikh}.visibility', 0)
    return ikh

def validate_path(path=None):
    """ Checks if the file already exists and provides a dialog to overwrite or not """
    if os.path.isfile(path):
        confirm = cmds.confirmDialog(title='Overwrite file?',
                                   message=f'The file {path} already exists. Do you want to overwrite it?',
                                   button=['Yes', 'No'],
                                   defaultButton='Yes',
                                   cancelButton='No',
                                   dismissString='No')
        if confirm == 'No':
            OpenMaya.MGlobal.displayInfo(f'The file {path} was not saved')
            # cmds.warning(f'The file {path} was not saved')
            return 0
    return 1



### used in biped class

def check_if_objs_exist(objects):
    """ checks if the objects exists in the Maya scene to run this function. """
    for obj in objects:
        if not isinstance(obj, (list, tuple)):
            obj = [obj]
        for element in obj:
            if not cmds.objExists(element):
                OpenMaya.MGlobal.displayInfo('At least one necessary object does not exist to run this function.')
                cmds.error()

def check_chain_length(chain, length):
    """ another layer of error checking to check the length of joint chain or FK control chains. """
    if len(chain) != length:
            OpenMaya.MGlobal.displayInfo(f'{chain} should have a length of {length} elements')
            cmds.error()        


def create_offsets(ctrl, tokens):
    """ """
    offsets = list()
    parent_offset = None
    for token in tokens:
        offset = cmds.createNode('transform', name=f'{ctrl}{token}')
        cmds.matchTransform(offset, ctrl)
        if parent_offset:
            cmds.parent(offset, parent_offset)
        parent_offset = offset
        offsets.append(offset)
    cmds.parent(ctrl, offsets[-1])
    return offsets

def set_hidden_attrs(ctrl, hidden_attrs):
    for attr in hidden_attrs:
        cmds.setAttr(f'{ctrl}.{attr}', lock=True, keyable=False, channelBox=False)







### joint creation tools

def calculate_mid_position(target_objects=None):
    """ This version is unstable. I should replace this at some point with the cluster hack. """
    selection = cmds.ls(selection=True, flatten=True) if target_objects is None else target_objects
    vec = OpenMaya.MVector()
    for i in selection:
        current_vec = OpenMaya.MVector(cmds.xform(i, query=True, ws=True, t=True))
        current_vec /= len(selection)  # division in OpenMaya
        vec += current_vec
    return vec






### matrix node functions

def zero_out_transform(transform_node):
    """ This is needed for matrix nodes based setups. """
    if cmds.objectType(transform_node, isType='joint'):
        cmds.joint(transform_node, edit=True, orientation=[0,0,0])
    cmds.xform(transform_node, os=True, m=list(OpenMaya.MMatrix()))
    cmds.setAttr(f'{transform_node}.inheritsTransform', 0)

def get_offset_matrix(transform1, transform2):
    mat1 = OpenMaya.MMatrix(cmds.xform(transform1, query=True, ws=True, matrix=True))
    mat2 = OpenMaya.MMatrix(cmds.xform(transform2, query=True, ws=True, matrix=True))
    mat2_inv = mat2.inverse()
    return list(mat1 * mat2_inv)

def create_direct_matrix_constraint(driver, driven):
    cmds.connectAttr(f'{driver}.worldMatrix[0]', f'{driven}.offsetParentMatrix')
    zero_out_transform(driven)



### different versions of duplicate joint chain

def duplicate_single_joint(joint, name=None, parent=None):
    if name is None:
        name = f'{joint}_copy'
    duplicate_joint = cmds.duplicate(joint, parentOnly=True, name=name)[0]
    if cmds.listRelatives(duplicate_joint, parent=True):
        cmds.parent(duplicate_joint, w=True)
    if parent:
        cmds.parent(duplicate_joint, parent)
    return duplicate_joint

def duplicate_joint_chain_v1(joint_chain, base_name, suffix, parent=None, hide=False):
    """ Appends a suffix to an iterated basename. """
    duplicate_chain = [duplicate_single_joint(jnt, name=f'{base_name}_{n}_{suffix}') for n, jnt in enumerate(joint_chain)]
    has_parent = None
    for jnt in duplicate_chain:
        if has_parent:
            cmds.parent(jnt, has_parent)
        has_parent = jnt
    if parent:
        cmds.parent(duplicate_chain[0], parent)
    if hide:
        for jnt in duplicate_chain:
            cmds.setAttr(f'{jnt}.visibility', 0)
    return duplicate_chain

def duplicate_joint_chain_v2(joint_chain, old_suffix, new_suffix, parent=None, hide=False):
    """ Replaces the old suffix with a new suffix. """
    duplicate_chain = [duplicate_single_joint(jnt, name=jnt.replace(old_suffix, new_suffix)) for jnt in joint_chain]
    has_parent = None
    for jnt in duplicate_chain:
        if has_parent:
            cmds.parent(jnt, has_parent)
        has_parent = jnt
    if parent:
        cmds.parent(duplicate_chain[0], parent)
    if hide:
        for jnt in duplicate_chain:
            cmds.setAttr(f'{jnt}.visibility', 0)
    return duplicate_chain

def duplicate_joint_chain_v3(joint_chain, suffix, parent=None, hide=False):
    """ Appends a suffix. """
    duplicate_chain = [duplicate_single_joint(jnt, name=f'{jnt}_{suffix}') for jnt in joint_chain]
    has_parent = None
    for jnt in duplicate_chain:
        if has_parent:
            cmds.parent(jnt, has_parent)
        has_parent = jnt
    if parent:
        cmds.parent(duplicate_chain[0], parent)
    if hide:
        for jnt in duplicate_chain:
            cmds.setAttr(f'{jnt}.visibility', 0)
    return duplicate_chain



### create/match/offset/parent combos

def create_match_offset_parent(name, target, offset=[0,0,0], parent=None, position_only=False, locator=False):
    """ """
    if locator:
        new_transform = cmds.spaceLocator(name=name)[0]
        cmds.setAttr(f'{new_transform}.localScaleX', 1)
        cmds.setAttr(f'{new_transform}.localScaleY', 1)
        cmds.setAttr(f'{new_transform}.localScaleZ', 1)
    else:
        new_transform = cmds.createNode('transform', name=name)
    cmds.matchTransform(new_transform, target, position=position_only)
    cmds.xform(new_transform, os=True, r=True, t=offset)
    if parent:
        cmds.parent(new_transform, parent)
    return new_transform

def create_offset_transform(name, position_target, rotation_target, joint=False, parent=None):
    """ Sometimes the position and the rotation are drawn from different sources. """
    if joint:
        cmds.select(cl=True)
        new_transform = cmds.joint(name=name)
    else:
        new_transform = cmds.createNode('transform', name=name)
    cmds.matchTransform(new_transform, position_target)
    cmds.matchTransform(new_transform, rotation_target, rotation=True)
    if parent:
        cmds.parent(new_transform, parent)
    return new_transform



### other

def create_equidistant_joint_chain(joints=None, joint_count=4):
    """ Number of joints includes start and end joint. """

    if joints is None:
        joints = cmds.ls(sl=True)  # shouldn't be restricted to joints

    vec1 = OpenMaya.MVector(cmds.xform(joints[0], query=True, ws=True, t=True))
    vec2 = OpenMaya.MVector(cmds.xform(joints[1], query=True, ws=True, t=True))

    vec3 = vec2 - vec1
    length = vec3.length()
    segments = joint_count - 1
    seg_len = length / segments
    vec3_dir = vec3.normal()

    cmds.select(cl=True)
    for i in range(joint_count):
        jnt = cmds.joint()
        vec4 = vec1 + vec3_dir * seg_len * i
        cmds.xform(jnt, ws=True, t=vec4)
        cmds.matchTransform(jnt, joints[0], rotation=True)


def measure_distance():
    sel = cmds.ls(sl=True, flatten=True)
    vec0 = OpenMaya.MVector(cmds.xform(sel[0], query=True, ws=True, t=True))
    vec1 = OpenMaya.MVector(cmds.xform(sel[1], query=True, ws=True, t=True))
    result_vec = vec1 - vec0
    return result_vec.length()

def optimize_constraint(constraint):
    """ """

    cnst_type = cmds.nodeType(constraint)
    cnst_obj = constraint.rpartition('_')[0]

    if cnst_type in ['parentConstraint', 'aimConstraint'] :
        cmds.disconnectAttr(f'{cnst_obj}.rotateOrder', f'{constraint}.constraintRotateOrder')
        cmds.disconnectAttr(f'{cnst_obj}.rotatePivot', f'{constraint}.constraintRotatePivot')
        cmds.disconnectAttr(f'{cnst_obj}.rotatePivotTranslate', f'{constraint}.constraintRotateTranslate')
    elif cnst_type == 'pointConstraint':
        cmds.disconnectAttr(f'{cnst_obj}.rotatePivot', f'{constraint}.constraintRotatePivot')
        cmds.disconnectAttr(f'{cnst_obj}.rotatePivotTranslate', f'{constraint}.constraintRotateTranslate')
    elif cnst_type == 'orientConstraint':
        cmds.disconnectAttr(f'{cnst_obj}.rotateOrder', f'{constraint}.constraintRotateOrder')

    cnst_obj_parent = cmds.listRelatives(cnst_obj, parent=True)
    if cnst_obj_parent:
        cmds.connectAttr(f'{cnst_obj_parent[0]}.worldInverseMatrix', f'{constraint}.constraintParentInverseMatrix', f=True)


def tag_as_ctrl(ctrl):
    """ """
    tag = cmds.createNode('controller', name=f'{ctrl}_tag')
    cmds.connectAttr(f'{ctrl}.message', f'{tag}.controllerObject')
    return tag