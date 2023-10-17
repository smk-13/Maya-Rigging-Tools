from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload

import logging
logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)





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






def add_float_attribute(attr_name, ctrls, dv_value=1, min_value=0, max_value=1, hasMinValue=True, hasMaxValue=True):
    """ Creates a float attr and proxies. """

    if not isinstance(ctrls, (list, tuple)):
        ctrls = [ctrls]

    cmds.addAttr(ctrls[0], ln=attr_name, at='double', dv=dv_value, min=min_value, max=max_value, k=True, hnv=hasMinValue, hxv=hasMaxValue)

    if len(ctrls) > 1:
        for ctrl in ctrls[1:]:
            cmds.addAttr(ctrl, proxy=f'{ctrls[0]}.{attr_name}', ln=attr_name, k=True)

    return attr_name, ctrls  # it passes through the attr name and returns ctrls always as a list


def add_enum_attrribute(attr_name, ctrls, enum_names):
    """ Creates an enum attr and proxies. """

    if not isinstance(ctrls, (list, tuple)):
        ctrls = [ctrls]

    cmds.addAttr(self.ctrl, ln=attr_name, at='enum', enumName=convert_enum_names(enum_names), k=True)

    if len(ctrls) > 1:
        for ctrl in ctrls[1:]:
            cmds.addAttr(ctrl, proxy=f'{ctrls[0]}.{attr_name}', ln=attr_name, k=True)

    return attr_name, ctrls  # it passes through the attr name and returns ctrls always as a list

def create_joint_and_match_transform(name, match, radius=1, parent=None, hide=True):
    """ Right now not compabtible for eyelid setup. This is the same as match move parent but for joints. """  
    cmds.select(cl=True)
    jnt = cmds.joint(name=name, radius=radius)
    cmds.matchTransform(jnt, match)
    cmds.makeIdentity(apply=True)  # I added this later
    if parent:
        cmds.parent(jnt, parent)
    if hide:
        cmds.setAttr(f'{jnt}.drawStyle', 2)
    return jnt


def create_joint_match_concatenate(name, match, radius=1, hide=True):
    """ """
    jnt = cmds.joint(name=name, radius=radius)
    cmds.matchTransform(jnt, match)
    cmds.makeIdentity(apply=True)
    if hide:
        cmds.setAttr(f'{jnt}.drawStyle', 2)
    return jnt


def create_joint_and_position(name, pos, radius=1, parent=None, hide=True):
    """ a version of the two functions above. """
    cmds.select(cl=True)
    jnt = cmds.joint(name=name, radius=radius)
    cmds.xform(jnt, ws=True, t=pos)
    cmds.makeIdentity(apply=True)
    if parent:
        cmds.parent(jnt, parent)
    if hide:
        cmds.setAttr(f'{jnt}.drawStyle', 2)
    return jnt


def create_joint_position_concatenate(name, pos, radius=1, hide=True):
    """ position instead of match """
    jnt = cmds.joint(name=name, radius=radius)
    cmds.xform(jnt, ws=True, t=pos)
    cmds.makeIdentity(apply=True)
    if hide:
        cmds.setAttr(f'{jnt}.drawStyle', 2)
    return jnt



def create_offsets(transform, base_name, offsets=['grp']):
    """ This seems to be complete shit. This is an old script, that is unstable. """
    has_parent = None
    buffers = []
    for off in offsets:
        buffer = cmds.createNode('transform', name=f'{base_name}_{off}')
        cmds.matchTransform(buffer, transform)
        if has_parent:
            cmds.parent(buffer, has_parent)
        has_parent = buffer
        buffers.append(buffer)
    old_parent = cmds.listRelatives(transform, parent=True)[0]
    cmds.parent(transform, buffers[-1])
    cmds.parent(buffers[0], old_parent)
    return buffers


def create_offset_joint(joint, name):
    """ Inserts another joint before the joint. This is what is needed for direct connections. """
    off_jnt = duplicate_single_joint(joint, name)
    parent_jnt = cmds.listRelatives(joint, parent=True)
    cmds.parent(joint, off_jnt)
    if parent_jnt:
        cmds.parent(off_jnt, parent_jnt)
    cmds.select(cl=True)
    return off_jnt

def create_offset_joint_downstream(joint, name):
    """ Inserts a joint after another joint and reparents its children to the new one. """
    off_jnt = duplicate_single_joint(joint, name)
    for c in cmds.listRelatives(joint, children=True):
        cmds.parent(c, off_jnt)
    cmds.parent(off_jnt, joint)
    cmds.select(cl=True)
    return off_jnt


def ik_handle(start_joint, end_joint, base_name, solver, parent=None):
    """ Creates an ik handle, renames the effector, hides the ik handle and parents the ikh. """
    ikh, eff = cmds.ikHandle(sj=start_joint, ee=end_joint, sol=solver, name=f'{base_name}_ikh')
    eff = cmds.rename(eff, f'{base_name}_eff')
    cmds.setAttr(f'{ikh}.visibility', 0)
    if parent:
        cmds.parent(ikh, parent)
    return ikh


def ik_spline(joint_chain, base_name):
    """ Creates an ik spline with a custom curve that is created based on a joint chain. 
        There is one very weird behaviour: if the start of the chain is parented to something, the curve is also parented to that thing instead of world.
    """
    crv = create_curve_along_joints(joint_chain=joint_chain, name=f'{base_name}_crv')
    ikh, eff = cmds.ikHandle(sj=joint_chain[0], ee=joint_chain[-1], sol='ikSplineSolver', name=f'{base_name}_ikh', curve=crv, createCurve=False)
    cmds.rename(eff, f'{base_name}_eff')
    cmds.setAttr(f'{ikh}.visibility', 0)
    cmds.setAttr(f'{crv}.visibility', 0)
    cmds.setAttr(f'{ikh}.inheritsTransform', 0)
    cmds.setAttr(f'{crv}.inheritsTransform', 0)
    return ikh, crv

def ik_spline_v2(joint_chain, base_name, spans):
    """ This time with the curve automatically simplified. The simplified curve shifts the jnts a little. """
    crv = create_curve_along_joints_v2(joint_chain=joint_chain, name=f'{base_name}_crv', spans=spans)
    ikh, eff = cmds.ikHandle(sj=joint_chain[0], ee=joint_chain[-1], sol='ikSplineSolver', name=f'{base_name}_ikh', curve=crv, createCurve=False)
    cmds.rename(eff, f'{base_name}_eff')
    cmds.setAttr(f'{ikh}.visibility', 0)
    cmds.setAttr(f'{crv}.visibility', 0)
    cmds.setAttr(f'{ikh}.inheritsTransform', 0)
    cmds.setAttr(f'{crv}.inheritsTransform', 0)
    return ikh, crv

def ik_spline_v3(joint_chain, base_name, crv):
    """ This time with a curve input"""
    ikh, eff = cmds.ikHandle(sj=joint_chain[0], ee=joint_chain[-1], sol='ikSplineSolver', name=f'{base_name}_ikh', curve=crv, createCurve=False)
    cmds.rename(eff, f'{base_name}_eff')
    cmds.setAttr(f'{ikh}.visibility', 0)
    cmds.setAttr(f'{crv}.visibility', 0)
    cmds.setAttr(f'{ikh}.inheritsTransform', 0)
    cmds.setAttr(f'{crv}.inheritsTransform', 0)
    return ikh


def create_curve_along_positions(positions, name, degree=3, parent=None, hide=False):
    """ This is a little bit more general than the function below. """
    crv = cmds.curve(ep=positions, name=name, degree=degree)
    crv = cmds.rebuildCurve(crv, keepRange=False, keepControlPoints=True, degree=degree)[0]  # This normalizes the curve
    cmds.rename(cmds.listRelatives(crv, shapes=True)[0], f'{crv}Shape')
    if parent:
        cmds.parent(crv, parent)
    if hide:
        cmds.setAttr(f'{crv}.visibility', 0)
    return crv


def create_curve_along_joints(joint_chain, name, degree=3, parent=None, hide=False):
    """ Creates a curve based on a joint chain. This also works for transforms and even vertices. For backwards comptability I don't change the name. """
    ep_list = [cmds.xform(i, query=True, ws=True, t=True) for i in joint_chain]
    crv = cmds.curve(ep=ep_list, name=name, degree=degree)
    crv = cmds.rebuildCurve(crv, keepRange=False, keepControlPoints=True, degree=degree)[0]  # This normalizes the curve
    cmds.rename(cmds.listRelatives(crv, shapes=True)[0], f'{crv}Shape')
    if parent:
        cmds.parent(crv, parent)
    if hide:
        cmds.setAttr(f'{crv}.visibility', 0)
    return crv


def create_curve_along_joints_with_offset(joint_chain, name, normal_axis=[0,0,2]):
    """ The amount of offset is implicit in the length of the normal_axis. """
    ep_list = list()
    temp_loc = cmds.spaceLocator()[0]
    for jnt in joint_chain:
        cmds.matchTransform(temp_loc, jnt)
        cmds.xform(temp_loc, r=True, os=True, t=normal_axis)
        temp_loc_pos = cmds.xform(temp_loc, query=True, ws=True, t=True)
        ep_list.append(temp_loc_pos)
    cmds.delete(temp_loc)
    crv = cmds.curve(ep=ep_list, name=name)
    crv = cmds.rebuildCurve(crv, keepRange=False, keepControlPoints=True)[0]  # This normalizes the curve
    cmds.rename(cmds.listRelatives(crv, shapes=True)[0], f'{crv}Shape')
    return crv


def create_ribbon_along_joints(joint_chain, name, normal_axis=[0,0,2], reverse_surface_normal=False, hide=True):
    """ Apparently u and v are flipped. U is along the short side and V along the long side. """
    temp_crv1 = create_curve_along_joints_with_offset(joint_chain=joint_chain, name='temp_crv1', normal_axis=normal_axis)
    temp_crv2 = create_curve_along_joints_with_offset(joint_chain=joint_chain, name='temp_crv2', normal_axis=[i * -1 for i in normal_axis])
    ribbon = cmds.loft(temp_crv1, temp_crv2, uniform=True, reverseSurfaceNormals=reverse_surface_normal, name=name, ch=False)[0]
    cmds.delete(temp_crv1, temp_crv2)
    if hide:
        cmds.setAttr(f'{ribbon}.visibility', 0)
    return ribbon




def create_curve_along_joints_v2(joint_chain, name, degree=3, parent=None, hide=False, spans=3):
    """ This rebuilds the created curve to a simpler curve. V2 simplifies the curve."""
    ep_list = [cmds.xform(i, query=True, ws=True, t=True) for i in joint_chain]
    crv = cmds.curve(ep=ep_list, name=name, degree=degree)
    crv = cmds.rebuildCurve(crv, keepRange=False, spans=spans, degree=degree)[0]  # keepRange set to 0 normalizes the curve
    cmds.rename(cmds.listRelatives(crv, shapes=True)[0], f'{crv}Shape')
    if parent:
        cmds.parent(crv, parent)
    if hide:
        cmds.setAttr(f'{crv}.visibility', 0)
    return crv


def create_curve_along_joints_with_offset_v2(joint_chain, name, normal_axis=[0,0,2], spans=4):
    """ The amount of offset is implicit in the length of the normal_axis. V2 simplifies the curve. """
    ep_list = list()
    temp_loc = cmds.spaceLocator()[0]
    for jnt in joint_chain:
        cmds.matchTransform(temp_loc, jnt)
        cmds.xform(temp_loc, r=True, os=True, t=normal_axis)
        temp_loc_pos = cmds.xform(temp_loc, query=True, ws=True, t=True)
        ep_list.append(temp_loc_pos)
    cmds.delete(temp_loc)
    crv = cmds.curve(ep=ep_list, name=name)
    crv = cmds.rebuildCurve(crv, keepRange=False, spans=spans)[0]  # This normalizes the curve
    cmds.rename(cmds.listRelatives(crv, shapes=True)[0], f'{crv}Shape')
    return crv


def create_ribbon_along_joints_v2(joint_chain, name, normal_axis=[0,0,2], spans=4, reverse_surface_normal=False, hide=True):
    """ Apparently u and v are flipped. U is along the short side and V along the long side. V2 simplifies the curve."""
    temp_crv1 = create_curve_along_joints_with_offset_v2(joint_chain=joint_chain, name='temp_crv1', normal_axis=normal_axis, spans=spans)
    temp_crv2 = create_curve_along_joints_with_offset_v2(joint_chain=joint_chain, name='temp_crv2', normal_axis=[i * -1 for i in normal_axis], spans=spans)
    ribbon = cmds.loft(temp_crv1, temp_crv2, uniform=True, reverseSurfaceNormals=reverse_surface_normal, name=name, ch=False)[0]
    cmds.delete(temp_crv1, temp_crv2)
    if hide:
        cmds.setAttr(f'{ribbon}.visibility', 0)
    return ribbon 





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

# IMPORTANT
def create_match_offset_parent(name, target, offset=[0,0,0], parent=None, position_only=False, locator=False):
    """ This is the newest version used in BNS """
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

# IMPORTANT
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






# OLD
def match_move_parent(obj, match=None, move=None, parent=None):
    """ This combo comes up frequently, e.g. for up and pole vectors. """
    if match:
        cmds.matchTransform(obj, match)
    if move:
        cmds.xform(obj, os=True, r=True, t=move)
    if parent:
        cmds.parent(obj, parent)

# OLD
def create_match_move_parent(name, match=None, move=None, parent=None, locator=False):
    """ Extension of the function above. Creates and positions an up locator. """
    up_loc = cmds.spaceLocator(name=name)[0] if locator else cmds.createNode('transform', name=name)
    if match:
        cmds.matchTransform(up_loc, match)
    if move:
        cmds.xform(up_loc, os=True, r=True, t=move)
    if parent:
        cmds.parent(up_loc, parent)
    return up_loc



def convert_enum_names(enum_names: list):
    """ Turns the list ['A, 'B', 'C'] into the string 'A:B:C' """
    enum = ''
    for i in enum_names:
        enum += f'{i}:'
    return enum[:-1]


def create_even_parameter_list(number, max_num=1):
    """ Returns an evenly spaced parameter list from 0 to max_num. """
    if number < 2:
        cmds.error('Number should be at least 2.')
    return [max_num / (number - 1) * i for i in range(number)]


def select_by_root_joint():
    root = cmds.ls(sl=True, type='joint')[0]
    sel = cmds.listRelatives(root, ad=True, type='joint')
    sel.append(root)
    sel.reverse()
    return sel


def calculate_mid_position(target_objects=None):
    selection = cmds.ls(selection=True, flatten=True) if target_objects is None else target_objects
    vec = OpenMaya.MVector()
    for i in selection:
        current_vec = OpenMaya.MVector(cmds.xform(i, query=True, ws=True, t=True))
        current_vec /= len(selection)  # division in OpenMaya
        vec += current_vec
    return vec

def place_joint_mid_position(target_objects=None):
    vec = calculate_mid_position(target_objects)
    cmds.select(cl=True)
    jnt = cmds.joint()
    cmds.xform(jnt, ws=True, t=vec)


def measure_distance():
    sel = cmds.ls(sl=True, flatten=True)
    vec0 = OpenMaya.MVector(cmds.xform(sel[0], query=True, ws=True, t=True))
    vec1 = OpenMaya.MVector(cmds.xform(sel[1], query=True, ws=True, t=True))
    result_vec = vec1 - vec0
    return result_vec.length()


def place_locator_at_pv_pos(name, joints=None, distance=50, scale=1):
    """ Using object space is probably a much simpler solution. The only downside is that one need to know which axis is which. """

    if joints is None:
        joints = cmds.ls(sl=True, type='joint')

    if len(joints) != 3:
        cmds.error('Select exactly three joints.')

    shoulder_vec = OpenMaya.MVector(cmds.xform(joints[0], query=True, ws=True, translation=True))
    elbow_vec = OpenMaya.MVector(cmds.xform(joints[1], query=True, ws=True, translation=True))
    wrist_vec = OpenMaya.MVector(cmds.xform(joints[2], query=True, ws=True, translation=True))

    arm_vec = wrist_vec - shoulder_vec
    upper_arm_vec = elbow_vec - shoulder_vec
    angle = arm_vec.angle(upper_arm_vec)
    mid_length = upper_arm_vec.length() * math.cos(angle)
    mid_dir = arm_vec.normal()
    mid_vec = shoulder_vec + mid_dir * mid_length
    dir_vec = (elbow_vec - mid_vec).normal()
    location_vec = elbow_vec + dir_vec * distance

    loc = cmds.spaceLocator()[0]
    cmds.xform(loc, ws=True, t=location_vec)
    loc_shp = cmds.listRelatives(loc, shapes=True)[0]
    cmds.setAttr(f'{loc_shp}.localScale', scale, scale, scale)
    loc = cmds.rename(loc, name)

    return loc

def create_loc_at_selected_position(scale=10):
    sel = cmds.ls(sl=True)[0]
    loc = cmds.spaceLocator()[0]
    loc_shp = cmds.listRelatives(loc, shapes=True)[0]
    cmds.setAttr(f'{loc_shp}.localScale', scale, scale, scale)
    cmds.xform(loc, ws=True, m=cmds.xform(sel, query=True, ws=True, m=True))


def create_inbetween_joints(joints=None, joint_count=4, disconnected=False, delete_old_joints=True):
    """ Number of joints includes start and end joint. """

    if joints is None:
        joints = cmds.ls(sl=True, type='joint')

    vec1 = OpenMaya.MVector(cmds.xform(joints[0], query=True, ws=True, t=True))
    vec2 = OpenMaya.MVector(cmds.xform(joints[1], query=True, ws=True, t=True))

    vec3 = vec2 - vec1
    length = vec3.length()
    segments = joint_count - 1
    seg_len = length / segments
    vec3_dir = vec3.normal()

    cmds.select(cl=True)
    for i in range(joint_count):
        if disconnected:
            cmds.select(cl=True)
        jnt = cmds.joint()
        vec4 = vec1 + vec3_dir * seg_len * i
        cmds.xform(jnt, ws=True, t=vec4)
        cmds.matchTransform(jnt, joints[0], rotation=True)

    if delete_old_joints:
        cmds.delete(joints)

def duplicate_selected_joint_chain(suffix, joints=None):
    # TO DO: Make the naming more flexible and let the naming function handle any naming convention

    if joints is None:
        joints = cmds.ls(sl=True, type='joint')

    parent = None
    cmds.select(cl=True)
    for jnt in joints:
        jnt = duplicate_single_joint(joint=jnt, name=f'{jnt}_{suffix}')
        if parent:
            cmds.parent(jnt, parent)
        parent = jnt

    cmds.select(cl=True)



# for organization

def create_blank_transform(name, parent=None):
    """ Creates a blank transform for outliner organization. Channelbox attrs are locked and hidden. """
    transform = cmds.createNode('transform', name=name) if not cmds.objExists(name) else name
    for attr in ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']:
        cmds.setAttr(f'{transform}.{attr}', lock=True, keyable=False, channelBox=False)
    if parent:
        cmds.parent(transform, parent)
    return transform


def lock_and_hide(transform, attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz', 'tx', 'ty', 'tz']):
    for attr in attrs:
        cmds.setAttr(f'{transform}.{attr}', lock=True, keyable=False, channelBox=False)








# maybe deprecated

def connect_decompose_node(transform):
    dcm = cmds.createNode('decomposeMatrix', name=f'{transform}_DM')
    cmds.connectAttr(f'{transform}.worldMatrix[0]', f'{dcm}.inputMatrix')
    return dcm


def create_vector_node_system(base_name, start_transform, end_transform):
    start_dcm = connect_decompose_node(transform=start_transform)
    end_dcm = connect_decompose_node(transform=end_transform)
    pma = cmds.createNode('plusMinusAverage', name=f'{base_name}_PMA')
    cmds.setAttr(f'{pma}.operation', 2)
    cmds.connectAttr(f'{start_dcm}.outputTranslate', f'{pma}.input3D[1]')
    cmds.connectAttr(f'{end_dcm}.outputTranslate', f'{pma}.input3D[0]')
    vp = cmds.createNode('vectorProduct', name=f'{base_name}_VP')
    cmds.setAttr(f'{vp}.operation', 0)
    cmds.setAttr(f'{vp}.normalizeOutput', 1)
    cmds.connectAttr(f'{pma}.output3D', f'{vp}.input1')
    return start_dcm, end_dcm, pma, vp


