"""
Abstract::

This file defines all elements in the Arcaea chart file (aff).
Definition extracted from https://wiki.arcaea.cn

Each element provides a minimal syntax check, but it is not perfect,
so please DO NOT rely on it too much.
"""

__all__ = [
    'Command',
    'Element', 'Chart',
    'Header', 'Note', 'Control',
    'AudioOffset', 'TimingPointDensityFactor',
    'Tap', 'Hold', 'Arc', 'ArcTap', 'Flick',
    'Timing', 'Camera', 'SceneControl', 'TimingGroup',
]

from abc import ABC
from typing import Union, Optional

from aff_token import AffToken, Color

AnyValue = Union[str, int, float]
Command = Union['Note', 'Control']


class Element(ABC):
    pass


class Chart(object):
    """Arcaea chart."""

    def __init__(self, header: list['Header'], command: list[Command]):
        self.header = header
        self.command = command

    def _get_tap_combo(self) -> int:
        """Return the number of Tap note"""
        count_in_cmd = sum(1 for tap in self.command if isinstance(tap, Tap))
        count_in_timing_group = sum(
            1
            for timing_group in self.command if isinstance(timing_group, TimingGroup)
            for tap in timing_group.item if isinstance(tap, Tap)
        )
        return count_in_cmd + count_in_timing_group

    def _get_arctap_combo(self) -> int:
        """Return the number of ArcTap note"""
        count_in_cmd = sum(
            1
            for arc in self.command if isinstance(arc, Arc)
            for _ in arc.arctap_list
        )
        count_in_timing_group = sum(
            1
            for timing_group in self.command if isinstance(timing_group, TimingGroup)
            for arc in timing_group.item if isinstance(arc, Arc)
            for _ in arc.arctap_list
        )
        return count_in_cmd + count_in_timing_group

    def _get_hold_combo(self) -> int:
        """Return the total combo of the Hold note"""
        raise NotImplementedError

    def get_total_combo(self) -> int:
        """Return the total combo of the chart."""
        raise NotImplementedError

    def syntax_check(self) -> bool:
        """Check the syntax of the chart as a whole."""
        raise NotImplementedError


class Header(Element):
    """Chart header, a k-v pair."""

    def __init__(self, key: str, value: AnyValue):
        self.key = key
        self.value = value

    def __repr__(self):
        return f'{self.key}:{self.value}'


class AudioOffset(Header):
    """Audio delay of the chart."""

    def __init__(self, value: int):
        super().__init__(AffToken.Keyword.audio_offset, value)


class TimingPointDensityFactor(Header):
    """Multiplicity of Arc and Hold densities relative to the normal case."""

    def __init__(self, value: float):
        super().__init__(AffToken.Keyword.timing_point_density_factor, value)


class Note(Element):
    """Base class for all note types."""

    def syntax_check(self) -> bool:
        """Basic syntax check of a note. DO NOT rely on it too much."""
        raise NotImplementedError


class Tap(Note):
    """Ground tap."""

    def __init__(self, t: int, lane: int):
        self.t = t
        self.lane = lane

    def __repr__(self):
        return f'[{self.t} Tap] on lane {self.lane}'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t, int),
            self.lane in range(1, 5),
        ])


class Hold(Note):
    """Ground hold."""

    def __init__(
            self,
            t1: int, t2: int,
            lane: int
    ):
        self.t1 = t1
        self.t2 = t2
        self.lane = lane

    def __repr__(self):
        return f'[{self.t1} -> {self.t2} Hold] on lane {self.lane}'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t1, int),
            isinstance(self.t2, int),
            self.t1 <= self.t2,
            self.lane in range(1, 5),
        ])


class Arc(Note):
    """Arc."""

    def __init__(
            self,
            t1: int, t2: int,
            x1: float, x2: float,
            easing: str,
            y1: float, y2: float,
            color: int,
            FX: str,
            is_skyline: str,
            arctap_list: list[Optional['ArcTap']],
    ):
        self.t1 = t1
        self.t2 = t2
        self.x1 = x1
        self.x2 = x2
        self.easing = easing
        self.y1 = y1
        self.y2 = y2
        self.color = Color(color)
        self.FX = FX
        # Regardless of the value of is_skyline,
        # as long as arctap_list exists, then it must be skyline.
        self.is_skyline = {
                              AffToken.Value.SkyLine.true: True,
                              AffToken.Value.SkyLine.false: False
                          }[is_skyline] or bool(arctap_list)
        self.arctap_list = arctap_list

    def __repr__(self):
        if self.is_skyline:
            if self.arctap_list:
                literal_arctap_list = ', with arctap: ' + ' '.join(map(lambda _: str(_.tn), self.arctap_list))
            else:
                literal_arctap_list = ''
            return (
                f'[{self.t1} -> {self.t2} Skyline] from ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})'
                f'{literal_arctap_list}'
            )
        return f'[{self.t1} -> {self.t2} {self.color} Arc] from ({self.x1}, {self.y1}) to ({self.x2}, {self.y2})'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t1, int),
            isinstance(self.t2, int),
            any([
                self.t1 <= self.t2,
                self.t1 > self.t2 and self.is_skyline,
            ]),
            self.t1 >= 0,
            self.t2 >= 0,
            isinstance(self.x1, float),
            isinstance(self.x2, float),
            isinstance(self.y1, float),
            isinstance(self.y2, float),
            self.color != Color.Error,
            self.easing in AffToken.Value.Easing.all,
            self.FX in AffToken.Value.FX.all,
        ])

    def get_arctap_count(self) -> int:
        """Return the number of ArcTap note on this Arc."""
        return len(self.arctap_list)


class ArcTap(Note):
    """Taps on skyline."""

    def __init__(
            self,
            tn: int,
            arc_timing_window: tuple[int, int],
            color: int
    ):
        self.tn = tn
        self.arc_timing_window = arc_timing_window  # (t1, t2) of the located arc
        self.color = Color(color)

    def __repr__(self):
        return f'[{self.tn} ArcTap] on Arc ({self.arc_timing_window}), {self.color})'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.tn, int),
            self.arc_timing_window[0] <= self.tn <= self.arc_timing_window[1],
        ])


class Flick(Note):
    """Flick. NEVER used in practice."""

    def __init__(
            self,
            t: int,
            x: float, y: float,
            vx: float, vy: float
    ):
        self.t = t
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def __repr__(self):
        return f'[{self.t} Flick] at ({self.x}, {self.y}) with velocity ({self.vx}, {self.vy})'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t, int),
            isinstance(self.x, float),
            isinstance(self.y, float),
            isinstance(self.vx, float),
            isinstance(self.vy, float),
        ])


class Control(Element):

    def syntax_check(self) -> bool:
        """Basic syntax check of a control. DO NOT rely on it too much."""
        raise NotImplementedError


class Timing(Control):
    """Change bpm and beats."""

    def __init__(
            self,
            t: int,
            bpm: float, beats: float,
            in_timing_group: bool = False
    ):
        self.t = t
        self.bpm = bpm
        self.beats = beats
        self.in_timing_group = in_timing_group

    def __repr__(self):
        return f'[{self.t} Timing] change bpm to {self.bpm} with {self.beats} beats'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t, int),
            isinstance(self.bpm, float),
            isinstance(self.beats, float),
            any([
                self.beats != 0,
                self.in_timing_group,
            ]),
            any([
                self.bpm >= 0,
                self.t != 0,
                self.in_timing_group,
            ])
        ])


class Camera(Control):
    """Change camera position. Only works properly in the April Fool's version."""

    def __init__(
            self,
            t: int,
            transverse: float,
            bottom_zoom: float,
            line_zoom: float,
            steady_angle: float,
            top_zoom: float,
            angle: float,
            easing: str,
            lasting_time: int
    ):
        self.t = t
        self.transverse = transverse
        self.bottom_zoom = bottom_zoom
        self.line_zoom = line_zoom
        self.steady_angle = steady_angle
        self.top_zoom = top_zoom
        self.angle = angle
        self.easing = easing
        self.lasting_time = lasting_time

    def __repr__(self):
        return (
            f'[{self.t} Camera] zoom: ({self.transverse}, {self.bottom_zoom}, {self.line_zoom}), '
            f'angle: ({self.steady_angle}, {self.top_zoom}, {self.angle}), '
            f'lasting: {self.lasting_time}'
        )

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t, int),
            isinstance(self.transverse, float),
            isinstance(self.bottom_zoom, float),
            isinstance(self.line_zoom, float),
            isinstance(self.steady_angle, float),
            isinstance(self.top_zoom, float),
            isinstance(self.angle, float),
            self.easing in AffToken.Value.Camera.all,
            isinstance(self.lasting_time, int),
        ])


class SceneControl(Control):
    """Control the performance effect."""

    def __init__(
            self,
            t: int,
            type_: str,
            param1: Optional[float] = None,
            param2: Optional[int] = None,
    ):
        self.t = t
        self.type_ = type_
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f'[{self.t} SceneControl] type: {self.type_}'

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.t, int),
            self.type_ in AffToken.Value.SceneControl.all,
            any([  # syntax check for specific scene control types
                all([
                    self.type_ in [
                        AffToken.Value.SceneControl.track_hide,
                        AffToken.Value.SceneControl.track_show,
                        AffToken.Value.SceneControl.arcahv_distort
                    ],
                    self.param1 is None,
                    self.param2 is None,
                ]),
                all([
                    self.type_ in [
                        AffToken.Value.SceneControl.track_display,
                        AffToken.Value.SceneControl.redline,
                        AffToken.Value.SceneControl.arcahv_debris
                    ],
                    isinstance(self.param1, float),
                    isinstance(self.param2, int),
                ]),
                all([
                    self.type_ == AffToken.Value.SceneControl.hide_group,
                    isinstance(self.param1, float),
                    self.param2 in range(2),
                ])
            ]),
        ])


class TimingGroup(Control):
    """Use the internal independent timing statements to control Notes and Controls within the group."""

    def __init__(
            self,
            type_list: list[str],
            item: list[Command]
    ):
        self.type_list = type_list
        self.item = item

    def __repr__(self):
        literal_type = f', type: {" ".join(self.type_list)}' if self.type_list else ''
        return f'[TimingGroup] {len(self.item)} commands{literal_type}'

    def __str__(self):
        return self.__repr__() + '\n > ' + '\n > '.join([str(_) for _ in self.item])

    def syntax_check(self) -> bool:
        return all([
            isinstance(self.type_list, list),
            all(sub_type in AffToken.Value.TimingGroup.all for sub_type in self.type_list),
            isinstance(self.item, list),
            all(sub_command.syntax_check() for sub_command in self.item)
        ])

    def sub_command_syntax_check(self) -> list[tuple[Command, bool]]:
        """Check the syntax of each subcommand (Note and Control) within the group individually."""
        return [(sub_command, sub_command.syntax_check()) for sub_command in self.item]
