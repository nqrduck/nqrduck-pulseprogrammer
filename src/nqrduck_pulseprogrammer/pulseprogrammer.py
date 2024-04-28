"""Initialize the PulseProgrammer module."""

from nqrduck.module.module import Module
from .model import PulseProgrammerModel
from .controller import PulseProgrammerController
from .view import PulseProgrammerView


class PulseProgrammer(Module):
    """The pulse programmer module."""

    def __init__(self, model, view, controller):
        """Initializes the pulse programmer module.

        Args:
            model (PulseProgrammerModel): The model of the pulse programmer module.
            view (PulseProgrammerView): The view of the pulse programmer module.
            controller (PulseProgrammerController): The controller of the pulse programmer module.
        """
        super().__init__(model, None, controller)
        self.view = None
        self.pulse_programmer_view = view(self)


pulse_programmer = PulseProgrammer(
    PulseProgrammerModel, PulseProgrammerView, PulseProgrammerController
)
