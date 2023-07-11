import logging
import functools
from collections import OrderedDict
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox, QTableWidgetItem, QCheckBox
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_view import ModuleView

logger = logging.getLogger(__name__)


class PulseProgrammerView(ModuleView):
    
    def __init__(self, module):
        super().__init__(module)

        self.setup_ui()

        logger.debug("Connecting pulse parameter options changed signal to on_pulse_parameter_options_changed")
        self.module.model.pulse_parameter_options_changed.connect(self.on_pulse_parameter_options_changed)
        
    def setup_ui(self):
        # Create pulse table
        title = QLabel("Pulse Sequence: %s" % self.module.model.pulse_sequence.name)
        # Make title bold
        font = title.font()
        font.setBold(True)
        title.setFont(font)

        self.pulse_table = QTableWidget(self)
        self.pulse_table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.pulse_table.setAlternatingRowColors(True)
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        table_layout = QHBoxLayout()
        table_layout.addWidget(self.pulse_table)
        table_layout.addStretch(1)
        # Add button for new event
        self.new_event_button = QPushButton("New event")

        # Connect signals
        self.new_event_button.clicked.connect(self.on_new_event_button_clicked)
        self.module.model.events_changed.connect(self.on_events_changed)

        button_layout.addWidget(self.new_event_button)
        button_layout.addStretch(1)
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addLayout(table_layout)
        layout.addStretch(1)
        
        # Add label for the event lengths
        self.event_layout = QVBoxLayout()
        event_parameters_label = QLabel("Event lengths:")
        event_parameters_label.setFont(font)
        self.event_layout.addWidget(event_parameters_label)
        # self.event_layout.addStretch(1)
        
        layout.addLayout(self.event_layout)
        self.setLayout(layout)
        

    @pyqtSlot()
    def on_pulse_parameter_options_changed(self):
        logger.debug("Updating pulse parameter options to %s", self.module.model.pulse_parameter_options.keys())
        self.pulse_table.setRowCount(len(self.module.model.pulse_parameter_options))
        self.pulse_table.setVerticalHeaderLabels(self.module.model.pulse_parameter_options.keys())

    @pyqtSlot()
    def on_new_event_button_clicked(self):
        # Create a QDialog for the new event
        logger.debug("New event button clicked")
        dialog = AddEventDialog(self)
        result = dialog.exec()
        if result:
            event_name = dialog.get_name()
            logger.debug("Adding new event with name %s", event_name)
            self.module.model.add_event(event_name)

    @pyqtSlot()
    def on_events_changed(self):
        logger.debug("Updating events to %s", self.module.model.pulse_sequence.events)

        for event in self.module.model.pulse_sequence.events:
            logger.debug("Adding event to pulseprogrammer view: %s", event)
            # Create a label for the event
            event_name = QLabel(event)
            event_name.setMinimumWidth(70)
            # Add an QLineEdit for the event
            line_edit = QLineEdit(str(self.module.model.pulse_sequence.events[event].duration))
            line_edit.setMinimumWidth(30)
            # Add a label for the unit
            unit_label = QLabel("µs")
            # Connect the editingFinished signal to the on_value_changed slot of the setting
            # line_edit.editingFinished.connect(lambda: setting.on_value_changed(line_edit.text()))
            # Add the label and the line edit to the layout
            event_layout = QHBoxLayout()
            event_layout.addWidget(event_name)
            event_layout.addWidget(line_edit)
            event_layout.addWidget(unit_label)
            event_layout.addStretch(1)
        
        self.layout().addLayout(event_layout)

        self.pulse_table.setColumnCount(len(self.module.model.pulse_sequence.events))
        self.pulse_table.setHorizontalHeaderLabels(self.module.model.pulse_sequence.events)

        self.set_parameter_icons()

    def set_parameter_icons(self):
        for column_idx, event in enumerate(self.module.model.pulse_sequence.events):
            for row_idx, parameter in enumerate(self.module.model.pulse_parameter_options.keys()):
                logger.debug("Adding button for event %s and parameter %s with state %s", event, parameter, self.module.model.pulse_sequence.events[event].parameters[parameter].state)
                logger.debug("Parameter object id: %s", id(self.module.model.pulse_sequence.events[event].parameters[parameter]))
                button = QPushButton()
                icon = QIcon(self.module.model.pulse_sequence.events[event].parameters[parameter].get_pixmap())
                logger.debug("Icon size: %s", icon.availableSizes())
                button.setIcon(icon)
                button.setIconSize(icon.availableSizes()[0])
                button.setFixedSize(icon.availableSizes()[0])
                
                self.pulse_table.setCellWidget(row_idx, column_idx, button)
                self.pulse_table.setRowHeight(row_idx, icon.availableSizes()[0].height())
                self.pulse_table.setColumnWidth(column_idx, icon.availableSizes()[0].width())

                # Connect the button to the on_button_clicked slot
                func = functools.partial(self.on_button_clicked, event=event, parameter=parameter)
                button.clicked.connect(func)

    @pyqtSlot()
    def on_button_clicked(self, event, parameter):
        logger.debug("Button for event %s and parameter %s clicked", event, parameter)
        # Create a QDialog to set the options for the parameter.
        dialog = OptionsDialog(event, parameter, self)
        result = dialog.exec()

        if result:
            selection = dialog.return_func()
            logger.debug("Setting parameter %s of event %s to %s", parameter, event, selection)
            self.module.model.pulse_sequence.events[event].parameters[parameter].set_options(selection)
            self.set_parameter_icons()

class OptionsDialog(QDialog):
    def __init__(self, event, parameter, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Options")

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Change options for the pulse parameter: %s" % parameter)
        self.layout.addWidget(self.label)
        parameter = parent.module.model.pulse_sequence.events[event].parameters[parameter]
        
        options = parameter.get_options()

        # Based on these options we will now create our selection widget

        # If the options are a list , we will create a QComboBox
        if options[0] == list:
            pass
        # If the options are boolean, we will create a QCheckBox
        elif options[0] == bool:
            check_box = QCheckBox()

            def checkbox_result():
                return check_box.isChecked()

            check_box.setChecked(options[1])
            self.layout.addWidget(check_box)
            self.return_func = checkbox_result
        # If the options are a float/int we will create a QSpinBox
        elif options[0] == float or options[0] == int:
            pass
        # If the options are a string we will create a QLineEdit
        elif options[0] == str:
            pass

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        
    def return_func(self):
        return self.return_func

class AddEventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Event")

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Enter event name:")
        self.name_input = QLineEdit()

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.buttons)

    def get_name(self):
        return self.name_input.text()        

        
