import logging
from collections import OrderedDict
from PyQt6.QtCore import pyqtSignal
from nqrduck.module.module_model import ModuleModel

logger = logging.getLogger(__name__)

class PulseProgrammerModel(ModuleModel):
    pulse_parameter_options_changed = pyqtSignal()
    events_changed = pyqtSignal(list)

    def __init__(self, module):
        super().__init__(module)
        self.pulse_parameter_options = OrderedDict()
        self.events = []

    @property
    def events(self):
        return self._events
    
    @events.setter
    def events(self, value):
        self._events = value
        self.events_changed.emit(value)

    @property
    def pulse_parameter_options(self):
        return self._pulse_parameter_options
    
    @pulse_parameter_options.setter
    def pulse_parameter_options(self, value):
        self._pulse_parameter_options = value
        logger.debug("Pulse parameter options changed - emitting signal")
        self.pulse_parameter_options_changed.emit()
