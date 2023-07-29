import logging
import functools
from collections import OrderedDict
from pathlib import Path
from decimal import Decimal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox, QGroupBox, QFormLayout, QTableWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QDialog, QLineEdit, QDialogButtonBox, QWidget, QCheckBox, QToolButton, QFileDialog, QSizePolicy
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from nqrduck.module.module_view import ModuleView
from nqrduck_spectrometer.pulseparameters import BooleanOption, NumericOption, FunctionOption

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

        # Table setup
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
        self.new_event_button.clicked.connect(self.on_new_event_button_clicked)
        button_layout.addWidget(self.new_event_button)

        # Add button for save pulse sequence
        self.save_pulse_sequence_button = QPushButton("Save pulse sequence")
        self.save_pulse_sequence_button.clicked.connect(self.on_save_button_clicked)
        button_layout.addWidget(self.save_pulse_sequence_button)
       
        # Add button for load pulse sequence
        self.load_pulse_sequence_button = QPushButton("Load pulse sequence")
        self.load_pulse_sequence_button.clicked.connect(self.on_load_button_clicked)
        button_layout.addWidget(self.load_pulse_sequence_button)

        # Connect signals
        self.module.model.events_changed.connect(self.on_events_changed)

        
        button_layout.addStretch(1)
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addLayout(table_layout)
        layout.addStretch(1)
        
        self.setLayout(layout)

        # Add layout for the event lengths
        self.event_widget = QWidget()
        self.layout().addWidget(self.event_widget)

        self.on_events_changed()
        

    @pyqtSlot()
    def on_pulse_parameter_options_changed(self):
        logger.debug("Updating pulse parameter options to %s", self.module.model.pulse_parameter_options.keys())
        # We set it to the length of the pulse parameter options + 1 because we want to add a row for the parameter option buttons
        self.pulse_table.setRowCount(len(self.module.model.pulse_parameter_options) + 1)
        # Move the vertical header labels on row down
        pulse_options = [""]
        pulse_options.extend(list(self.module.model.pulse_parameter_options.keys()))
        self.pulse_table.setVerticalHeaderLabels(pulse_options)

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
        """This method is called whenever the events in the pulse sequence change. It updates the view to reflect the changes."""
        logger.debug("Updating events to %s", self.module.model.pulse_sequence.events)

        # Add label for the event lengths
        event_layout = QVBoxLayout()
        event_parameters_label = QLabel("Event lengths:")
        event_layout.addWidget(event_parameters_label)

        for event in self.module.model.pulse_sequence.events:
            logger.debug("Adding event to pulseprogrammer view: %s", event.name)
            # Create a label for the event
            event_label = QLabel("%s : %s µs" % (event.name, str(event.duration * Decimal(1e6))))
            event_layout.addWidget(event_label)
        
        # Delete the old widget and create a new one
        self.event_widget.deleteLater()
        self.event_widget = QWidget()
        self.event_widget.setLayout(event_layout)
        self.layout().addWidget(self.event_widget)

        self.pulse_table.setColumnCount(len(self.module.model.pulse_sequence.events))
        self.pulse_table.setHorizontalHeaderLabels([event.name for event in self.module.model.pulse_sequence.events])

        self.set_parameter_icons()

    def set_parameter_icons(self):
        for column_idx, event in enumerate(self.module.model.pulse_sequence.events):
            for row_idx, parameter in enumerate(self.module.model.pulse_parameter_options.keys()):
                if row_idx == 0:
                    event_options_widget = EventOptionsWidget(event)
                    # Connect the delete_event signal to the on_delete_event slot
                    func = functools.partial(self.module.controller.delete_event, event_name=event.name)
                    event_options_widget.delete_event.connect(func)
                    # Connect the change_event_duration signal to the on_change_event_duration slot
                    event_options_widget.change_event_duration.connect(self.module.controller.change_event_duration)
                    # Connect the change_event_name signal to the on_change_event_name slot
                    event_options_widget.change_event_name.connect(self.module.controller.change_event_name)

                    self.pulse_table.setCellWidget(row_idx, column_idx, event_options_widget)
                    self.pulse_table.setRowHeight(row_idx, event_options_widget.layout().sizeHint().height())

                logger.debug("Adding button for event %s and parameter %s", event, parameter)
                logger.debug("Parameter object id: %s", id(event.parameters[parameter]))
                button = QPushButton()
                icon = QIcon(event.parameters[parameter].get_pixmap())
                logger.debug("Icon size: %s", icon.availableSizes())
                button.setIcon(icon)
                button.setIconSize(icon.availableSizes()[0])
                button.setFixedSize(icon.availableSizes()[0])
                    
                # We add 1 to the row index because the first row is used for the event options
                self.pulse_table.setCellWidget(row_idx + 1, column_idx, button)
                self.pulse_table.setRowHeight(row_idx + 1, icon.availableSizes()[0].height())
                self.pulse_table.setColumnWidth(column_idx, icon.availableSizes()[0].width())

                # Connect the button to the on_button_clicked slot
                func = functools.partial(self.on_table_button_clicked, event=event, parameter=parameter)
                button.clicked.connect(func)

    @pyqtSlot()
    def on_table_button_clicked(self, event, parameter):
        logger.debug("Button for event %s and parameter %s clicked", event, parameter)
        # Create a QDialog to set the options for the parameter.
        dialog = OptionsDialog(event, parameter, self)
        result = dialog.exec()

        if result:
            for option, function in dialog.return_functions.items():
                logger.debug("Setting option %s of parameter %s in event %s to %s", option, parameter, event, function())
                option.set_value(function())
            
            self.set_parameter_icons()

    @pyqtSlot()
    def on_save_button_clicked(self):
        logger.debug("Save button clicked")
        file_manager = QFileManager(self)
        file_name = file_manager.saveFileDialog()
        if file_name:
            self.module.controller.save_pulse_sequence(file_name)

    @pyqtSlot()
    def on_load_button_clicked(self):
        logger.debug("Load button clicked")
        file_manager = QFileManager(self)
        file_name = file_manager.loadFileDialog()
        if file_name:
            self.module.controller.load_pulse_sequence(file_name)

class EventOptionsWidget(QWidget):
    """ This class is a widget that can be used to set the options for a pulse parameter.
    This widget is then added to the the first row of the according event column in the pulse table.
    It has a edit button that opens a dialog that allows the user to change the options for the event (name and duration).
    Furthermore it has a delete button that deletes the event from the pulse sequence.
    """

    delete_event = pyqtSignal(str)
    change_event_duration = pyqtSignal(str, str)
    change_event_name = pyqtSignal(str, str)

    def __init__(self, event):
        super().__init__()
        self.event = event


        self_path = Path(__file__).parent
        layout = QHBoxLayout()
        self.edit_button = QToolButton()
        icon = QIcon(str(self_path / "resources/Pen_16x16.png"))
        self.edit_button.setIcon(icon)
        self.edit_button.setIconSize(icon.availableSizes()[0])
        self.edit_button.setFixedSize(icon.availableSizes()[0])
        self.edit_button.clicked.connect(self.edit_event)
        # Delete button
        self.delete_button = QToolButton()
        icon = QIcon(str(self_path / "resources/Garbage_16x16.png"))
        self.delete_button.setIcon(icon)
        self.delete_button.setIconSize(icon.availableSizes()[0])
        self.delete_button.setFixedSize(icon.availableSizes()[0])
        self.delete_button.clicked.connect(self.create_delete_event_dialog)

        layout.addWidget(self.edit_button)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def edit_event(self):
        logger.debug("Edit button clicked for event %s", self.event.name)
        
        # Create a QDialog to edit the event
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit event")
        layout = QVBoxLayout()
        label = QLabel("Edit event %s" % self.event.name)
        layout.addWidget(label)

        # Create the inputs for event name, duration 
        event_form_layout = QFormLayout()
        name_label = QLabel("Name:")
        name_lineedit = QLineEdit(self.event.name)
        event_form_layout.addRow(name_label, name_lineedit)
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration:")
        duration_lineedit = QLineEdit()
        unit_label = QLabel("µs")
        duration_lineedit.setText(str(self.event.duration * Decimal(1e6)))
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_lineedit)
        duration_layout.addWidget(unit_label)
        event_form_layout.addRow(duration_layout)
        layout.addLayout(event_form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        result = dialog.exec()
        if result:
            logger.debug("Editing event %s", self.event.name)
            if name_lineedit.text() != self.event.name:
                self.change_event_name.emit(self.event.name, name_lineedit.text())
            if duration_lineedit.text() != str(self.event.duration):
                self.change_event_duration.emit(self.event.name, duration_lineedit.text())


    def create_delete_event_dialog(self):
        # Create an 'are you sure' dialog
        logger.debug("Delete button clicked")
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete event")
        layout = QVBoxLayout()
        label = QLabel("Are you sure you want to delete event %s?" % self.event.name)
        layout.addWidget(label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        result = dialog.exec()
        if result:
            self.delete_event.emit(self.event.name)
            

class OptionsDialog(QDialog):
    """ This dialog is created whenever the edit button for a pulse option is clicked. 
    It allows the user to change the options for the pulse parameter and creates the dialog in accordance to what can be set."""
    def __init__(self, event, parameter, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setWindowTitle("Options")

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Change options for the pulse parameter: %s" % parameter)
        self.layout.addWidget(self.label)
        parameter = event.parameters[parameter]
        
        options = parameter.get_options()

        # Based on these options we will now create our selection widget
        self.return_functions = OrderedDict()

        # If the options are a list , we will create a QComboBox
        for option in options:
            if option == list:
                pass
            # If the options are boolean, we will create a QCheckBox
            elif isinstance(option, BooleanOption):
                check_box = QCheckBox()

                def checkbox_result():
                    return check_box.isChecked()

                check_box.setChecked(option.value)
                self.layout.addWidget(check_box)
                self.return_functions[option] = checkbox_result

            # If the options are a float/int we will create a QSpinBox
            elif isinstance(option, NumericOption):
                numeric_layout = QHBoxLayout()
                numeric_label = QLabel(option.name)
                numeric_lineedit = QLineEdit(str(option.value))
                numeric_layout.addWidget(numeric_label)
                numeric_layout.addWidget(numeric_lineedit)
                numeric_layout.addStretch(1)
                self.layout.addLayout(numeric_layout)
                
                self.return_functions[option] = numeric_lineedit.text

            # If the options are a string we will create a QLineEdit
            elif option == str:
                pass

            elif isinstance(option, FunctionOption):
                function_option = FunctionOptionWidget(option, event, parent)
                self.layout.addWidget(function_option)
        
        logger.debug("Return functions are: %s" % self.return_functions.items())

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)

class FunctionOptionWidget(QWidget):
    """This class is a widget that can be used to set the options for a pulse parameter.
    It plots the given function in time and frequency domain. 
    One can also select the function from a list of functions represented as buttons."""

    def __init__(self, function_option, event, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.function_option = function_option
        self.event = event
        layout = QVBoxLayout()
        inner_layout = QHBoxLayout()
        for function in function_option.functions:
            button = QPushButton(function.name)
            button.clicked.connect(functools.partial(self.on_functionbutton_clicked, function=function))
            inner_layout.addWidget(button)
        
        layout.addLayout(inner_layout)
        self.setLayout(layout)

        # Add Advanced settings button
        self.advanced_settings_button = QPushButton("Show Advanced settings")
        self.advanced_settings_button.clicked.connect(self.on_advanced_settings_button_clicked)
        layout.addWidget(self.advanced_settings_button)

        # Add advanced settings widget
        self.advanced_settings = QGroupBox('Advanced Settings')
        self.advanced_settings.setHidden(True)
        self.advanced_settings_layout = QFormLayout()
        self.advanced_settings.setLayout(self.advanced_settings_layout)
        layout.addWidget(self.advanced_settings)

        # Add the advanced settings
        # Advanced settings are  resolution, start_x = -1, end_x and the expr of the function_option.value
        resolution_layout = QHBoxLayout()
        resolution_label = QLabel("Resolution:")
        self.resolution_lineedit = QLineEdit(str(function_option.value.resolution))
        resolution_layout.addWidget(resolution_label)
        resolution_layout.addWidget(self.resolution_lineedit)
        resolution_layout.addStretch(1)
        self.advanced_settings_layout.addRow(resolution_label, resolution_layout)

        start_x_layout = QHBoxLayout()
        start_x_label = QLabel("Start x:")
        self.start_x_lineedit = QLineEdit(str(function_option.value.start_x))
        start_x_layout.addWidget(start_x_label)
        start_x_layout.addWidget(self.start_x_lineedit)
        start_x_layout.addStretch(1)
        self.advanced_settings_layout.addRow(start_x_label, start_x_layout)

        end_x_layout = QHBoxLayout()
        end_x_label = QLabel("End x:")
        self.end_x_lineedit = QLineEdit(str(function_option.value.end_x))
        end_x_layout.addWidget(end_x_label)
        end_x_layout.addWidget(self.end_x_lineedit)
        end_x_layout.addStretch(1)
        self.advanced_settings_layout.addRow(end_x_label, end_x_layout)

        expr_layout = QHBoxLayout()
        expr_label = QLabel("Expression:")
        self.expr_lineedit = QLineEdit(str(function_option.value.expr))
        expr_layout.addWidget(expr_label)
        expr_layout.addWidget(self.expr_lineedit)
        expr_layout.addStretch(1)
        self.advanced_settings_layout.addRow(expr_label, expr_layout)

        # Display the active function
        self.load_active_function()

        # Add buttton for replotting of the active function with the new parameters
        self.replot_button = QPushButton("Replot")
        self.replot_button.clicked.connect(self.on_replot_button_clicked)
        layout.addWidget(self.replot_button)

    @pyqtSlot()
    def on_replot_button_clicked(self):
        logger.debug("Replot button clicked")
        # Update the resolution, start_x, end_x and expr lineedits
        self.function_option.value.resolution = float(self.resolution_lineedit.text())
        self.function_option.value.start_x = float(self.start_x_lineedit.text())
        self.function_option.value.end_x = float(self.end_x_lineedit.text())
        try:
            self.function_option.value.expr = self.expr_lineedit.text()
        except SyntaxError:
            logger.debug("Invalid expression: %s", self.expr_lineedit.text())
            self.expr_lineedit.setText(str(self.function_option.value.expr))
            # Create message box that tells the user that the expression is invalid
            self.create_message_box("Invalid expression", "The expression you entered is invalid. Please enter a valid expression.")


        self.delete_active_function()
        self.load_active_function()
  

    @pyqtSlot()
    def on_advanced_settings_button_clicked(self):
        if self.advanced_settings.isHidden():
            self.advanced_settings.setHidden(False)
            self.advanced_settings_button.setText('Hide Advanced Settings')
        else:
            self.advanced_settings.setHidden(True)
            self.advanced_settings_button.setText('Show Advanced Settings')


    @pyqtSlot()
    def on_functionbutton_clicked(self, function):
        logger.debug("Button for function %s clicked", function.name)
        self.function_option.set_value(function)
        self.delete_active_function()
        self.load_active_function()

    def delete_active_function(self):
        # Remove the plotter with object name "plotter" from the layout
        for i in reversed(range(self.layout().count())):
            item = self.layout().itemAt(i)
            if item.widget() and item.widget().objectName() == "active_function":
                item.widget().deleteLater()
                break

    def load_active_function(self):
        # New QWidget for the active function
        active_function_Widget = QWidget()
        active_function_Widget.setObjectName("active_function")
        
        function_layout = QVBoxLayout()

        plot_layout = QHBoxLayout()
        
        # Add plot for time domain
        time_domain_layout = QVBoxLayout()
        time_domain_label = QLabel("Time domain:")
        time_domain_layout.addWidget(time_domain_label)
        plot = self.function_option.value.time_domain_plot(self.event.duration)
        time_domain_layout.addWidget(plot)
        plot_layout.addLayout(time_domain_layout)

        # Add plot for frequency domain
        frequency_domain_layout = QVBoxLayout()
        frequency_domain_label = QLabel("Frequency domain:")
        frequency_domain_layout.addWidget(frequency_domain_label)
        plot = self.function_option.value.frequency_domain_plot(self.event.duration)
        frequency_domain_layout.addWidget(plot)
        plot_layout.addLayout(frequency_domain_layout)

        function_layout.addLayout(plot_layout)

        parameter_layout = QFormLayout()
        parameter_label = QLabel("Parameters:")
        parameter_layout.addRow(parameter_label)
        for parameter in self.function_option.value.parameters:
            parameter_label = QLabel(parameter.name)
            parameter_lineedit = QLineEdit(str(parameter.value))
            # Add the parameter_lineedit editingFinished signal to the paramter.set_value slot
            parameter_lineedit.editingFinished.connect(lambda: parameter.set_value(parameter_lineedit.text()))

            # Create a QHBoxLayout
            hbox = QHBoxLayout()

            # Add your QLineEdit and a stretch to the QHBoxLayout
            hbox.addWidget(parameter_lineedit)
            hbox.addStretch(1)

            # Use addRow() method to add label and the QHBoxLayout next to each other
            parameter_layout.addRow(parameter_label, hbox)

        function_layout.addLayout(parameter_layout)
        function_layout.addStretch(1)
        active_function_Widget.setLayout(function_layout)
        self.layout().addWidget(active_function_Widget)

        # Update the resolution, start_x, end_x and expr lineedits
        self.resolution_lineedit.setText(str(self.function_option.value.resolution))
        self.start_x_lineedit.setText(str(self.function_option.value.start_x))
        self.end_x_lineedit.setText(str(self.function_option.value.end_x))
        self.expr_lineedit.setText(str(self.function_option.value.expr))

    def create_message_box(self, message : str, information : str) -> None:
        """Creates a message box with the given message and information and shows it.
        
        Args:
            message (str): The message to be shown in the message box
            information (str): The information to be shown in the message box"""
        msg = QMessageBox(parent=self.parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.setInformativeText(information)
        msg.setWindowTitle("Warning")
        msg.exec()
        

class AddEventDialog(QDialog):
    """This dialog is created whenever a new event is added to the pulse sequence. It allows the user to enter a name for the event."""
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
        self.buttons.accepted.connect(self.check_input)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.buttons)

    def get_name(self):
        return self.name_input.text()

    def check_input(self):
        # Make sure that name is not empty and that event name doesn't already exist. 
        if self.name_input.text() == "":
            self.label.setText("Please enter a name for the event.")
        elif self.name_input.text() in self.parent().module.model.pulse_sequence.events:
            self.label.setText("Event name already exists. Please enter a different name.")
        else:
            self.accept()


class QFileManager:
    def __init__(self, parent=None):
        self.parent = parent

    def loadFileDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self.parent,
                                                  "QFileManager - Open File",
                                                  "",
                                                  "Quack Files (*.quack);;All Files (*)",
                                                  options = QFileDialog.Option.ReadOnly)
        if fileName:
            return fileName
        else:
            return None

    def saveFileDialog(self):
        fileName, _ = QFileDialog.getSaveFileName(self.parent,
                                                  "QFileManager - Save File",
                                                  "",
                                                  "Quack Files (*.quack);;All Files (*)",
                                                  options=QFileDialog.Option.DontUseNativeDialog)
        if fileName:
            # Append the .quack extension if not present
            if not fileName.endswith('.quack'):
                fileName += '.quack'
            return fileName
        else:
            return None
        