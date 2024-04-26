import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.pulsesequence import PulseSequence

logger = logging.getLogger(__name__)


class PulseProgrammerModel(ModuleModel):
    pulse_parameter_options_changed = pyqtSignal()
    events_changed = pyqtSignal()
    pulse_sequence_changed = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)
        self.pulse_parameter_options = OrderedDict()
        self.pulse_sequence = PulseSequence("Untitled pulse sequence")

    def add_event(self, event_name: str, duration: float = 20):
        """Add a new event to the current pulse sequence.

        Args:
            event_name (str): A human-readable name for the event
            duration (float): The duration of the event in µs. Defaults to 20.
        """
        self.pulse_sequence.events.append(
            PulseSequence.Event(event_name, "%.16gu" % float(duration))
        )
        logger.debug(
            "Creating event %s with object id %s",
            event_name,
            id(self.pulse_sequence.events[-1]),
        )

        # Create a default instance of the pulse parameter options and add it to the event
        for name, pulse_parameter_class in self.pulse_parameter_options.items():
            logger.debug("Adding pulse parameter %s to event %s", name, event_name)
            self.pulse_sequence.events[-1].parameters[name] = pulse_parameter_class(
                name
            )
            logger.debug(
                "Created pulse parameter %s with object id %s",
                name,
                id(self.pulse_sequence.events[-1].parameters[name]),
            )

        logger.debug(self.pulse_sequence.to_json())
        self.events_changed.emit()

    @property
    def pulse_parameter_options(self):
        return self._pulse_parameter_options

    @pulse_parameter_options.setter
    def pulse_parameter_options(self, value):
        self._pulse_parameter_options = value
        logger.debug("Pulse parameter options changed - emitting signal")
        self.pulse_parameter_options_changed.emit()

    @property
    def pulse_sequence(self):
        return self._pulse_sequence

    @pulse_sequence.setter
    def pulse_sequence(self, value):
        self._pulse_sequence = value
        self.pulse_sequence_changed.emit()
