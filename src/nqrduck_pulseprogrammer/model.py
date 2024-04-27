"""Model for the pulse programmer module."""
import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel
from nqrduck_spectrometer.pulsesequence import PulseSequence

logger = logging.getLogger(__name__)


class PulseProgrammerModel(ModuleModel):
    """Model for the pulse programmer module.
    
    This class is responsible for storing the data of the pulse programmer module.
    
    Signals:
        pulse_parameter_options_changed: Emitted when the pulse parameter options change.
        events_changed: Emitted when the events in the pulse sequence change.
        pulse_sequence_changed: Emitted when the pulse sequence changes.
    """
    pulse_parameter_options_changed = pyqtSignal()
    events_changed = pyqtSignal()
    pulse_sequence_changed = pyqtSignal()

    def __init__(self, module):
        """Initializes the pulse programmer model.
        
        Args:
            module (Module): The module to which this model belongs.
        """
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
            PulseSequence.Event(event_name, f"{float(duration):.16g}u")
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
        """dict: The pulse parameter options."""
        return self._pulse_parameter_options

    @pulse_parameter_options.setter
    def pulse_parameter_options(self, value):
        self._pulse_parameter_options = value
        logger.debug("Pulse parameter options changed - emitting signal")
        self.pulse_parameter_options_changed.emit()

    @property
    def pulse_sequence(self):
        """PulseSequence: The pulse sequence."""
        return self._pulse_sequence

    @pulse_sequence.setter
    def pulse_sequence(self, value):
        self._pulse_sequence = value
        self.pulse_sequence_changed.emit()
