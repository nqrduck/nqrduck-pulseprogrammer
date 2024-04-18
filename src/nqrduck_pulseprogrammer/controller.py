import logging
import json
import decimal
from PyQt6.QtCore import pyqtSlot
from nqrduck.helpers.serializer import DecimalEncoder
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.pulsesequence import PulseSequence

logger = logging.getLogger(__name__)

class PulseProgrammerController(ModuleController):
      
    def on_loading(self, pulse_parameter_options : dict) -> None:
        """This method is called when the module is loaded. It sets the pulse parameter options in the model.

        Args:
            pulse_parameter_options (dict): The pulse parameter options.
        """
        logger.debug("Pulse programmer controller on loading")
        self.module.model.pulse_parameter_options = pulse_parameter_options

    @pyqtSlot(str)
    def delete_event(self, event_name : str) -> None:
        """This method deletes an event from the pulse sequence.

        Args:
            event_name (str): The name of the event to be deleted.
        """
        logger.debug("Deleting event %s", event_name)
        for event in self.module.model.pulse_sequence.events:
            if event.name == event_name:
                self.module.model.pulse_sequence.events.remove(event)
                break
        self.module.model.events_changed.emit()

    @pyqtSlot(str, str)
    def change_event_name(self, old_name : str, new_name : str) -> None:
        """This method changes the name of an event.

        Args:
            old_name (str): The old name of the event.
            new_name (str): The new name of the event.
        """
        logger.debug("Changing event name from %s to %s", old_name, new_name)
        for event in self.module.model.pulse_sequence.events:
            if event.name == old_name:
                event.name = new_name
                break
        self.module.model.events_changed.emit()

    @pyqtSlot(str, str)
    def change_event_duration(self, event_name:str, duration) -> None:
        """This method changes the duration of an event.

        Args:
            event_name (str): The name of the event.
            duration (str): The new duration of the event.
        """
        logger.debug("Changing duration of event %s to %s", event_name, duration)
        for event in self.module.model.pulse_sequence.events:
            if event.name == event_name:
                try:
                    # The u is for microseconds
                    event.duration = duration + "u"
                except decimal.InvalidOperation:
                    logger.error("Duration must be a positive number")
                    # Emit signal to the nqrduck core to show an error message
                    self.module.nqrduck_signal.emit("notification", ["Error", "Duration must be a positive number"])
                break
        self.module.model.events_changed.emit()

    @pyqtSlot(str)
    def on_move_event_left(self, event_name: str) -> None:
        """This method moves the event one position to the left if possible.
        
        Args:
            event_name (str): The name of the event to be moved.
        """
        logger.debug("Moving event %s to the left", event_name)
        for i, event in enumerate(self.module.model.pulse_sequence.events):
            if event.name == event_name:
                if i > 0:
                    self.module.model.pulse_sequence.events[i], self.module.model.pulse_sequence.events[i-1] = self.module.model.pulse_sequence.events[i-1], self.module.model.pulse_sequence.events[i]
                    break
        self.module.model.events_changed.emit()


    @pyqtSlot(str)
    def on_move_event_right(self, event_name : str) -> None:
        """This method moves the event one position to the right if possible.
        
        Args:
            event_name (str): The name of the event to be moved.
        """
        logger.debug("Moving event %s to the right", event_name)
        for i, event in enumerate(self.module.model.pulse_sequence.events):
            if event.name == event_name:
                if i < len(self.module.model.pulse_sequence.events) - 1:
                    self.module.model.pulse_sequence.events[i], self.module.model.pulse_sequence.events[i+1] = self.module.model.pulse_sequence.events[i+1], self.module.model.pulse_sequence.events[i]
                    break
        self.module.model.events_changed.emit()

    def save_pulse_sequence(self, path :str) -> None:
        """This method saves the pulse sequence to a file.

        Args:
            path (str): The path to the file.
        """
        logger.debug("Saving pulse sequence to %s", path)
        # Get the name of the file without the extension and without the path
        file_name = path.split("/")[-1].split(".")[0]
        self.module.model.pulse_sequence.name = file_name
        logger.debug("Pulse sequence name: %s", self.module.model.pulse_sequence.name)
        self.module.model.pulse_sequence_changed.emit()

        sequence = self.module.model.pulse_sequence.to_json()
        with open(path, "w") as file:
            file.write(json.dumps(sequence, cls=DecimalEncoder))
        

    def load_pulse_sequence(self, path : str) -> None:
        """This method loads a pulse sequence from a file.

        Args:
            path (str): The path to the file.
        """
        logger.debug("Loading pulse sequence from %s", path)
        sequence = None
        with open(path) as file:
            sequence = file.read()

        sequence = json.loads(sequence)

        loaded_sequence = PulseSequence.load_sequence(sequence, self.module.model.pulse_parameter_options)
        
        self.module.model.pulse_sequence = loaded_sequence
        self.module.model.events_changed.emit()