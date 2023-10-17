from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)




def blend_switch(ctrl, space1, space2, transform, attr_name='lock'):
    """ usually space2 = world """
    cmds.addAttr(ctrl, ln=attr_name, at='double', dv=0, min=0, max=1, k=True)
    bm = cmds.createNode('blendMatrix', name=f'{transform}_BM')

    cmds.connectAttr(f'{space1}.worldMatrix[0]', f'{bm}.inputMatrix')
    cmds.connectAttr(f'{space2}.worldMatrix[0]', f'{bm}.target[0].targetMatrix')
    cmds.connectAttr(f'{bm}.outputMatrix', f'{transform}.offsetParentMatrix')
    cmds.connectAttr(f'{ctrl}.{attr_name}', f'{bm}.target[0].weight')

    utils.helper.zero_out_transform(transform_node=transform)




