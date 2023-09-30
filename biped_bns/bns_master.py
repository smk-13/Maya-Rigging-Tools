from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)





class Master:

    def __init__(self, name='RIG'):
        """ """
        self.name = name

        self.main()

    def main(self):

        self.RIG_grp = self.create_grp(name=self.name)
        self.masterCtlObj = ctl.ctrl.Control(base_name='master', color=22, shape='brackets', scale=45, offsets=[], parent=self.RIG_grp)
        self.master2CtlObj = ctl.ctrl.Control(base_name='master2', color=14, shape='circleY', scale=40, offsets=[], hidden_attrs=['v','sx','sy','sz'], parent=self.masterCtlObj.ctrl)
        self.geo_grp = self.create_grp(name='geo_grp', parent=self.RIG_grp)
        self.skeleton_grp = self.create_grp(name='skeleton_grp', parent=self.RIG_grp)
        self.constraint_grp = self.create_grp(name='constraint_grp', parent=self.RIG_grp)

        utils.helper.create_direct_matrix_constraint(driver=self.master2CtlObj.ctrl, driven=self.skeleton_grp)
        utils.helper.create_direct_matrix_constraint(driver=self.master2CtlObj.ctrl, driven=self.constraint_grp)

        self.create_global_scale_attr()

    def create_global_scale_attr(self):
        global_scale_attr = 'Global_Scale'
        cmds.addAttr(self.masterCtlObj.ctrl, ln=global_scale_attr, at='double', dv=1, min=0.01, max=100, k=True)
        for scale_channel in ['sx', 'sy', 'sz']:
            cmds.connectAttr(f'{self.masterCtlObj.ctrl}.{global_scale_attr}', f'{self.masterCtlObj.ctrl}.{scale_channel}')
            cmds.setAttr(f'{self.masterCtlObj.ctrl}.{scale_channel}', keyable=False, channelBox=False)

    def create_grp(self, name, parent=None):
        new_grp = cmds.createNode('transform', name=name) if not cmds.objExists(name) else name
        if parent:
            cmds.parent(new_grp, parent)
        return new_grp

