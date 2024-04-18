import logging
import functools
from collections import OrderedDict
from decimal import Decimal
from PyQt6.QtGui import QValidator
from PyQt6.QtWidgets import (
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QTableWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
    QWidget,
    QCheckBox,
    QToolButton,
    QFileDialog,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSlot, pyqtSignal
from nqrduck.module.module_view import ModuleView
from nqrduck.assets.icons import Logos
from nqrduck.helpers.duckwidgets import DuckFloatEdit, DuckEdit
from nqrduck_spectrometer.pulseparameters import (
    BooleanOption,
    NumericOption,
    FunctionOption,
)

logger = logging.getLogger(__name__)


class PulseProgrammerView(ModuleView):

    def __init__(self, module):
        super().__init__(module)

        self.setup_pulsetable()

        self.setup_variabletables()

        logger.debug(
            "Connecting pulse parameter options changed signal to on_pulse_parameter_options_changed"
        )
        self.module.model.pulse_parameter_options_changed.connect(
            self.on_pulse_parameter_options_changed
        )

    def setup_variabletables(self) -> None:
        """Setup the table for the variables."""
        pass

    def setup_pulsetable(self) -> None:
        """Setup the table for the pulse sequence. Also add buttons for saving and loading pulse sequences and editing and creation of events"""
        # Create pulse table
        self.title = QLabel(
            "Pulse Sequence: %s" % self.module.model.pulse_sequence.name
        )
        # Make title bold
        font = self.title.font()
        font.setBold(True)
        self.title.setFont(font)

        # Table setup
        self.pulse_table = QTableWidget(self)
        self.pulse_table.setSizeAdjustPolicy(
            QTableWidget.SizeAdjustPolicy.AdjustToContents
        )
        self.pulse_table.setAlternatingRowColors(True)
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        table_layout = QHBoxLayout()
        table_layout.addWidget(self.pulse_table)
        table_layout.addStretch(1)
        # Add button for new event
        self.new_event_button = QPushButton("New event")
        # Add the New Icon to the button
        icon = Logos.New16x16()
        self.new_event_button.setIconSize(icon.availableSizes()[0])
        self.new_event_button.setIcon(icon)
        self.new_event_button.clicked.connect(self.on_new_event_button_clicked)
        button_layout.addWidget(self.new_event_button)

        # Add button for save pulse sequence
        self.save_pulse_sequence_button = QPushButton("Save pulse sequence")
        self.save_pulse_sequence_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        # Add the Save Icon to the button
        icon = Logos.Save16x16()
        self.save_pulse_sequence_button.setIconSize(icon.availableSizes()[0])
        self.save_pulse_sequence_button.setIcon(icon)
        self.save_pulse_sequence_button.clicked.connect(self.on_save_button_clicked)
        button_layout.addWidget(self.save_pulse_sequence_button)

        # Add button for load pulse sequence
        self.load_pulse_sequence_button = QPushButton("Load pulse sequence")
        # Add the Load Icon to the button
        icon = Logos.Load16x16()
        self.load_pulse_sequence_button.setIconSize(icon.availableSizes()[0])
        self.load_pulse_sequence_button.setIcon(icon)
        self.load_pulse_sequence_button.clicked.connect(self.on_load_button_clicked)
        button_layout.addWidget(self.load_pulse_sequence_button)

        # Connect signals
        self.module.model.events_changed.connect(self.on_events_changed)
        self.module.model.pulse_sequence_changed.connect(self.on_pulse_sequence_changed)

        button_layout.addStretch(1)
        layout.addWidget(self.title)
        layout.addLayout(button_layout)
        layout.addLayout(table_layout)
        layout.addStretch(1)

        self.setLayout(layout)

        # Add layout for the event lengths
        self.event_widget = QWidget()
        self.layout().addWidget(self.event_widget)

        self.on_events_changed()

    @pyqtSlot()
    def on_pulse_sequence_changed(self) -> None:
        """This method is called whenever the pulse sequence changes. It updates the view to reflect the changes."""
        logger.debug(
            "Updating pulse sequence to %s", self.module.model.pulse_sequence.name
        )
        self.title.setText("Pulse Sequence: %s" % self.module.model.pulse_sequence.name)

    @pyqtSlot()
    def on_pulse_parameter_options_changed(self) -> None:
        """This method is called whenever the pulse parameter options change. It updates the view to reflect the changes."""
        logger.debug(
            "Updating pulse parameter options to %s",
            self.module.model.pulse_parameter_options.keys(),
        )
        # We set it to the length of the pulse parameter options + 1 because we want to add a row for the parameter option buttons
        self.pulse_table.setRowCount(len(self.module.model.pulse_parameter_options) + 1)
        # Move the vertical header labels on row down
        pulse_options = [""]
        pulse_options.extend(list(self.module.model.pulse_parameter_options.keys()))
        self.pulse_table.setVerticalHeaderLabels(pulse_options)

    @pyqtSlot()
    def on_new_event_button_clicked(self) -> None:
        """This method is called whenever the new event button is clicked. It creates a new event and adds it to the pulse sequence."""
        # Create a QDialog for the new event
        logger.debug("New event button clicked")
        dialog = AddEventDialog(self)
        result = dialog.exec()
        if result:
            event_name = dialog.get_name()
            duration = dialog.get_duration()
            logger.debug(
                "Adding new event with name %s, duration %g", event_name, duration
            )
            self.module.model.add_event(event_name, duration)

    @pyqtSlot()
    def on_events_changed(self) -> None:
        """This method is called whenever the events in the pulse sequence change. It updates the view to reflect the changes."""
        logger.debug("Updating events to %s", self.module.model.pulse_sequence.events)

        # Add label for the event lengths
        event_layout = QVBoxLayout()
        event_parameters_label = QLabel("Event lengths:")
        event_layout.addWidget(event_parameters_label)

        for event in self.module.model.pulse_sequence.events:
            logger.debug("Adding event to pulseprogrammer view: %s", event.name)
            # Create a label for the event
            event_label = QLabel(
                "%s : %.16g µs" % (event.name, (event.duration * Decimal(1e6)))
            )
            event_layout.addWidget(event_label)

        # Delete the old widget and create a new one
        self.event_widget.deleteLater()
        self.event_widget = QWidget()
        self.event_widget.setLayout(event_layout)
        self.layout().addWidget(self.event_widget)

        self.pulse_table.setColumnCount(len(self.module.model.pulse_sequence.events))
        self.pulse_table.setHorizontalHeaderLabels(
            [event.name for event in self.module.model.pulse_sequence.events]
        )

        self.set_parameter_icons()

    def set_parameter_icons(self) -> None:
        """This method sets the icons for the pulse parameter options."""
        for column_idx, event in enumerate(self.module.model.pulse_sequence.events):
            for row_idx, parameter in enumerate(
                self.module.model.pulse_parameter_options.keys()
            ):
                if row_idx == 0:
                    event_options_widget = EventOptionsWidget(event)
                    # Connect the delete_event signal to the on_delete_event slot
                    func = functools.partial(
                        self.module.controller.delete_event, event_name=event.name
                    )
                    event_options_widget.delete_event.connect(func)
                    # Connect the change_event_duration signal to the on_change_event_duration slot
                    event_options_widget.change_event_duration.connect(
                        self.module.controller.change_event_duration
                    )
                    # Connect the change_event_name signal to the on_change_event_name slot
                    event_options_widget.change_event_name.connect(
                        self.module.controller.change_event_name
                    )
                    # Connect the move_event_left signal to the on_move_event_left slot
                    event_options_widget.move_event_left.connect(
                        self.module.controller.on_move_event_left
                    )
                    # Connect the move_event_right signal to the on_move_event_right slot
                    event_options_widget.move_event_right.connect(
                        self.module.controller.on_move_event_right
                    )

                    self.pulse_table.setCellWidget(
                        row_idx, column_idx, event_options_widget
                    )
                    self.pulse_table.setRowHeight(
                        row_idx, event_options_widget.layout().sizeHint().height()
                    )

                logger.debug(
                    "Adding button for event %s and parameter %s", event, parameter
                )
                logger.debug("Parameter object id: %s", id(event.parameters[parameter]))
                button = QPushButton()
                icon = event.parameters[parameter].get_pixmap()
                logger.debug("Icon size: %s", icon.availableSizes())
                button.setIcon(icon)
                button.setIconSize(icon.availableSizes()[0])
                button.setFixedSize(icon.availableSizes()[0])

                # We add 1 to the row index because the first row is used for the event options
                self.pulse_table.setCellWidget(row_idx + 1, column_idx, button)
                self.pulse_table.setRowHeight(
                    row_idx + 1, icon.availableSizes()[0].height()
                )
                self.pulse_table.setColumnWidth(
                    column_idx, icon.availableSizes()[0].width()
                )

                # Connect the button to the on_button_clicked slot
                func = functools.partial(
                    self.on_table_button_clicked, event=event, parameter=parameter
                )
                button.clicked.connect(func)

    @pyqtSlot()
    def on_table_button_clicked(self, event, parameter) -> None:
        """This method is called whenever a button in the pulse table is clicked. It opens a dialog to set the options for the parameter."""
        logger.debug("Button for event %s and parameter %s clicked", event, parameter)
        # Create a QDialog to set the options for the parameter.
        dialog = OptionsDialog(event, parameter, self)
        result = dialog.exec()

        if result:
            for option, function in dialog.return_functions.items():
                logger.debug(
                    "Setting option %s of parameter %s in event %s to %s",
                    option,
                    parameter,
                    event,
                    function(),
                )
                option.set_value(function())

            self.set_parameter_icons()

    @pyqtSlot()
    def on_save_button_clicked(self) -> None:
        """This method is called whenever the save button is clicked. It opens a dialog to select a file to save the pulse sequence to."""
        logger.debug("Save button clicked")
        file_manager = QFileManager(self)
        file_name = file_manager.saveFileDialog()
        if file_name:
            self.module.controller.save_pulse_sequence(file_name)

    @pyqtSlot()
    def on_load_button_clicked(self) -> None:
        """This method is called whenever the load button is clicked. It opens a dialog to select a file to load the pulse sequence from."""
        logger.debug("Load button clicked")
        file_manager = QFileManager(self)
        file_name = file_manager.loadFileDialog()
        if file_name:
            self.module.controller.load_pulse_sequence(file_name)


class EventOptionsWidget(QWidget):
    """This class is a widget that can be used to set the options for a pulse parameter.
    This widget is then added to the the first row of the according event column in the pulse table.
    It has a edit button that opens a dialog that allows the user to change the options for the event (name and duration).
    Furthermore it has a delete button that deletes the event from the pulse sequence.
    """

    delete_event = pyqtSignal(str)
    change_event_duration = pyqtSignal(str, str)
    change_event_name = pyqtSignal(str, str)
    move_event_left = pyqtSignal(str)
    move_event_right = pyqtSignal(str)

    def __init__(self, event):
        super().__init__()
        self.event = event

        layout = QVBoxLayout()
        upper_layout = QHBoxLayout()
        # Edit button
        self.edit_button = QToolButton()
        icon = Logos.Pen12x12()
        self.edit_button.setIcon(icon)
        self.edit_button.setIconSize(icon.availableSizes()[0])
        self.edit_button.setFixedSize(icon.availableSizes()[0])
        self.edit_button.clicked.connect(self.edit_event)

        # Delete button
        self.delete_button = QToolButton()
        icon = Logos.Garbage12x12()
        self.delete_button.setIcon(icon)
        self.delete_button.setIconSize(icon.availableSizes()[0])
        self.delete_button.setFixedSize(icon.availableSizes()[0])
        self.delete_button.clicked.connect(self.create_delete_event_dialog)

        upper_layout.addWidget(self.edit_button)
        upper_layout.addWidget(self.delete_button)

        lower_layout = QHBoxLayout()
        # Move left button
        self.move_left_button = QToolButton()
        icon = Logos.ArrowLeft12x12()
        self.move_left_button.setIcon(icon)
        self.move_left_button.setIconSize(icon.availableSizes()[0])
        self.move_left_button.setFixedSize(icon.availableSizes()[0])
        self.move_left_button.clicked.connect(self.move_event_left_button_clicked)

        # Move right button
        self.move_right_button = QToolButton()
        icon = Logos.ArrowRight12x12()
        self.move_right_button.setIcon(icon)
        self.move_right_button.setIconSize(icon.availableSizes()[0])
        self.move_right_button.setFixedSize(icon.availableSizes()[0])
        self.move_right_button.clicked.connect(self.move_event_right_button_clicked)

        lower_layout.addWidget(self.move_left_button)
        lower_layout.addWidget(self.move_right_button)

        layout.addLayout(upper_layout)
        layout.addLayout(lower_layout)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    @pyqtSlot()
    def edit_event(self) -> None:
        """This method is called when the edit button is clicked. It opens a dialog that allows the user to change the event name and duration.
        If the user clicks ok, the change_event_name and change_event_duration signals are emitted.
        """
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
        duration_lineedit.setText("%.16g" % (self.event.duration * Decimal(1e6)))
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(duration_lineedit)
        duration_layout.addWidget(unit_label)
        event_form_layout.addRow(duration_layout)
        layout.addLayout(event_form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
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
                self.change_event_duration.emit(
                    self.event.name, duration_lineedit.text()
                )

    @pyqtSlot()
    def create_delete_event_dialog(self) -> None:
        """This method is called when the delete button is clicked. It creates a dialog that asks the user if he is sure he wants to delete the event.
        If the user clicks yes, the delete_event signal is emitted.
        """
        # Create an 'are you sure' dialog
        logger.debug("Delete button clicked")
        dialog = QDialog(self)
        dialog.setWindowTitle("Delete event")
        layout = QVBoxLayout()
        label = QLabel("Are you sure you want to delete event %s?" % self.event.name)
        layout.addWidget(label)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        result = dialog.exec()
        if result:
            self.delete_event.emit(self.event.name)

    @pyqtSlot()
    def move_event_left_button_clicked(self) -> None:
        """This method is called when the move left button is clicked."""
        logger.debug("Move event left: %s", self.event.name)
        self.move_event_left.emit(self.event.name)

    def move_event_right_button_clicked(self) -> None:
        """This method is called when the move right button is clicked."""
        logger.debug("Move event right: %s", self.event.name)
        self.move_event_right.emit(self.event.name)


class OptionsDialog(QDialog):
    """This dialog is created whenever the edit button for a pulse option is clicked.
    It allows the user to change the options for the pulse parameter and creates the dialog in accordance to what can be set.
    """

    def __init__(self, event, parameter, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setWindowTitle("Options")

        self.layout = QVBoxLayout(self)

        numeric_layout = QFormLayout()
        numeric_layout.setHorizontalSpacing(30)

        self.label = QLabel("Change options for the pulse parameter: %s" % parameter)
        self.layout.addWidget(self.label)

        self.layout.addLayout(numeric_layout)

        # If the parameter is a string, we first need to get the parameter object from the according event
        if isinstance(parameter, str):
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
                numeric_label = QLabel(option.name)
                numeric_lineedit = QLineEdit(str(option.value))
                numeric_lineedit.setMaximumWidth(300)
                numeric_layout.addRow(numeric_label, numeric_lineedit)

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
    One can also select the function from a list of functions represented as buttons.
    """

    def __init__(self, function_option, event, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.function_option = function_option
        self.event = event
        layout = QVBoxLayout()
        inner_layout = QHBoxLayout()
        for function in function_option.functions:
            button = QPushButton(function.name)
            button.clicked.connect(
                functools.partial(self.on_functionbutton_clicked, function=function)
            )
            inner_layout.addWidget(button)

        layout.addLayout(inner_layout)
        self.setLayout(layout)

        # Add Advanced settings button
        self.advanced_settings_button = QPushButton("Show Advanced settings")
        self.advanced_settings_button.clicked.connect(
            self.on_advanced_settings_button_clicked
        )
        layout.addWidget(self.advanced_settings_button)

        # Add advanced settings widget
        self.advanced_settings = QGroupBox("Advanced Settings")
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

        # Add buttton for replotting of the active function with the new parameters
        self.replot_button = QPushButton("Replot")
        self.replot_button.clicked.connect(self.on_replot_button_clicked)
        layout.addWidget(self.replot_button)

        # Display the active function
        self.load_active_function()

    @pyqtSlot()
    def on_replot_button_clicked(self) -> None:
        """This function is called when the replot button is clicked.
        It will update the parameters of the function and replots the function.
        """
        logger.debug("Replot button clicked")
        # Update the resolution, start_x, end_x and expr lineedits
        self.function_option.value.resolution = self.resolution_lineedit.text()
        self.function_option.value.start_x = self.start_x_lineedit.text()
        self.function_option.value.end_x = self.end_x_lineedit.text()
        try:
            self.function_option.value.expr = self.expr_lineedit.text()
        except SyntaxError:
            logger.debug("Invalid expression: %s", self.expr_lineedit.text())
            self.expr_lineedit.setText(str(self.function_option.value.expr))
            # Create message box that tells the user that the expression is invalid
            self.create_message_box(
                "Invalid expression",
                "The expression you entered is invalid. Please enter a valid expression.",
            )

        self.delete_active_function()
        self.load_active_function()

    @pyqtSlot()
    def on_advanced_settings_button_clicked(self) -> None:
        """This function is called when the advanced settings button is clicked.
        It will show or hide the advanced settings.
        """
        if self.advanced_settings.isHidden():
            self.advanced_settings.setHidden(False)
            self.advanced_settings_button.setText("Hide Advanced Settings")
        else:
            self.advanced_settings.setHidden(True)
            self.advanced_settings_button.setText("Show Advanced Settings")

    @pyqtSlot()
    def on_functionbutton_clicked(self, function) -> None:
        """This function is called when a function button is clicked.
        It will update the function_option.value to the function that was clicked.
        """
        logger.debug("Button for function %s clicked", function.name)
        self.function_option.set_value(function)
        self.delete_active_function()
        self.load_active_function()

    def delete_active_function(self) -> None:
        """This function is called when the active function is deleted.
        It will remove the active function from the layout.
        """
        # Remove the plotter with object name "plotter" from the layout
        for i in reversed(range(self.layout().count())):
            item = self.layout().itemAt(i)
            if item.widget() and item.widget().objectName() == "active_function":
                item.widget().deleteLater()
                break

    def load_active_function(self) -> None:
        """This function is called when the active function is loaded.
        It will add the active function to the layout.
        """
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
            parameter_lineedit.editingFinished.connect(
                lambda: parameter.set_value(parameter_lineedit.text())
            )

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

    def create_message_box(self, message: str, information: str) -> None:
        """Creates a message box with the given message and information and shows it.

        Args:
            message (str): The message to be shown in the message box
        information (str): The information to be shown in the message box
        """
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

        self.layout = QFormLayout(self)

        self.name_layout = QHBoxLayout()

        self.label = QLabel("Enter event name:")
        self.name_input = DuckEdit()
        self.name_input.validator = self.NameInputValidator(self)

        self.name_layout.addWidget(self.label)
        self.name_layout.addWidget(self.name_input)

        self.layout.addRow(self.name_layout)

        self.duration_layout = QHBoxLayout()

        self.duration_label = QLabel("Duration:")
        self.duration_lineedit = DuckFloatEdit(min_value=0)
        self.duration_lineedit.setText("20")
        self.unit_label = QLabel("µs")

        self.duration_layout.addWidget(self.duration_label)
        self.duration_layout.addWidget(self.duration_lineedit)

        self.duration_layout.addWidget(self.unit_label)

        self.layout.addRow(self.duration_layout)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )

        self.buttons.accepted.connect(self.check_input)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)

    def get_name(self) -> str:
        """Returns the name entered by the user.

        Returns:
        str: The name entered by the user
        """
        return self.name_input.text()

    def get_duration(self) -> Decimal:
        """Returns the duration entered by the user, or a fallback value."

        Returns:
        Decimal: The duration value provided by the user, or 20
        """
        return Decimal(self.duration_lineedit.text() or 20)

    def check_input(self) -> None:
        """Checks if the name and duration entered by the user is valid. If it is, the dialog is accepted. If not, the user is informed of the error."""
        if (
            self.duration_lineedit.validator.validate(self.duration_lineedit.text(), 0)[
                0
            ]
            == QValidator.State.Acceptable
            and self.name_input.validator.validate(self.name_input.text(), 0)[0]
            == QValidator.State.Acceptable
        ):
            self.accept()

    class NameInputValidator(QValidator):
        """A validator for the name input field.

        This is used to validate the input of the QLineEdit widget.
        """

        def validate(self, value, position):
            """Validates the input value.

            Args:
                value (str): The input value
                position (int): The position of the cursor

            Returns:
                Tuple[QValidator.State, str, int]: The validation state, the fixed value, and the position
            """
            if not value:
                return (QValidator.State.Intermediate, value, position)

            if any(
                [
                    event.name == value
                    for event in self.parent()
                    .parent()
                    .module.model.pulse_sequence.events
                ]
            ):
                return (QValidator.State.Invalid, value, position)

            return (QValidator.State.Acceptable, value, position)


# This class should be refactored in the module view so it can be used by all modules
class QFileManager:
    """This class provides methods for opening and saving files."""

    def __init__(self, parent=None):
        self.parent = parent

    def loadFileDialog(self) -> str:
        """Opens a file dialog for the user to select a file to open.

        Returns:
            str: The path of the file selected by the user.
        """
        fileName, _ = QFileDialog.getOpenFileName(
            self.parent,
            "QFileManager - Open File",
            "",
            "Quack Files (*.quack);;All Files (*)",
            options=QFileDialog.Option.ReadOnly,
        )
        if fileName:
            return fileName
        else:
            return None

    def saveFileDialog(self) -> str:
        """Opens a file dialog for the user to select a file to save.

        Returns:
            str: The path of the file selected by the user.
        """
        fileName, _ = QFileDialog.getSaveFileName(
            self.parent,
            "QFileManager - Save File",
            "",
            "Quack Files (*.quack);;All Files (*)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if fileName:
            # Append the .quack extension if not present
            if not fileName.endswith(".quack"):
                fileName += ".quack"
            return fileName
        else:
            return None
