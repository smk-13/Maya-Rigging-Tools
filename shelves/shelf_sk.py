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

        self.addButton(label="CrvDes", command=self.curve_cmd)
        self.addButton(label="CrvSet", command=self.curve_set_cmd)
        self.addButton(label="Orient", command=self.orient_cmd)
        self.addButton(label="Skel", command=self.skel_cmd)
        self.addButton(label="Roll", command=self.roll_joints_cmd)
        



    def curve_cmd(self):
        import UI.curve_ui
        reload(UI.curve_ui)
        UI.curve_ui.CurveDialog()


    def orient_cmd(self):
        import UI.orient_joints_ui
        reload(UI.orient_joints_ui)
        UI.orient_joints_ui.OrientJointsDialog()


    def skel_cmd(self):
        """ """
        import UI.skeleton_ui
        reload(UI.skeleton_ui)
        UI.skeleton_ui.SkeletonDialog()


    def roll_joints_cmd(self):
        import UI.roll_joints_ui
        reload(UI.roll_joints_ui)
        UI.roll_joints_ui.RollJointsDialog()


    def curve_set_cmd(self):
        import UI.curve_set_ui
        reload(UI.curve_set_ui)
        UI.curve_set_ui.CurveSetDialog()









