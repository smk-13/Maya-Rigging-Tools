from maya import cmds
from maya.api import OpenMaya
from importlib import reload

import shelves.shelf_base
reload(shelves.shelf_base)


# copy to userSetup.py file or run in script editor:
# import shelves.shelf_sk
# reload(shelves.shelf_sk)
# shelves.shelf_sk.sk_shelf(name='sk_shelf')


class sk_shelf(shelves.shelf_base._shelf):

    def build(self):
        self.addButton(label="init", command=self.init_cmd)
        self.addButton(label='joint', command=self.jnt_cmd)
        self.addButton(label='LRA_on', command=self.lkaOn_cmd)
        self.addButton(label='LRA_off', command=self.lkaOff_cmd)
        self.addButton(label="CTRL", command=self.ctrl_cmd)
        self.addButton(label="Orient", command=self.orient_cmd)
        self.addButton(label="Skel", command=self.skel_cmd)


    def init_cmd(self):
        """ """
        from maya import cmds
        from maya.api import OpenMaya
        from importlib import reload


    def ctrl_cmd(self):
        """ """
        import UI.control_ui
        reload(UI.control_ui)

        try:
            d1.close()
            d1.deleteLater()
        except:
            pass
        d1 = UI.control_ui.ControlDialog()
        d1.show()

    def orient_cmd(self):
        """ """
        import UI.orient_joints_ui
        reload(UI.orient_joints_ui)

        try:
            d2.close()
            d2.deleteLater()
        except:
            pass

        d2 = UI.orient_joints_ui.OrientJointsDialog()
        d2.show()

    def skel_cmd(self):
        """ """
        import UI.skeleton_ui
        reload(UI.skeleton_ui)

        try:
            d3.close()
            d3.deleteLater()
        except:
            pass
        d3 = UI.skeleton_ui.SkeletonDialog()
        d3.show()


    def jnt_cmd(self):
        cmds.select(cl=True)
        cmds.joint()
        cmds.select(cl=True)

    def lkaOn_cmd(self):
        all_joints = cmds.ls(type='joint')
        for jnt in all_joints:
            cmds.setAttr(f'{jnt}.displayLocalAxis', 1)

    def lkaOff_cmd(self):
        all_joints = cmds.ls(type='joint')
        for jnt in all_joints:
            cmds.setAttr(f'{jnt}.displayLocalAxis', 0)







