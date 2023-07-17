import logging
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_controller import ModuleController

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