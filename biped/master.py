from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)

import ctl.ctrl 
reload(ctl.ctrl)




class Master:

    def __init__(self):
        """ """
        self.masterCtlObj = ctl.ctrl.Control(base_name='master', color=22, shape='brackets',
            scale=45, offsets=[])
        self.master2CtlObj = ctl.ctrl.Control(base_name='master2', color=14, shape='circleY',
            scale=40, offsets=[], hidden_attrs=['v','sx','sy','sz'], parent=self.masterCtlObj.ctrl)
     

