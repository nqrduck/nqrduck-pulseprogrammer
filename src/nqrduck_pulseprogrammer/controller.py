import logging
from nqrduck.module.module_controller import ModuleController

logger = logging.getLogger(__name__)

class PulseProgrammerController(ModuleController):
      
    def on_loading(self, pulse_parameter_options):
        logger.debug("Pulse programmer controller on loading")
        self.module.model.pulse_parameter_options = pulse_parameter_options