from maya import cmds
from maya.api import OpenMaya
from importlib import reload




def _null(*args):
    pass


class Shelf_sk:

    def __init__(self, name='customShelf', iconPath=''):

        self.name = name
        self.iconPath = iconPath
        self.labelBackground = (0, 0, 0, 0)
        self.labelColour = (.9, .9, .9)

        self._cleanOldShelf()
        cmds.setParent(self.name)
        self.build()

    def _cleanOldShelf(self):
        if cmds.shelfLayout(self.name, ex=1):
            if cmds.shelfLayout(self.name, q=1, ca=1):
                for each in cmds.shelfLayout(self.name, q=1, ca=1):
                    cmds.deleteUI(each)
        else:
            cmds.shelfLayout(self.name, p="ShelfLayout")


    def addButton(self, label, icon="commandButton.png", command=_null, doubleCommand=_null):
        cmds.setParent(self.name)
        if icon:
            icon = self.iconPath + icon
        cmds.shelfButton(width=37, height=37, image=icon, l=label, command=command,
            dcc=doubleCommand, imageOverlayLabel=label, olb=self.labelBackground,
            olc=self.labelColour)


    def build(self):
        self.addButton('CTRL', command=self.ctrl_cmd)
        self.addButton('Orient')
        self.addButton('Skel')



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
        """" """
        

    def skel_cmd(self):
        """ """