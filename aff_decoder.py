"""
Decode an aff file into a Chart object.
"""

__all__ = ['decode', 'parse_header', 'parse_command_dict', 'parse_aff']

from typing import Optional

import aff_parsing
from aff_token import AffToken
from element import (
    Chart, Header, Command,
    Tap, Arc, Flick, Hold,
    Camera, SceneControl, Timing, TimingGroup, AudioOffset, TimingPointDensityFactor, ArcTap
)


def decode(command_type: str, command: list, **kwargs) -> Command:
    """Decode a command according to its type."""
    in_timing_group: bool = kwargs.get('in_timing_group', False)

    if command_type == AffToken.Keyword.tap:
        # [[238, 2]]
        return Tap(*command[0])
    elif command_type == AffToken.Keyword.arc:
        # [[28666, 28999, 0.25, 0.25, 's', 0.00, 0.00, 0, 'none', 'true'], [[28666], [28833]]]
        arc = command[0]
        if len(command) == 2:  # with arctap
            arctap_list = list(map(lambda _: ArcTap(_[0], (arc[0], arc[1]), arc[7]), command[1]))
        else:
            arctap_list = []
        return Arc(*arc, arctap_list=arctap_list)
    elif command_type == AffToken.Keyword.flick:
        # [[114514, 0.00, 0.00, 1.00, -1.00]]
        return Flick(*command[0])
    elif command_type == AffToken.Keyword.hold:
        return Hold(*command[0])
    elif command_type == AffToken.Keyword.camera:
        return Camera(*command[0])
    elif command_type == AffToken.Keyword.scene_control:
        return SceneControl(*command[0])
    elif command_type == AffToken.Keyword.timing:
        return Timing(*command[0], in_timing_group=in_timing_group)
    elif command_type == AffToken.Keyword.timing_group:
        # see aff_parsing_unittest.py for examples
        type_: list[Optional[str]] = command[0]
        inner_cmd = parse_command_dict(command[1], in_timing_group=True)
        return TimingGroup(type_, inner_cmd)

    raise ValueError(f'Unknown command type: {command_type}')


def parse_header(line: str) -> Header:
    """Record header k-v pair and return a Header object."""
    key, _, value = aff_parsing.header.parse_string(line)
    if key == AffToken.Keyword.audio_offset:
        return AudioOffset(int(value))
    elif key == AffToken.Keyword.timing_point_density_factor:
        return TimingPointDensityFactor(float(value))
    return Header(key, value)


def parse_command_dict(command_dict: dict[str, list], **kwargs) -> list[Command]:
    """Convert generated command dict into a list of Command objects."""
    result: list[Command] = []

    for command_type, command_list in command_dict.items():
        for command in command_list:
            result.append(decode(command_type, command, **kwargs))

    return result


def parse_aff(aff: list[str]) -> Chart:
    """Parse aff file and return a Chart object."""
    header: list[Header] = []
    command: list[Command]

    # record headers (before '-\n')
    line = aff.pop(0)
    while line != '-\n':
        header.append(parse_header(line))
        line = aff.pop(0)

    # record commands (use PyParsing to parse rest of lines directly)
    rest_content = ''.join(aff)
    command_dict: dict[str, list] = aff_parsing.command.parse_string(rest_content).as_dict()
    # All commands are sorted by type and stored in this dict,
    # each value is a list of commands corresponding to the name of key
    # e.g. command_dict = {"timing": [[[0, 126.0, 4.0]], [[30476, 0.0, 4.0]], ...]}
    command = parse_command_dict(command_dict)

    return Chart(header, command)
