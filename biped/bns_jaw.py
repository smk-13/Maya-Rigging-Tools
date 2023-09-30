from maya import cmds
from maya.api import OpenMaya
import math
from importlib import reload
import os


import utils.helper
reload(utils.helper)

import ctl.control 
reload(ctl.control)





class Jaw:

    def __init__(self):
        self.jaw_chain = ['jawBase', 'jaw_jnt', 'jaw_end']
        self.master = 'master2_ctl'
        self.head = 'head_jnt'

        self.main()

    def main(self):
        """ """

        self.jawCtlObj = ctl.ctrl.Control(base_name='jaw', shape='sphere', scale=1, color=22, hidden_attrs=['v', 'sx', 'sy', 'sz', 'rx', 'ry', 'rz'],
            target=self.jaw_chain[-1], parent=self.head)

        self.jaw_ikh = utils.helper.ik_handle(base_name='jaw', start_joint=self.jaw_chain[0], end_joint=self.jaw_chain[-1], solver='ikSCsolver', parent=self.jawCtlObj.ctrl)

