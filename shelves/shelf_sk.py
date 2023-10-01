from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import shelves.shelf_base
reload(shelves.shelf_base)


# copy to userSetup.py file (or run in script editor after every maya start up):
# from maya import cmds
# from importlib import reload
# import shelves.shelf_sk
# reload(shelves.shelf_sk)
# shelves.shelf_sk.sk_shelf(name='sk')


class sk_shelf(shelves.shelf_base._shelf):

    def build(self):
        self.addButton(label='LRA_on', command=self.lkaOn_cmd)
        self.addButton(label='LRA_off', command=self.lkaOff_cmd)
        self.addButton(label="CTRL", command=self.ctrl_cmd)
        self.addButton(label="Orient", command=self.orient_cmd)
        self.addButton(label="Skel", command=self.skel_cmd)


    def ctrl_cmd(self):
        """ """
        import UI.control_ui
        reload(UI.control_ui)
        UI.control_ui.ControlDialog()


    def orient_cmd(self):
        """ """
        import UI.orient_joints_ui
        reload(UI.orient_joints_ui)
        UI.orient_joints_ui.OrientJointsDialog()


    def skel_cmd(self):
        """ """
        import UI.skeleton_ui
        reload(UI.skeleton_ui)
        UI.skeleton_ui.SkeletonDialog()


    def lkaOn_cmd(self):
        all_joints = cmds.ls(type='joint')
        for jnt in all_joints:
            cmds.setAttr(f'{jnt}.displayLocalAxis', 1)


    def lkaOff_cmd(self):
        all_joints = cmds.ls(type='joint')
        for jnt in all_joints:
            cmds.setAttr(f'{jnt}.displayLocalAxis', 0)







