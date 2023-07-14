import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.pulse_sequence import PulseSequence

logger = logging.getLogger(__name__)

class PulseProgrammerModel(ModuleModel):
    pulse_parameter_options_changed = pyqtSignal()
    events_changed = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)
        self.pulse_parameter_options = OrderedDict()
        self.pulse_sequence = PulseSequence("Untitled pulse sequence")

    def add_event(self, event_name):
        self.pulse_sequence.events.append(PulseSequence.Event(event_name, 0))
        logger.debug("Creating event %s with object id %s", event_name, id(self.pulse_sequence.events[-1]))

        # Create a default instance of the pulse parameter options and add it to the event
        for name, pulse_parameter_class in self.pulse_parameter_options.items():
            logger.debug("Adding pulse parameter %s to event %s", name, event_name)
            self.pulse_sequence.events[-1].parameters[name] = pulse_parameter_class(name)
            logger.debug("Created pulse parameter %s with object id %s", name, id(self.pulse_sequence.events[-1].parameters[name]))

        logger.debug(self.pulse_sequence.dump_sequence_data())
        self.events_changed.emit()

    @property
    def pulse_parameter_options(self):
        return self._pulse_parameter_options
    
    @pulse_parameter_options.setter
    def pulse_parameter_options(self, value):
        self._pulse_parameter_options = value
        logger.debug("Pulse parameter options changed - emitting signal")
        self.pulse_parameter_options_changed.emit()
