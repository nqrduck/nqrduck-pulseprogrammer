import logging
from collections import OrderedDict
from PyQt6.QtWidgets import QTableWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox
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
        title = QLabel("Pulse Sequence:")
        # Make title bold
        font = title.font()
        font.setBold(True)
        title.setFont(font)

        self.pulse_table = QTableWidget(self)
        self.pulse_table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
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

        # Add label for the event lengths
        event_parameters_label = QLabel("Event lengths:")
        event_parameters_label.setFont(font)
        layout.addStretch(1)
        layout.addWidget(event_parameters_label)

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
            event_name = dialog.get_length()
            logger.debug("Adding new event with name %s", event_name)
            self.module.model.add_event(event_name)

    @pyqtSlot()
    def on_events_changed(self):
        logger.debug("Updating events to %s", self.module.model.events)
        layout = self.layout()

        event = self.module.model.events[-1]
        logger.debug("Adding event to pulseprogrammer view: %s", event)
        # Create a label for the setting
        label = QLabel(event)
        label.setMinimumWidth(70)
        # Add an QLineEdit for the setting
        line_edit = QLineEdit(str(0))
        line_edit.setMinimumWidth(100)
        # Connect the editingFinished signal to the on_value_changed slot of the setting
        # line_edit.editingFinished.connect(lambda: setting.on_value_changed(line_edit.text()))
        # Add the label and the line edit to the layout
        event_layout = QHBoxLayout()
        event_layout.addWidget(label)
        event_layout.addWidget(line_edit)
        event_layout.addStretch(1)
        layout.addLayout(event_layout)

        self.pulse_table.setColumnCount(len(self.module.model.events))
        self.pulse_table.setHorizontalHeaderLabels(self.module.model.events)
        
        


class AddEventDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add Event")

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Enter event name:")
        self.length_input = QLineEdit()

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.length_input)
        self.layout.addWidget(self.buttons)

    def get_length(self):
        return self.length_input.text()        

        
