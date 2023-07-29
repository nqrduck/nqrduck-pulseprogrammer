import logging
import json
import decimal
from PyQt6.QtCore import pyqtSlot
from nqrduck.helpers.serializer import DecimalEncoder
from nqrduck.module.module_controller import ModuleController
from nqrduck_spectrometer.pulsesequence import PulseSequence

logger = logging.getLogger(__name__)

class PulseProgrammerController(ModuleController):
      
    def on_loading(self, pulse_parameter_options):
        logger.debug("Pulse programmer controller on loading")
        self.module.model.pulse_parameter_options = pulse_parameter_options

    @pyqtSlot(str)
    def delete_event(self, event_name):
        logger.debug("Deleting event %s", event_name)
        for event in self.module.model.pulse_sequence.events:
            if event.name == event_name:
                self.module.model.pulse_sequence.events.remove(event)
                break
        self.module.model.events_changed.emit()

    @pyqtSlot(str, str)
    def change_event_name(self, old_name, new_name):
        logger.debug("Changing event name from %s to %s", old_name, new_name)
        for event in self.module.model.pulse_sequence.events:
            if event.name == old_name:
                event.name = new_name
                break
        self.module.model.events_changed.emit()

    @pyqtSlot(str, str)
    def change_event_duration(self, event_name, duration):
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

    def save_pulse_sequence(self, path):
        logger.debug("Saving pulse sequence to %s", path)
        sequence = self.module.model.pulse_sequence.to_json()
        with open(path, "w") as file:
            file.write(json.dumps(sequence, cls=DecimalEncoder))
        

    def load_pulse_sequence(self, path):
        logger.debug("Loading pulse sequence from %s", path)
        sequence = None
        with open(path, "r") as file:
            sequence = file.read()

        sequence = json.loads(sequence)

        loaded_sequence = PulseSequence.load_sequence(sequence, self.module.model.pulse_parameter_options)
        
        self.module.model.pulse_sequence = loaded_sequence
        self.module.model.events_changed.emit()