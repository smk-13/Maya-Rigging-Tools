# Rigging Toolkit for Maya

## Installation
Copy the Maya_Rigging_Tools folder anywhere you want and add PYTHONPATH = [insert your path] to the maya.env file. The maya.env file usually located at C:\Users\NAME\Documents\maya\YEAR.

Then add the following lines to the userSetup.py file:

```python
    from maya import cmds
    from maya.api import OpenMaya
    from importlib import reload
    cmds.evalDeferred('import shelves.shelf_sk')
    cmds.evalDeferred('shelves.shelf_sk.sk_shelf(name=\'sk_toolkit\')')
```

The userSetup.py file is also in the maya scripts folder. In a fresh Maya installation the userSetup.py file doesn't exist. In that case, create a new one.

## Documentation

The shelf has eight dialogboxes:
* CrvDes
* CrvSet
* Skel
* Orient
* Roll
* Joints
* Offset
* Biped

### CrvDes, CrvSet and Skel
*CrvDes* is a curve creation tool to load and save controller curves; *CrvSet* loads and saves sets of controller curves, and *Skel* loads and saves set of joints and joint chains. The data is stored in JSON files. If you click on the library button, it opens the library folder in the filebrowser containing the JSON files. From here you can rename and delete them or just check what is available. If you click on the config button, it opens the JSON file that configures the dropdown menu. It contains a dictionary with keys being the label shown in the dialogbox and the values being the filename of a JSON file in the library without the JSON file extension. Reopen the dialogbox to update.

### Orient
*Orient* extends Mayas orient joint chain toolset. It orients a 3-joints joint chain such that one axis is perpendicular to the plane these three joints define. This is needed for proper IK setups. The tool is set to root joint selection, e.g. if you have a joint chain of hip, knee and ankle, only select the hip.

### Roll
*Roll* creates roll joints. This is a so called no flip setup using aim constraints with their up type set to None.

### Biped
*Biped* creates subcomponents of a full biped rigging system. Most importantly, the spine and neck rig setups used here are reverse engineered from Bandai Namco's free BNS Rig (with some minor changes). You can find a link to the BNS Rig here: [BNS Rig](https://kunanim.wordpress.com/2020/06/06/ridicule-is-nothing-to-be-scared-of/). If you want to test the rigs out, you can load the sample skeleton and the sample curve sets from the library and then run the rig setups from the biped dialogbox.














