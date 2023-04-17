"""
Decode an aff file into a Chart object.
"""

__all__ = ['decode', 'parse_header', 'parse_command_dict', 'parse_aff']

from typing import Optional, Any

from .parsing import command, header
from .token import AffToken
from ..element import (
    Chart, Command,
    Tap, Arc, Flick, Hold,
    Camera, SceneControl, Timing, TimingGroup, ArcTap
)


def decode(command_type: str, command: list, in_timing_group: bool = False) -> Command:
    """Decode a command according to its type."""
    if command_type == AffToken.Keyword.tap:
        # [[238, 2]]
        return Tap(*command[0])
    elif command_type == AffToken.Keyword.arc:
        # [[28666, 28999, 0.25, 0.25, 's', 0.00, 0.00, 0, 'none', 'true'], [[28666], [28833]]]
        arc = command[0]
        arctap_list = [
            ArcTap(tn=tn[0], arc_timing_window=(arc[0], arc[1]), color=arc[7])
            for tn in command[1]
        ]
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
        inner_command_list = parse_command_dict(command[1], in_timing_group=True)
        return TimingGroup(type_, inner_command_list)

    raise ValueError(f'Unknown command type: {command_type}')


def parse_header(line: str) -> tuple[str, Any]:
    """Record header k-v pair."""
    key, _, value = header.parse_string(line)
    return key, value


def parse_command_dict(command_dict: dict[str, list], in_timing_group: bool = False) -> list[Command]:
    """
    Convert generated command dict into a list of Command objects.

    All commands are sorted by type and stored in this dict,
    each value is a list of commands corresponding to the name of key

    Usage::

        command_dict = {"timing": [[[0, 126.0, 4.0]], [[30476, 0.0, 4.0]], ...]}
        parse_command_dict(command_dict)
    """
    result: list[Command] = []

    for command_type, command_list in command_dict.items():
        for command in command_list:
            result.append(decode(command_type, command, in_timing_group))

    return result


def parse_aff(aff: list[str]) -> Chart:
    """
    Parse aff file and return a Chart object.

    Usage::

        from utils import read_file
        parse_aff(read_file(aff_path))
    """
    header_dict: dict = {}

    # record headers (before '-\n')
    while (line := aff.pop(0)) != '-\n':
        key, value = parse_header(line)
        header_dict[key] = value

    # record commands (use PyParsing to parse rest of lines directly)
    rest_content = ''.join(aff)
    command_dict: dict[str, list] = command.parse_string(rest_content).as_dict()
    command_list: list[Command] = parse_command_dict(command_dict)

    return Chart(header_dict, command_list)
