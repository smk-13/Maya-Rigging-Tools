from maya import cmds
from maya.api import OpenMaya

from itertools import permutations











def calculate_aim_matrix(pos, aim, up, positive_aim=True, positive_up=True, enum=0):
    """ Calculates the aim matrix from 3 positions.
        enum 0: aim_axis = X, up_axis = Z
        enum 1: aim_axis = X, up_axis = Y
        enum 2: aim_axis = Y, up_axis = Z
        enum 3: aim_axis = Z, up_axis = Y
        enum 4: aim_axis = Y, up_axis = X
        enum 5: aim_axis = Z, up_axis = X
    """

    if not isinstance(pos, (OpenMaya.MVector, list, tuple)):
        pos = cmds.xform(pos, q=True, ws=True, t=True)
    if not isinstance(aim, (OpenMaya.MVector, list, tuple)):
        aim = cmds.xform(aim, q=True, ws=True, t=True)
    if not isinstance(up, (OpenMaya.MVector, list, tuple)):
        up = cmds.xform(up, q=True, ws=True, t=True)

    aim_vec = OpenMaya.MVector(aim) - OpenMaya.MVector(pos) if positive_aim else OpenMaya.MVector(pos) - OpenMaya.MVector(aim)
    up_vec = OpenMaya.MVector(pos) - OpenMaya.MVector(up) if positive_up else OpenMaya.MVector(up) - OpenMaya.MVector(pos)

    aim_vec.normalize()
    up_vec.normalize()
    cross1 = aim_vec ^ up_vec
    cross2 = aim_vec ^ cross1
    cross1.normalize()
    cross2.normalize()

    # plug the 3 vectors (aim, cross1, cross2) into a 4 by 4 matrix in the order specified by the enum
    perm = list(permutations([list(i) for i in (aim_vec, cross1, cross2)]))[enum]

    mat_seq = list()
    for i in perm:
        i.append(0.0)
        mat_seq.extend(i)
    mat_seq.extend(pos)
    mat_seq.append(1.0)

    return OpenMaya.MMatrix(mat_seq)



def orient_single_joint(pos, aim, up, positive_aim=True, positive_up=True, enum=0):
    mat = calculate_aim_matrix(pos, aim, up, positive_aim, positive_up, enum)
    cmds.xform(pos, ws=True, m=mat)



def orient_joint_chain(joint_chain, positive_aim=True, positive_up=True, enum=0):
    """ This orients a joint chain with any length and without snapping. """



def orient_three_joints(joint_chain, positive_aim=True, positive_up=True, enum=0):
    """ Orients the first three joints of a joint chain and leaves the rest unchanged.
        This is useful for the arm leaving the finger joint chains unchanged.
    """

    parent_list = [cmds.listRelatives(i, parent=True) for i in joint_chain]
    for i in joint_chain:
        if cmds.listRelatives(i, parent=True) is not None:  # catches a warning
            cmds.parent(i, w=True)

    vec0 = OpenMaya.MVector(cmds.xform(joint_chain[0], query=True, ws=True, t=True))
    vec1 = OpenMaya.MVector(cmds.xform(joint_chain[1], query=True, ws=True, t=True))
    vec2 = OpenMaya.MVector(cmds.xform(joint_chain[2], query=True, ws=True, t=True))
    vec3 = vec1 - vec0
    vec4 = vec2 - vec1
    n_vec = vec3 ^ vec4

    for n, jnt in enumerate(joint_chain):
        if n == 2:
            cmds.matchTransform(jnt, joint_chain[1], rotation=True)
            cmds.makeIdentity(jnt, apply=True)
        elif n > 2:
            break
        else:
            current_vec = OpenMaya.MVector(cmds.xform(jnt, query=True, ws=True, t=True))
            up_vec = current_vec + n_vec.normal()

            cmds.xform(jnt, ws=True, m=calculate_aim_matrix(pos=jnt, aim=joint_chain[n+1], up=up_vec,
                                        positive_aim=positive_aim, positive_up=positive_up, enum=enum))
            cmds.makeIdentity(jnt, apply=True)

    for i, j in zip(joint_chain, parent_list):
        if j is not None:  # catches an error
            cmds.parent(i, j)

    cmds.select(cl=True)


def orient_joint_chain_and_snap(joint_chain, indices=[0,1,2], positive_aim=True, positive_up=True, enum=0):
    """ Pick 3 joints by their index to construct the plane. 
        This is useful for the leg or the finger joint chains.
    """

    # step 1: unparent all joints and store parent to reparent at the end of the function
    parent_list = [cmds.listRelatives(i, parent=True) for i in joint_chain]
    for i in joint_chain:
        if cmds.listRelatives(i, parent=True) is not None:  # catches a warning
            cmds.parent(i, w=True)

    # step 2: set up vectors
    vec0 = OpenMaya.MVector(cmds.xform(joint_chain[indices[0]], query=True, ws=True, t=True))
    vec1 = OpenMaya.MVector(cmds.xform(joint_chain[indices[1]], query=True, ws=True, t=True))
    vec2 = OpenMaya.MVector(cmds.xform(joint_chain[indices[2]], query=True, ws=True, t=True))
    vec3 = vec1 - vec0
    vec4 = vec2 - vec1
    n_vec = vec3 ^ vec4

    # step 3: snap all joints onto the plane
    for jnt in joint_chain:
        if jnt in [joint_chain[i] for i in indices]:  # the 3 joints that define the plane can be skipped
            continue

        # formula to calculate the shortest distance of a point to a plane
        current_vec = OpenMaya.MVector(cmds.xform(jnt, query=True, ws=True, t=True))
        distance = (current_vec - vec0) * n_vec / n_vec.length()

        # place at new position
        new_pos = current_vec - n_vec.normal() * distance
        cmds.xform(jnt, ws=True, t=new_pos)

    # step 4: orient all joints
    else:
        for n, jnt in enumerate(joint_chain):
            if jnt == joint_chain[-1]:  # the last joint is handled differently
                cmds.matchTransform(jnt, joint_chain[-2], rotation=True)
                cmds.makeIdentity(jnt, apply=True)
            else:
                current_vec = OpenMaya.MVector(cmds.xform(jnt, query=True, ws=True, t=True))
                up_vec = current_vec + n_vec.normal()

                cmds.xform(jnt, ws=True, m=calculate_aim_matrix(pos=jnt, aim=joint_chain[n+1], up=up_vec,
                                            positive_aim=positive_aim, positive_up=positive_up, enum=enum))
                cmds.makeIdentity(jnt, apply=True)

    # step 5: reparent all joints
    for i, j in zip(joint_chain, parent_list):
        if j is not None:  # catches an error
            cmds.parent(i, j)

    cmds.select(cl=True)



def orient_with_selection(positive_aim=True, positive_up=True, enum=0):
    """ This needs a revision. """

    cmds.selectPref(trackSelectionOrder=True)
    selection = cmds.ls(orderedSelection=True, flatten=True)
    pos = selection[0]
    aim = selection[1]
    up = selection[2]

    children = cmds.listRelatives(pos, children=True, type='transform')
    if children is None:
        children = []
    for child in children:
        cmds.parent(child, w=True)

    mat = calculate_aim_matrix(pos, aim, up, positive_aim, positive_up, enum)
    cmds.xform(pos, ws=True, m=mat)
    cmds.makeIdentity(pos, apply=True)

    for child in children:
        cmds.parent(child, pos)


def orient_joint_chain_with_maya_tools(joint_chain, oj='xyz', sao='xup'):
    for i in joint_chain:
        cmds.joint(i, e=True, oj='none') if i == joint_chain[-1] else cmds.joint(i, e=True, oj=oj, sao=sao)