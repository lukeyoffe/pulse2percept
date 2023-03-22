"""`GSL2022Model`, `GSL2022Spatial`, `GSL2022Temporal`
   [GSL2022]_"""
from .base import Model, SpatialModel, TemporalModel


class GSL2022Spatial(SpatialModel):
    """Spatial response model of [GSL2022]_
    """

    def get_default_params(self):
        """Returns all settable parameters of the GSL model"""
        pass

    def _predict_spatial(self, earray, stim):
        """Predicts the brightness at spatial locations"""
        pass

class GSL2022Temporal(TemporalModel):
    """Temporal model of [GSL2022]_
    """

    def get_default_params(self):
        pass

    def _predict_temporal(self, stim, t_percept):
        pass


class GSL2022Model(Model):
    """[GSL2022]_ Model
    """

    def __init__(self, **params):
        super(GSL2022Model, self).__init__(spatial=GSL2022Spatial(),
                                               temporal=GSL2022Temporal(),
                                               **params)
