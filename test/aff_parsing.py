import textwrap
import pytest

from ArcaeaChartRender.aff import parsing as aff_parsing


class TestAffParsing:

    @pytest.mark.parametrize('line, parsed', [
        ('AudioOffset:160', ['AudioOffset', '160']),
        ('TimingPointDensityFactor:0.8', ['TimingPointDensityFactor', '0.8'])
    ], ids=["AudioOffset", "TimingPointDensityFactor"])
    def test_header(self, line, parsed):
        expected_parsed_list = aff_parsing.header.parse_string(line).as_list()
        assert len(expected_parsed_list) == 3
        assert expected_parsed_list[0] == parsed[0]
        assert expected_parsed_list[2] == parsed[1]

    @pytest.mark.parametrize('line, time, lane', [
        ('(125117,0);', 125117, 0),
        ('(345,4);', 345, 4)
    ])
    def test_tap(self, line, time, lane):
        expected_parsed_list = aff_parsing.tap.parse_string(line).as_list()
        assert len(expected_parsed_list) == 1
        assert len(expected_parsed_list[0]) == 2
        _t, _l = expected_parsed_list[0]
        assert _t == time
        assert _l == lane

    @pytest.mark.parametrize('easing_type', ['s', 'b', 'si', 'so', 'siso', 'sisi', 'soso'])
    def test_arc_easing_type(self, easing_type):
        parsed_list = aff_parsing.arc_easing_type.parse_string(easing_type).as_list()
        assert len(parsed_list) == 1
        assert easing_type == parsed_list[0]

    @pytest.mark.parametrize('hit_sound_type', ['none', 'full', 'incremental', 'glass_wav', 'voice_wav', 'kick_wav'])
    def test_arctap_hit_sound_type(self, hit_sound_type):
        parsed_list = aff_parsing.arctap_hit_sound_type.parse_string(hit_sound_type).as_list()
        assert len(parsed_list) == 1
        assert hit_sound_type == parsed_list[0]

    @pytest.mark.parametrize('skyline_arg', ['true', 'false'])
    def test_skyline_judgment(self, skyline_arg):
        parsed_list = aff_parsing.skyline_judgment.parse_string(skyline_arg).as_list()
        assert len(parsed_list) == 1
        assert skyline_arg == parsed_list[0]

    @pytest.mark.parametrize('line, time', [
        ('arctap(28666)', 28666)
    ])
    def test_arctap(self, line, time):
        parsed = aff_parsing.arctap.parse_string(line).as_list()
        assert len(parsed) == 1
        assert len(parsed[0]) == 1
        assert time == parsed[0][0]

    @pytest.mark.parametrize('line, arctap_list', [
        ('[arctap(28666),arctap(28833)]', [[28666], [28833]])
    ])
    def test_arctap_nested(self, line, arctap_list):
        parsed = aff_parsing.arctap_nested.parse_string(line).as_list()
        assert len(parsed) == 1
        assert len(parsed[0]) == 2
        assert arctap_list == parsed[0]

    @pytest.mark.parametrize('line, parsed_arc_args, parsed_arctap_args', [
        ('arc(28666,28999,0.25,0.25,s,0.00,0.00,0,none,true)[arctap(28666),arctap(28833)];',
         [28666, 28999, 0.25, 0.25, 's', 0.00, 0.00, 0, 'none', 'true'], [[28666], [28833]]),
        ('arc(28666,28999,0.25,0.25,s,0.00,0.00,0,none,true);',
         [28666, 28999, 0.25, 0.25, 's', 0.00, 0.00, 0, 'none', 'true'], [])
    ], ids=["with arctaps", "without arctaps"])
    def test_arc(self, line, parsed_arc_args, parsed_arctap_args):
        arc = aff_parsing.arc.parse_string(line).as_list()
        assert len(arc) == 2
        assert parsed_arc_args == arc[0]
        assert parsed_arctap_args == arc[1]

    @pytest.mark.parametrize('camera_easing_type', ['qi', 'qo', 'reset'])
    def test_camera_easing_type(self, camera_easing_type):
        parsed_list = aff_parsing.camera_easing_type.parse_string(camera_easing_type).as_list()
        assert len(parsed_list) == 1
        assert camera_easing_type == parsed_list[0]

    @pytest.mark.parametrize('line, args', [
        ('camera(106150,24.76,0.00,0.00,0.00,0.00,0.00,l,1);', [106150, 24.76, 0.00, 0.00, 0.00, 0.00, 0.00, 'l', 1])
    ])
    def test_camera(self, line, args):
        camera = aff_parsing.camera.parse_string(line).as_list()
        assert len(camera) == 1
        assert len(camera[0]) == len(args)
        assert args == camera[0]

    @pytest.mark.parametrize('line, args', [
        ('flick(114514,0.00,0.00,1.00,-1.00);', [114514, 0.00, 0.00, 1.00, -1.00])
    ])
    def test_flick(self, line, args):
        parsed = aff_parsing.flick.parse_string(line).as_list(),
        assert len(parsed) == 1
        assert len(parsed[0]) == 1
        assert args == parsed[0][0]

    @pytest.mark.parametrize('line, start, end, lane', [
        ('hold(95950,96617,2);', 95950, 96617, 2)
    ])
    def test_hold(self, line, start, end, lane):
        parsed = aff_parsing.hold.parse_string(line).as_list()
        assert len(parsed) == 1
        assert len(parsed[0]) == 3
        _start, _end, _lane = parsed[0]
        assert _start == start
        assert _end == end
        assert _lane == lane

    @pytest.mark.parametrize('line, args', [
        ('scenecontrol(0,hidegroup,0.00,1);', [0, 'hidegroup', 0.00, 1]),
        ('scenecontrol(102853,trackshow);', [102853, 'trackshow'])
    ], ids=["hidegroup param", "trackshow param"])
    def test_scene_control(self, line, args):
        parsed = aff_parsing.scene_control.parse_string(line).as_list(),
        assert len(parsed) == 1
        assert len(parsed[0]) == 1
        assert args == parsed[0][0]

    @pytest.mark.parametrize('line, time, bpm, beat', [
        ('timing(37500, 126.00, 4.00)', 37500, 126.00, 4.00)
    ])
    def test_timing(self, line, time, bpm, beat):
        parsed_line = aff_parsing.timing.parse_string(line).as_list()
        assert len(parsed_line) == 1
        assert len(parsed_line[0]) == 3
        t, _bpm, _beat = parsed_line[0]
        assert t == time
        assert _bpm == bpm
        assert _beat == beat

    @pytest.mark.parametrize('s, is_noinput', [
        ('''
        timinggroup(noinput){};
        ''', True),
        ('''
        timinggroup(){};
        ''', False)
    ], ids=["Timing group(no input)", "Timing group(without noinput)"])
    def test_timing_group(self, s, is_noinput):
        parsed_dict = aff_parsing.timing_group.parse_string(textwrap.dedent(s)).as_dict()
        assert type(parsed_dict) == dict
        assert 'timinggroup' in parsed_dict
        assert len(parsed_dict['timinggroup'][0]) == 2
        if is_noinput:
            assert 'noinput' in parsed_dict['timinggroup'][0][0]
        else:
            assert 'noinput' not in parsed_dict['timinggroup'][0][0]
