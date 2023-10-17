from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import utils.helper
reload(utils.helper)

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
        self.addButton(label="Skel", command=self.skel_cmd)
        self.addButton(label="Orient", command=self.orient_cmd)
        self.addButton(label="Roll", command=self.roll_joints_cmd)
        self.addButton(label="Joints", command=self.create_joints_cmd)
        self.addButton(label="Offset", command=self.create_offsets_cmd)
        self.addButton(label="Biped", command=self.biped_cmd)
        

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


    def create_offsets_cmd(self):
        sel = cmds.ls(sl=True, type='transform')
        if sel == []:
            OpenMaya.MGlobal.displayInfo('Select one or more controller curves.')
        for ctrl in sel:
            utils.helper.create_offsets(ctrl=ctrl, tokens=['Grp'])


    def biped_cmd(self):
        import UI.biped_ui
        reload(UI.biped_ui)
        UI.biped_ui.BipedDialog()


    def create_joints_cmd(self):
        import UI.create_joints_ui
        reload(UI.create_joints_ui)
        UI.create_joints_ui.CreateJointsDialog()



