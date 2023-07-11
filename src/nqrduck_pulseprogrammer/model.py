import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class PulseProgrammerModel(ModuleModel):
    pulse_parameter_options_changed = pyqtSignal()
    events_changed = pyqtSignal()

    def __init__(self, module):
        super().__init__(module)
        self.pulse_parameter_options = OrderedDict()
        self.events = OrderedDict()

    def add_event(self, event_name):
        self.events[event_name] = OrderedDict()
        # Create a default instance of the pulse parameter options and add it to the event
        for name, pulse_parameter_class in self.pulse_parameter_options.items():
            self.events[event_name][name] = pulse_parameter_class("name")

        self.events_changed.emit()

    @property
    def events(self):
        return self._events
    
    @events.setter
    def events(self, value):
        self._events = value
        self.events_changed.emit()

    @property
    def pulse_parameter_options(self):
        return self._pulse_parameter_options
    
    @pulse_parameter_options.setter
    def pulse_parameter_options(self, value):
        self._pulse_parameter_options = value
        logger.debug("Pulse parameter options changed - emitting signal")
        self.pulse_parameter_options_changed.emit()
