'''
Unit conversion helpers for the USD exporter.
'''
from dataclasses import dataclass
from typing import Optional

_TWO_PI = 6.283185307179586


@dataclass
class StageOpts:
    meters_per_unit: float = 0.001   # 1 stage unit = 1 mm (matches Geant4 internal)
    up_axis: str = "Z"
    tess_segments: int = 32
    tess_tolerance: Optional[float] = None
    default_format: str = "usda"
    instanceable: bool = True


def to_stage_length(q, opts):
    '''Pint Quantity (length) → float in stage units.'''
    return float(q.to('m').magnitude) / opts.meters_per_unit


def to_degrees(q):
    '''Pint Quantity (angle) → float in degrees.'''
    return float(q.to('degree').magnitude)


def is_zero(q):
    '''True if angle quantity is effectively zero.'''
    return abs(float(q.to('rad').magnitude)) < 1e-9


def is_full_circle(q):
    '''True if angle quantity spans a full 2π.'''
    return abs(float(q.to('rad').magnitude) - _TWO_PI) < 1e-9
