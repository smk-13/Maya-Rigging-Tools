from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload


import archive.orient_joints_old
reload(archive.orient_joints_old)


def get_knots(crv_shape):
    """ copied over from ctl.utils. """
    sel = OpenMaya.MSelectionList()
    sel.add(crv_shape)  # just crv is probably fine
    obj = sel.getDependNode(0)
    if obj.hasFn(OpenMaya.MFn.kNurbsCurve):
        crv_fn = OpenMaya.MFnNurbsCurve(obj)
        return list(crv_fn.knots())


def get_u_param(pt, crv):
    """ pt = [float, float, float] """

    crv_obj = OpenMaya.MSelectionList().add(crv).getDependNode(0)
    crv_dgpa = OpenMaya.MDagPath.getAPathTo(crv_obj)
    crv_fn = OpenMaya.MFnNurbsCurve(crv_dgpa)
    return crv_fn.getParamAtPoint(OpenMaya.MPoint(pt), 0.001, OpenMaya.MSpace.kWorld)


def get_closest_u_param(pt, crv):
    """ """
    crv_obj = OpenMaya.MSelectionList().add(crv).getDependNode(0)
    crv_dgpa = OpenMaya.MDagPath.getAPathTo(crv_obj)
    crv_fn = OpenMaya.MFnNurbsCurve(crv_dgpa)
    closest_mpt = crv_fn.closestPoint(OpenMaya.MPoint(pt), 0.001, OpenMaya.MSpace.kWorld)[0]
    return crv_fn.getParamAtPoint(closest_mpt, 0.001, OpenMaya.MSpace.kWorld)


def get_pos_from_u_param(crv, u):
    """ crv is the name of the curve, u is a float representing the u_parameter. Returns a list [x,y,z]"""
    crv_obj = OpenMaya.MSelectionList().add(crv).getDependNode(0)
    crv_dgpa = OpenMaya.MDagPath.getAPathTo(crv_obj)
    crv_fn = OpenMaya.MFnNurbsCurve(crv_dgpa)
    mpt = crv_fn.getPointAtParam(u, OpenMaya.MSpace.kWorld)   
    return list(mpt)[:-1]  # MPoint has 4 coordinates x, y, z, w, the last one is not needed




def get_uv_param_surface(pt, surface):
    """ returns [u, v] """
    surface_obj = OpenMaya.MSelectionList().add(surface).getDependNode(0)
    surface_dgpa = OpenMaya.MDagPath.getAPathTo(surface_obj)
    surface_fn = OpenMaya.MFnNurbsSurface(surface_dgpa)
    return surface_fn.getParamAtPoint(OpenMaya.MPoint(pt), ignoreTrimBoundaries=False, tolerance=0.001, space=OpenMaya.MSpace.kWorld)


def get_closest_uv_param_surface(pt, surface):
    """ """
    surface_obj = OpenMaya.MSelectionList().add(surface).getDependNode(0)
    surface_dgpa = OpenMaya.MDagPath.getAPathTo(surface_obj)
    surface_fn = OpenMaya.MFnNurbsSurface(surface_dgpa)
    closest_mpt = surface_fn.closestPoint(OpenMaya.MPoint(pt), uStart=None, vStart=None, ignoreTrimBoundaries=False, tolerance=0.001, space=OpenMaya.MSpace.kWorld)[0]
    return surface_fn.getParamAtPoint(closest_mpt, False, 0.001, OpenMaya.MSpace.kWorld)





def get_offset_between_matrices(matrix_input1, matrix_input2):
    """ In a space switch input1 is the obj and input 2 are the different spaces. """
    mat1 = OpenMaya.MMatrix(matrix_input1) if isinstance(matrix_input1, (list, tuple)) else OpenMaya.MMatrix(cmds.xform(matrix_input1, q=True, ws=True, m=True))
    mat2 = OpenMaya.MMatrix(matrix_input2) if isinstance(matrix_input2, (list, tuple)) else OpenMaya.MMatrix(cmds.xform(matrix_input2, q=True, ws=True, m=True))
    mat2_inv = mat2.inverse()
    return list(mat1 * mat2_inv)



def get_closest_uv(loc, mesh):
    """ """
    mesh_obj = OpenMaya.MSelectionList().add(mesh).getDependNode(0)
    mesh_dgpa = OpenMaya.MDagPath.getAPathTo(mesh_obj)
    mesh_fn = OpenMaya.MFnMesh(mesh_dgpa)

    mpt = OpenMaya.MPoint(cmds.xform(loc, q=True, ws=True, t=True))

    return mesh_fn.getUVAtPoint(mpt)  # getUVAtPoint(point, space=MSpace.kObject, uvSet='') -> (float, float, int)


# def get_closest_uv_surface(loc, surface):
#     """ This doesn't work properly. """
#     surface_obj = OpenMaya.MSelectionList().add(surface).getDependNode(0)
#     surface_dgpa = OpenMaya.MDagPath.getAPathTo(surface_obj)
#     surface_fn = OpenMaya.MFnNurbsSurface(surface_dgpa)

#     mpt = OpenMaya.MPoint(cmds.xform(loc, q=True, ws=True, t=True))

#     # return surface_fn.getParamAtPoint(mpt)
#     return surface_fn.closestPoint(mpt)



def get_cpt_normal(loc, mesh):
    """ I use loc for something I can perform an xform on like a locator or vertex, I use pt for a position vector. """

    mesh_obj = OpenMaya.MSelectionList().add(mesh).getDependNode(0)
    mesh_dgpa = OpenMaya.MDagPath.getAPathTo(mesh_obj)
    mesh_fn = OpenMaya.MFnMesh(mesh_dgpa)

    mpt = OpenMaya.MPoint(cmds.xform(loc, q=True, ws=True, t=True))

    cpt_normal, cpt_fid = mesh_fn.getClosestNormal(mpt)  # getClosestNormal(MPoint, space=MSpace.kObject) -> (MVector, int)

    return cpt_normal, cpt_fid


def get_vtx_id(vtx):
    """ In Maya the vertex is something like 'head_skc.vtx[1463]'. """
    return int(vtx.rpartition(']')[0].rpartition('[')[2])

def get_vtx_mesh(vtx):
    """ In Maya the vertex is something like 'head_skc.vtx[1463]'. """
    return vtx.partition('.')[0]


def get_vtx_normal(vtx, mesh):

    mesh_obj = OpenMaya.MSelectionList().add(mesh).getDependNode(0)
    mesh_dgpa = OpenMaya.MDagPath.getAPathTo(mesh_obj)
    mesh_fn = OpenMaya.MFnMesh(mesh_dgpa)

    mvec = mesh_fn.getVertexNormal(get_vtx_id(vtx), False)  # getVertexNormal(vertexId, angleWeighted, space=MSpace.kObject) -> MVector

    return list(mvec)


def get_vtx_tangent(vtx, mesh, fid):

    mesh_obj = OpenMaya.MSelectionList().add(mesh).getDependNode(0)
    mesh_dgpa = OpenMaya.MDagPath.getAPathTo(mesh_obj)
    mesh_fn = OpenMaya.MFnMesh(mesh_dgpa)

    mvec = mesh_fn.getFaceVertexTangent(fid, get_vtx_id(vtx))

    return list(mvec)


def create_normal_aligned_transform_at_vtx(vtx, mesh, positive_aim=True, positive_up=True, enum=0, transform_type='joint'):
    """ For vtx at center lines the algorithm is confused. """

    if transform_type == 'joint':
        cmds.select(cl=True)
        loc = cmds.joint()
        cmds.setAttr(f'{loc}.radius', 0.3)
    elif transform_type == 'locator':
        loc = cmds.spaceLocator()[0]
    elif transform_type == 'transform':
        loc = cmds.createNode('transform')
    else:
        cmds.error('Unknown transform type. Pick joint, locator or transform.')

    cpt_normal, cpt_fid = get_cpt_normal(vtx, mesh)  # this is the alternative to get_vtx_normal, this has the advantage that I automatically get a face id
    vtx_normal = get_vtx_normal(vtx, mesh)  # not used right now, because the other method automatically gives me a face id for calculating the tangent vector (used as up vec)

    cpt_tangent = get_vtx_tangent(vtx, mesh, cpt_fid)

    mat = archive.orient_joints_old.calculate_aim_matrix(pos=[0,0,0], aim=cpt_normal, up=cpt_tangent, positive_aim=positive_aim, positive_up=positive_up, enum=enum)
    cmds.xform(loc, ws=True, m=mat)
    cmds.xform(loc, ws=True, t=cmds.xform(vtx, query=True, ws=True, t=True))  # this is the position vector

    if transform_type == 'joint':
        cmds.makeIdentity(loc, apply=True)

    return loc


def get_uv_orientation_of_vtx(vtx, mesh, positive_aim=True, positive_up=True, enum=0):
    cpt_normal, cpt_fid = get_cpt_normal(vtx, mesh)
    cpt_tangent = get_vtx_tangent(vtx, mesh, cpt_fid)
    mat = utils.orient_joints.calculate_aim_matrix(pos=[0,0,0], aim=cpt_normal, up=cpt_tangent, positive_aim=positive_aim, positive_up=positive_up, enum=enum)
    return mat



def get_pos_from_surface(surface, u, v):
    """ """
    surface_obj = OpenMaya.MSelectionList().add(surface).getDependNode(0)
    surface_dgpa = OpenMaya.MDagPath.getAPathTo(surface_obj)
    surface_fn = OpenMaya.MFnNurbsSurface(surface_dgpa)

    return list(surface_fn.getPointAtParam(u, v))[:-1]




