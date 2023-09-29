from maya import cmds
from maya.api import OpenMaya


def create_single_joint():
	""" Creates a single joint and clears the current selection. """
	cmds.select(cl=True)
	jnt = cmds.joint()
	cmds.select(cl=True)
	return jnt


