from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)




class Master:

    def __init__(self, masters, root):

        self.masters = masters

        utils.helper.check_if_objs_exist(objects=list(self.__dict__.values()))


        self.root = root

        self.create_hierarchy()
        self.set_hidden_attrs()

    def create_hierarchy(self):
        """ """
        parent = self.masters[0]
        for m in self.masters[1:]:
            cmds.parent(m, parent)
            parent = m

        if cmds.objExists(self.root):
            cmds.parent(self.root, self.masters[-1])

    def set_hidden_attrs(self):
        for m in self.masters[1:]:
            utils.helper.set_hidden_attrs(ctrl=m, hidden_attrs=['v', 'sx', 'sy', 'sz'])


