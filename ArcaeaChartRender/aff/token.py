"""
Abstract::

This file defines the token in the aff file.
"""

__all__ = ['AffToken', 'Color']

import enum

from pyparsing import Regex


class AffToken(object):
    class Keyword(object):
        audio_offset = 'AudioOffset'
        timing_point_density_factor = 'TimingPointDensityFactor'
        arc = 'arc'
        arctap = 'arctap'
        camera = 'camera'
        flick = 'flick'
        hold = 'hold'
        scene_control = 'scenecontrol'
        tap = 'tap'  # placeholder, never used in aff file
        timing = 'timing'
        timing_group = 'timinggroup'

    class Value(object):
        class SkyLine(object):
            true = 'true'
            false = 'false'
            designant = 'designant'
            all = [true, false, designant]

        class HitSound(object):
            none = 'none'
            full = 'full'
            incremental = 'incremental'
            glass_wav = 'glass_wav'
            voice_wav = 'voice_wav'
            kick_wav = 'kick_wav'
            other_wav = Regex('[^,]+_wav')  # do not add it to all
            all = [none, full, incremental, glass_wav, voice_wav, kick_wav]

        class Easing(object):
            bezier = 'b'
            straight = 's'
            sine_in = 'si'
            sine_out = 'so'
            sine_in_in = 'sisi'
            sine_out_out = 'soso'
            sine_in_out = 'siso'
            sine_out_in = 'sosi'
            all = [bezier, straight, sine_in, sine_out, sine_in_in, sine_out_out, sine_in_out, sine_out_in]

        class Camera(object):
            cubic_in = 'qi'
            cubic_out = 'qo'
            linear = 'l'
            sine_in_and_out = 's'
            reset = 'reset'
            all = [cubic_in, cubic_out, linear, sine_in_and_out, reset]

        class SceneControl(object):
            track_hide = 'trackhide'
            track_show = 'trackshow'
            track_display = 'trackdisplay'
            redline = 'redline'
            arcahv_distort = 'arcahvdistort'
            arcahv_debris = 'arcahvdebris'
            hide_group = 'hidegroup'
            enwidenlanes = 'enwidenlanes'
            enwidencamera = 'enwidencamera'
            all = [
                track_hide, track_show, track_display, redline, arcahv_distort, arcahv_debris, hide_group,
                enwidenlanes, enwidencamera
            ]

        class TimingGroup(object):
            no_input = 'noinput'
            fading_holds = 'fadingholds'
            angle_x = 'anglex'
            angle_y = 'angley'
            all = [no_input, fading_holds, angle_x, angle_y]

    class Spilt(object):
        header_split = ':'


class Color(enum.Enum):
    """Color of the arc."""
    Error = -1
    Blue = 0
    Red = 1
    Green = 2
    Alpha = 3  # used in PRAGMATISM (BEYOND)

    @classmethod
    def _missing_(cls, value):
        """If a color exceeds 3 in the aff file, it will be defined as Error."""
        return Color.Error
