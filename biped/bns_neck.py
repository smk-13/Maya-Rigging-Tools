from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload


import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)

import utils.switch
reload(utils.switch)



# This is again some nifty piece of engineering. Shit this is complicated.


class Neck:

    def __init__(self):
        """ """
        self.neck = 'neck_jnt'
        self.head = 'head_jnt'
        self.chest = 'chest_jnt'
        self.master = 'master2_ctl'

        self.ctl_dict = {
            'neck' : {'base_name': 'neck', 'shape': 'cube', 'scale': 3.5, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx'], 'color': 22},
            'headTilt': {'base_name': 'headTilt', 'shape': 'sphere', 'scale': 4.5, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'tx', 'ty', 'tz', 'rx', 'rz'], 'color': 22},
            'headAim': {'base_name': 'headAim', 'shape': 'sphere', 'scale': 2, 'hidden_attrs': ['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'], 'color': 22}
        }

        self.main()


    def main(self):
        """ """

        # three controllers
        self.neckCtlObj = ctl.ctrl.Control(target=self.neck, parent=self.chest, **self.ctl_dict['neck'], offsets=['grp'])
        self.headCtlObj = ctl.ctrl.Control(target=self.head, parent=self.neckCtlObj.ctrl, **self.ctl_dict['headTilt'], offsets=['grp'])
        self.headAimCtlObj = ctl.ctrl.Control(target=self.head, parent=self.master, **self.ctl_dict['headAim'], offsets=['grp'])
        cmds.xform(self.headAimCtlObj.grp, os=True, r=True, t=[0,40,0])

        cmds.parent(self.neck, self.neckCtlObj.ctrl)

        # for better outliner organization (alternatively the neck grp is just parented to the chest)
        cmds.parent(self.neckCtlObj.grp, self.master)
        cmds.parentConstraint(self.chest, self.neckCtlObj.grp, mo=True)

        # neck part
        head_driver = utils.helper.create_match_offset_parent(name='head_driver', target=self.headCtlObj.ctrl, parent=self.headCtlObj.ctrl)  # this thing needs a buffer

        cmds.aimConstraint(self.headAimCtlObj.ctrl, head_driver, worldUpType='objectrotation', aimVector=[0,1,0], upVector=[1,0,0], worldUpVector=[1,0,0],
            worldUpObject=self.headCtlObj.ctrl)

        neckFollow_mdl = cmds.createNode('multDoubleLinear', name='neck_follow_MDL')
        cmds.connectAttr(f'{head_driver}.rx', f'{neckFollow_mdl}.input1')
        cmds.setAttr(f'{neckFollow_mdl}.input2', 0.4)
        cmds.connectAttr(f'{neckFollow_mdl}.output', f'{self.neck}.rx')  # the neck inherits from the chest and then this rotation values is added on top from the head movement

        # v1: with orient constraint
        # cmds.orientConstraint(head_driver, self.head)  # is this bad? Why use an aim constraint?

        # v2: with aim constraint
        head_eff = utils.helper.create_match_offset_parent(name='head_eff', target=self.headCtlObj.ctrl, offset=[0,40,0], parent=head_driver)
        head_up = utils.helper.create_match_offset_parent(name='head_up', target=self.headCtlObj.ctrl, offset=[40,0,0], parent=head_driver)
        cmds.aimConstraint(head_eff, self.head, worldUpType='object', aimVector=[0,1,0], upVector=[1,0,0], worldUpVector=[1,0,0],
            worldUpObject=head_up)

        # space switch
        utils.switch.SpaceSwitch(base_name='headAim', buffer=self.headAimCtlObj.grp, ctrl=self.headAimCtlObj.ctrl, space_dict={'World': self.master, 'Chest': self.chest})

