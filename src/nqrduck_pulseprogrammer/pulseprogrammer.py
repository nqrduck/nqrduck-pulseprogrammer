from PyQt5.QtCore import pyqtSignal, QObject
from nqrduck.module.module import Module
from .model import PulseProgrammerModel
from .view import PulseProgrammerView
from .controller import PulseProgrammerController

PulseProgrammer = Module(PulseProgrammerModel, PulseProgrammerView, PulseProgrammerController)
