from nqrduck.module.module import Module
from .model import PulseProgrammerModel
from .controller import PulseProgrammerController
from .view import PulseProgrammerView

class PulseProgrammer(Module):
    def __init__(self, model, view, controller):
        super().__init__(model, None, controller)
        self.view = None
        self.pulse_programmer_view = view(self)

pulse_programmer = PulseProgrammer(PulseProgrammerModel, PulseProgrammerView, PulseProgrammerController)
