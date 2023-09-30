from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload
import os


import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)

import utils.switch
reload(utils.switch)


class Eyes:
    """ simple eye rig. This is literally the old system minus the eyelid. """

    def __init__(self):
        """ """
        self.L_eye = 'L_eye_jnt'
        self.R_eye = 'R_eye_jnt'
        self.master = 'master2_ctl'
        self.head = 'head_jnt'

        self.main()

    def main(self):
        """ """

        self.L_eyeCtlObj = ctl.ctrl.Control(base_name='L_eye', shape='circleZ', color=13, scale=1, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz', 'tz'], target=self.L_eye,)
        cmds.xform(self.L_eyeCtlObj.grp, os=True, r=True, t=[0,0,3])

        self.R_eyeCtlObj = ctl.ctrl.Control(base_name='R_eye', shape='circleZ', color=6, scale=1, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx',' ry', 'rz', 'tz'], target=self.R_eye)
        cmds.xform(self.R_eyeCtlObj.grp, os=True, r=True, t=[0,0,3])

        self.C_eyeCtlObj = ctl.ctrl.Control(base_name='eyesMain', shape='eyes_brackets', color=22, scale=0.08, hidden_attrs=['v','sx','sy','sz','rx','ry','rz'], parent=self.master)
        cmds.xform(self.C_eyeCtlObj.grp, ws=True, t=utils.helper.calculate_mid_position(target_objects=[self.L_eyeCtlObj.ctrl, self.R_eyeCtlObj.ctrl]))

        cmds.parent(self.L_eyeCtlObj.grp, self.C_eyeCtlObj.ctrl)
        cmds.parent(self.R_eyeCtlObj.grp, self.C_eyeCtlObj.ctrl)

        cmds.aimConstraint(self.L_eyeCtlObj.ctrl, self.L_eye, worldUpType='none', aimVector=[0,0,1])
        cmds.aimConstraint(self.R_eyeCtlObj.ctrl, self.R_eye, worldUpType='none', aimVector=[0,0,1])

        utils.switch.SpaceSwitch(base_name='eyes', buffer=self.C_eyeCtlObj.grp, ctrl=self.C_eyeCtlObj.ctrl, space_dict={'Head': self.head, 'World': self.master})
