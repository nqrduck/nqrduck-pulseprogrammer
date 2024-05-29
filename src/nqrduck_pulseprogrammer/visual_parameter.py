from nqrduck.assets.icons import PulseParamters
from quackseq.pulseparameters import TXPulse, RXReadout, PulseParameter
from quackseq.functions import Function, RectFunction, SincFunction, GaussianFunction, CustomFunction

class VisualParameter():

    def __init__(self, pulse_parameter : PulseParameter):
        self.pulse_parameter = pulse_parameter

    def get_pixmap(self):
        """Returns the pixmap of the TX Pulse Parameter.

        Returns:
            QPixmap: The pixmap of the TX Pulse Parameter depending on the relative amplitude.
        """
        # Check the instance of the pulse parameter
        if isinstance(self.pulse_parameter, TXPulse):
            amplitude = self.pulse_parameter.get_option_by_name(TXPulse.RELATIVE_AMPLITUDE).value
            if amplitude > 0:
                # Get the shape
                shape = self.pulse_parameter.get_option_by_name(TXPulse.TX_PULSE_SHAPE).value
                if isinstance(shape, RectFunction):
                    pixmap = PulseParamters.TXRect()
                    return pixmap
                elif isinstance(shape, SincFunction):
                    pixmap = PulseParamters.TXSinc()
                    return pixmap
                elif isinstance(shape, GaussianFunction):
                    pixmap = PulseParamters.TXGauss()
                    return pixmap
                else:
                    pixmap = PulseParamters.TXCustom()
                    return pixmap
            else:
                pixmap = PulseParamters.TXOff()
                return pixmap
            
        elif isinstance(self.pulse_parameter, RXReadout):
            rx = self.pulse_parameter.get_option_by_name(RXReadout.RX).value
            if rx:
                pixmap = PulseParamters.RXOn()
                return pixmap
            else:
                pixmap = PulseParamters.RXOff()
                return pixmap
