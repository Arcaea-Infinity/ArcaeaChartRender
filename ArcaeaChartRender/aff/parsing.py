"""
Abstract::

Compose your Arcaea chart by Python DSL (Domain-Specific Language).

This file provides the tools needed for the initial plain text parsing of the
Arcaea chart (aff files). It mainly uses the pyparsing module for static parsing
and converts all parsing results to ParserElement instances of this module.

The parsed results are still dict or list classes and need to be converted to
your custom classes using other tools.

Examples::

    aff_parsing.command.parse_string(content)
    aff_parsing.command.parse_string(content).as_dict()
    aff_parsing.timing_group.parse_string(content).as_dict()
    aff_parsing.timing_group.parse_string(content).as_list()
"""

__all__ = [
    'header', 'tap', 'arc_easing_type', 'arctap_hit_sound_type', 'skyline_judgment', 'arctap',
    'arctap_nested', 'arc', 'camera_easing_type', 'camera', 'flick', 'hold',
    'scene_control', 'timing', 'command', 'timing_group',
]

from pyparsing import (
    Word,
    alphanums,
    Suppress,
    printables,
    one_of,
    nested_expr,
    delimited_list,
    pyparsing_common as ppc, Opt,
)

from .token import AffToken

AK = AffToken.Keyword
AV = AffToken.Value
AS = AffToken.Spilt

# e.g. AudioOffset:41
header = Word(alphanums) + AS.header_split + Word(printables)

# e.g. (125117,3);
tap = nested_expr('(', ')', delimited_list(ppc.number))

# arc easing type
arc_easing_type = one_of(AV.Easing.all, as_keyword=True)

# arctap hit sound
arctap_hit_sound_type = one_of(AV.HitSound.all, as_keyword=True) | AV.HitSound.other_wav

# arc skyline judgment
skyline_judgment = one_of(AV.SkyLine.all, as_keyword=True)

# e.g. arctap(28666)
arctap = (
        Suppress(AK.arctap) +
        nested_expr('(', ')', ppc.number)
)

# e.g. [arctap(28666),arctap(28833)]
arctap_nested = nested_expr('[', ']', delimited_list(arctap))

# e.g. arc(28666,28999,0.25,0.25,s,0.00,0.00,0,none,true)[arctap(28666),arctap(28833)];
arc = (
              Suppress(AK.arc) +
              nested_expr('(', ')', delimited_list(ppc.number | arc_easing_type | arctap_hit_sound_type | skyline_judgment))
      ) + Opt(arctap_nested, default=[])

# camera easing type
camera_easing_type = one_of(AV.Camera.all)

# e.g. camera(106150,24.76,0.00,0.00,0.00,0.00,0.00,l,1);
camera = (
        Suppress(AK.camera) +
        nested_expr('(', ')', delimited_list(ppc.number | camera_easing_type))
)

# e.g. flick(114514,0.00,0.00,1.00,-1.00);
flick = (
        Suppress(AK.flick) +
        nested_expr('(', ')', delimited_list(ppc.number))
)

# e.g. hold(95950,96617,2);
hold = (
        Suppress(AK.hold) +
        nested_expr('(', ')', delimited_list(ppc.number))
)

# e.g. scenecontrol(0,hidegroup,0.00,1);
scene_control = (
        Suppress(AK.scene_control) +
        nested_expr('(', ')', delimited_list(ppc.number | Word(alphanums)))
)

# e.g. timing(37500,126.00,4.00);
timing = (
        Suppress(AK.timing) +
        nested_expr('(', ')', delimited_list(ppc.number))
)

command_ = (
        tap.set_results_name(AK.tap, list_all_matches=True) |
        arc.set_results_name(AK.arc, list_all_matches=True) |
        camera.set_results_name(AK.camera, list_all_matches=True) |
        flick.set_results_name(AK.flick, list_all_matches=True) |
        hold.set_results_name(AK.hold, list_all_matches=True) |
        scene_control.set_results_name(AK.scene_control, list_all_matches=True) |
        timing.set_results_name(AK.timing, list_all_matches=True)
)

# timing group
timing_group = (
        Suppress(AK.timing_group) +
        nested_expr('(', ')', delimited_list(Word(alphanums), delim='_')) +
        nested_expr('{', '}', delimited_list(command_, delim=';', allow_trailing_delim=True))
).set_results_name(AK.timing_group, list_all_matches=True)

command = delimited_list(command_ | timing_group, delim=';', allow_trailing_delim=True)
