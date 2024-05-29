"""Model for the pulse programmer module."""

import logging
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel
from quackseq.pulsesequence import QuackSequence
from quackseq.event import Event

logger = logging.getLogger(__name__)


class PulseProgrammerModel(ModuleModel):
    """Model for the pulse programmer module.

    This class is responsible for storing the data of the pulse programmer module.

    Attributes:
        FILE_EXTENSION (str): The file extension for pulse programmer files.

    Signals:
        pulse_parameter_options_changed: Emitted when the pulse parameter options change.
        events_changed: Emitted when the events in the pulse sequence change.
        pulse_sequence_changed: Emitted when the pulse sequence changes.
    """

    FILE_EXTENSION = "quack"

    events_changed = pyqtSignal()
    pulse_sequence_changed = pyqtSignal()

    def __init__(self, module):
        """Initializes the pulse programmer model.

        Args:
            module (Module): The module to which this model belongs.
        """
        super().__init__(module)
        self.pulse_sequence = QuackSequence("Untitled pulse sequence")

    def add_event(self, event_name: str, duration: float = 20):
        """Add a new event to the current pulse sequence.

        Args:
            event_name (str): A human-readable name for the event
            duration (float): The duration of the event in µs. Defaults to 20.
        """
        logger.debug(f"Adding event {event_name} with duration {duration}")
        
        event = Event(event_name, f"{duration}u", self.pulse_sequence)
        self.pulse_sequence.add_event(event)

        logger.debug(self.pulse_sequence.to_json())
        self.events_changed.emit()

    @property
    def pulse_sequence(self):
        """PulseSequence: The pulse sequence."""
        return self._pulse_sequence

    @pulse_sequence.setter
    def pulse_sequence(self, value):
        self._pulse_sequence = value
        self.pulse_sequence_changed.emit()
