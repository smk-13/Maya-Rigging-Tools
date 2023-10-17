from maya import cmds
from maya.api import OpenMaya
from maya import OpenMayaUI
from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from importlib import reload

import ctl.control
import utils.helper
import ctl.utils
reload(ctl.control)
reload(utils.helper)
reload(ctl.utils)


def maya_main_window():
    maya_window_ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(int(maya_window_ptr), QtWidgets.QWidget)

# https://doc.qt.io/qtforpython-5/PySide2/QtCore/Qt.html#PySide2.QtCore.PySide2.QtCore.Qt.Key

class CustomListWidget(QtWidgets.QListWidget):

    enter_pressed = QtCore.Signal()
    delete_pressed = QtCore.Signal()

    def keyPressEvent(self, e):
        super().keyPressEvent(e)

        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.enter_pressed.emit()
        elif e.key() == QtCore.Qt.Key_Delete:
            self.delete_pressed.emit()


class CustomLineEdit(QtWidgets.QLineEdit):

    enter_pressed = QtCore.Signal()

    def keyPressEvent(self, e):
        super().keyPressEvent(e)

        if e.key() == QtCore.Qt.Key_Return or e.key() == QtCore.Qt.Key_Enter:
            self.enter_pressed.emit()


class ControlDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Control')
        self.setMaximumWidth(280)
        self.setMinimumWidth(280)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        
        self.line1 = QtWidgets.QLineEdit('C_test')
        self.line2 = QtWidgets.QLineEdit('ctl')
        self.line1.setMaximumWidth(100)
        self.line2.setMaximumWidth(100)

        self.comboBox1 = QtWidgets.QComboBox()
        self.comboBox1.setMaxVisibleItems(30)
        self.comboBox1.addItem('sphere', 'sphere')
        self.comboBox1.addItem('box', 'cube')
        self.comboBox1.addItem('box on base', 'cube_on_base')
        self.comboBox1.addItem('box arrow', 'cube_arrow')
        self.comboBox1.addItem('box arrow on base', 'cube_arrow_on_base')
        self.comboBox1.addItem('diamond', 'diamond')
        self.comboBox1.addItem('ornament', 'emblem')
        self.comboBox1.addItem('brackets', 'brackets')
        self.comboBox1.addItem('circle', 'circle')
        self.comboBox1.addItem('circle pointer', 'circle_pointer')
        self.comboBox1.addItem('circle arrow', 'circle_arrow')
        self.comboBox1.addItem('square', 'square')
        self.comboBox1.addItem('rectangle', 'rectangle')
        self.comboBox1.addItem('chamfered square', 'chamfered_square')
        self.comboBox1.addItem('rotate sphere', 'rotate_sphere_sk_v1')
        self.comboBox1.addItem('stepped square', 'stepped_square')
        self.comboBox1.addItem('stepped circle', 'stepped_circle')
        self.comboBox1.addItem('circle cross arrow', 'circle_cross_arrow')
        self.comboBox1.addItem('arrow', 'arrow')
        self.comboBox1.addItem('double arrow', 'double_arrow')
        self.comboBox1.addItem('locator', 'locator')
        self.comboBox1.addItem('pin', 'pin')
        self.comboBox1.addItem('pin2', 'pin2')
        self.comboBox1.addItem('dome', 'dome')
        self.comboBox1.addItem('4-star', 'star')
        self.comboBox1.addItem('8-star', '8_star')
        self.comboBox1.addItem('3-pyramide', 'three_sided_pyramide')
        self.comboBox1.addItem('4-pyramide', 'four_sided_pyramide')
        self.comboBox1.addItem('head', 'head')
        self.comboBox1.addItem('paw', 'paw')
        self.comboBox1.addItem('wave', 'wave')
        self.comboBox1.addItem('spine', 'spine')
        self.comboBox1.addItem('glasses', 'glasses')
        self.comboBox1.addItem('curved double arrow', 'curved_double_arrow')
        self.comboBox1.addItem('curved double arrow X', 'curved_double_arrow_X')
        self.comboBox1.addItem('curved arrow cross', 'curved_arrow_cross')
        self.comboBox1.addItem('closed eyelid', 'closed_eyelid')
        self.comboBox1.addItem('open eyelid', 'open_eyelid')
        self.comboBox1.addItem('cube arrow', 'cube_arrow')
        self.comboBox1.addItem('cube arrow on base', 'cube_arrow_on_base')
        self.comboBox1.addItem('Nyra_foot', 'Nyra_foot')
        self.comboBox1.addItem('Nyra_pelvis', 'Nyra_pelvis')
        self.comboBox1.addItem('Nyra_chest', 'Nyra_chest')
        self.comboBox1.addItem('Nyra_skirt2', 'Nyra_skirt2')
        self.comboBox1.addItem('shoulder_pad', 'shoulder_pad')
        self.comboBox1.addItem('Shinobi_armorPlate', 'Shinobi_armorPlate')
        self.comboBox1.addItem('sledgehammer', 'sledgehammer')
        self.comboBox1.addItem('Shinobi_head', 'Shinobi_head')
        self.comboBox1.addItem('Shinobi_armor', 'Shinobi_armor')
        self.comboBox1.addItem('curved_circle', 'curved_circle')



        self.comboBox1.insertSeparator(4)
        self.comboBox1.insertSeparator(11)

        self.comboBox2 = QtWidgets.QComboBox()
        self.comboBox2.addItem('Y', [0,0,0])
        self.comboBox2.addItem('X', [0,0,90])
        self.comboBox2.addItem('Z', [90,0,0])

        self.spinbox6 = QtWidgets.QDoubleSpinBox()
        self.spinbox6.setValue(0.0)
        self.spinbox6.setRange(-360, 360)
        self.spinbox6.setSingleStep(15.0)

        self.spinbox1 = QtWidgets.QSpinBox()
        self.spinbox1.setRange(0, 31)
        self.spinbox1.setValue(17)

        self.spinbox2 = QtWidgets.QDoubleSpinBox()
        self.spinbox2.setValue(1.0)
        self.spinbox2.setRange(-99, 99)
        self.spinbox2.setSingleStep(0.5)

        self.spinbox3 = QtWidgets.QDoubleSpinBox()
        self.spinbox3.setValue(1.0)
        self.spinbox3.setRange(-99, 99)
        self.spinbox3.setSingleStep(0.25)
        self.spinbox4 = QtWidgets.QDoubleSpinBox()
        self.spinbox4.setValue(1.0)
        self.spinbox4.setRange(-99, 99)
        self.spinbox4.setSingleStep(0.25)
        self.spinbox5 = QtWidgets.QDoubleSpinBox()
        self.spinbox5.setValue(1.0)
        self.spinbox5.setRange(-99, 99)
        self.spinbox5.setSingleStep(0.25)

        self.line3 = CustomLineEdit()

        self.list_wdg1 = CustomListWidget()
        self.list_wdg1.addItems(['grp', 'aim', 'off', 'offset'])
        self.list_wdg1.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.btn_up = QtWidgets.QPushButton('Up')
        self.btn_down = QtWidgets.QPushButton('Dn')
        self.btn_up.setMaximumWidth(25)
        self.btn_down.setMaximumWidth(25)

        self.btn_grp1 = QtWidgets.QButtonGroup()
        self.radio_btn1 = QtWidgets.QRadioButton('Match offset to selected object')
        self.radio_btn2 = QtWidgets.QRadioButton('Calculate pole vector location')
        self.btn_grp1.addButton(self.radio_btn1)
        self.btn_grp1.addButton(self.radio_btn2)
        self.radio_btn1.toggle()

        self.spinbox7 = QtWidgets.QDoubleSpinBox()
        self.spinbox7.setValue(20)
        self.spinbox7.setRange(0, 999)
        self.spinbox7.setSingleStep(10)

        self.btn_run = QtWidgets.QPushButton('Run')

    def create_layouts(self):
        
        main_layout = QtWidgets.QVBoxLayout(self)

        input_layout1 = QtWidgets.QHBoxLayout()
        input_layout1.addWidget(self.line3)
        input_layout1.addWidget(self.btn_up)
        input_layout1.addWidget(self.btn_down)

        axis_scale_layout = QtWidgets.QHBoxLayout()
        axis_scale_layout.addWidget(self.spinbox3)
        axis_scale_layout.addWidget(self.spinbox4)
        axis_scale_layout.addWidget(self.spinbox5)

        form_layout1 = QtWidgets.QFormLayout()
        form_layout1.addRow('Base Name', self.line1)
        form_layout1.addRow('Control Suffix', self.line2)
        form_layout1.addRow('Color Index', self.spinbox1)
        form_layout1.addRow('Shape', self.comboBox1)
        form_layout1.addRow('Orientation', self.comboBox2)
        form_layout1.addRow('Rotation', self.spinbox6)
        form_layout1.addRow('Uniform Scale', self.spinbox2)
        form_layout1.addRow('Axis Scale', axis_scale_layout)
        form_layout1.addRow('New Offset', input_layout1)

        btn_run_layout = QtWidgets.QHBoxLayout()
        btn_run_layout.addWidget(self.btn_run)
        btn_run_layout.addStretch()

        pv_layout = QtWidgets.QHBoxLayout()
        pv_layout.addWidget(self.radio_btn2)
        pv_layout.addWidget(self.spinbox7)

        main_layout.addLayout(form_layout1)
        main_layout.addWidget(self.list_wdg1)
        main_layout.addWidget(self.radio_btn1)
        main_layout.addLayout(pv_layout)
        main_layout.addLayout(btn_run_layout)

    def create_connections(self):
        self.line3.enter_pressed.connect(self.add_item_to_list)
        self.list_wdg1.delete_pressed.connect(self.remove_items_from_list)
        self.btn_up.clicked.connect(self.move_item_up)
        self.btn_down.clicked.connect(self.move_item_down)
        self.btn_run.clicked.connect(self.create_ctrl_command)

    # slots
    def add_item_to_list(self):
        item = self.line3.text()
        self.list_wdg1.addItem(item)

    def remove_items_from_list(self):
        selected_items = self.list_wdg1.selectedItems()
        for item in selected_items:
            row = self.list_wdg1.row(item)
            self.list_wdg1.takeItem(row)

    def move_item_up(self):
        current_row = self.list_wdg1.currentRow()
        current_item = self.list_wdg1.currentItem()
        self.list_wdg1.takeItem(current_row)
        self.list_wdg1.insertItem(current_row-1, current_item)
        self.list_wdg1.setCurrentItem(current_item)

    def move_item_down(self):
        current_row = self.list_wdg1.currentRow()
        current_item = self.list_wdg1.currentItem()
        self.list_wdg1.takeItem(current_row)
        self.list_wdg1.insertItem(current_row+1, current_item)
        self.list_wdg1.setCurrentItem(current_item)

    # main slot
    def create_ctrl_command(self):
        base_name = self.line1.text()
        if base_name == '':
            raise RuntimeError('Enter a base name.')

        ctrl_suffix = self.line2.text()

        full_ctrl_name = base_name if ctrl_suffix == '' else f'{base_name}_{ctrl_suffix}'
        if cmds.objExists(full_ctrl_name):
            raise RuntimeError('Control already exists. Pick another base name.')

        shape = self.comboBox1.currentData()
        color = self.spinbox1.value()
        scale = self.spinbox2.value()
        scale_components = [self.spinbox3.value(), self.spinbox4.value(), self.spinbox5.value()]
        offsets = [item.text() for item in self.list_wdg1.selectedItems()]

        initial_orientation = self.comboBox2.currentData()
        rotation_val = self.spinbox6.value()
        if initial_orientation == [0,0,0]:
            post_rotation = [0, rotation_val, 0]
        elif initial_orientation == [0,0,90]:
            post_rotation = [rotation_val, 0, 0]
        else:
            post_rotation = [0, 0, rotation_val]

        matching_object = cmds.ls(sl=True, flatten=True) if self.radio_btn1.isChecked() else None
        pole_vector_data = [cmds.ls(sl=True), self.spinbox7.value()] if self.radio_btn2.isChecked() and cmds.ls(sl=True) != [] else None

        ctrl_obj = ctl.control.Control(base_name=base_name, shape=shape, color=color, offsets=offsets, ctrl_suffix=ctrl_suffix,
            scale=scale, scale_components=scale_components, rotation=initial_orientation, matching_object=matching_object, pole_vector=pole_vector_data)

        ctrl_obj.rotate_shape(post_rotation)



class ShapeDialog(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super().__init__(parent)

        self.setWindowTitle('Shape')
        self.setMinimumWidth(250)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.line1 = QtWidgets.QLineEdit()
        self.line1.setPlaceholderText('Select curve and enter a name')
        self.btn1 = QtWidgets.QPushButton('Save')
        self.btn1.setMaximumWidth(40)

    def create_layouts(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.line1)
        main_layout.addWidget(self.btn1)

    def create_connections(self):
        self.btn1.clicked.connect(self.save_to_library)

    def save_to_library(self):
        crv = cmds.ls(sl=True)[0]
        if not cmds.objectType(cmds.listRelatives(crv, shapes=True)[0], isType='nurbsCurve'):
            raise RuntimeError('Not a curve.')
        name = self.line1.text()
        ctl.utils.save_to_lib(crv=crv, shape_name=name)







