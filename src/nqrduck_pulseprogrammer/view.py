import logging
from collections import OrderedDict
from PyQt6.QtWidgets import QTableWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSlot
from nqrduck.module.module_view import ModuleView

logger = logging.getLogger(__name__)


class PulseProgrammerView(ModuleView):
    
    def __init__(self, module):
        super().__init__(module)

        self.setup_ui()

        logger.debug("Connecting pulse parameter options changed signal to on_pulse_parameter_options_changed")
        module.model.pulse_parameter_options_changed.connect(self.on_pulse_parameter_options_changed)
        
    def setup_ui(self):
        self.pulse_table = QTableWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.pulse_table)
        self.setLayout(layout)

    @pyqtSlot()
    def on_pulse_parameter_options_changed(self):
        logger.debug("Updating pulse parameter options to %s", self.module.model.pulse_parameter_options.keys())
        self.pulse_table.setRowCount(len(self.module.model.pulse_parameter_options))
        self.pulse_table.setVerticalHeaderLabels(self.module.model.pulse_parameter_options.keys())
        

        
