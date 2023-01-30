import textwrap
import unittest

import aff_parsing


class AffParsingTestCase(unittest.TestCase):

    def test_header(self):
        line = 'AudioOffset:160'
        self.assertEqual(
            ['AudioOffset', ':', '160'],
            aff_parsing.header.parse_string(line).as_list(),
        )
        line = 'TimingPointDensityFactor:0.8'
        self.assertEqual(
            ['TimingPointDensityFactor', ':', '0.8'],
            aff_parsing.header.parse_string(line).as_list(),
        )

    def test_tap(self):
        line = '(125117,3);'
        self.assertEqual(
            [[125117, 3]],
            aff_parsing.tap.parse_string(line).as_list(),
        )

    def test_arc_easing_type(self):
        line = 's'
        self.assertEqual(
            ['s'],
            aff_parsing.arc_easing_type.parse_string(line).as_list(),
        )
        line = 'si'
        self.assertEqual(
            ['si'],
            aff_parsing.arc_easing_type.parse_string(line).as_list(),
        )
        line = 'siso'
        self.assertEqual(
            ['siso'],
            aff_parsing.arc_easing_type.parse_string(line).as_list(),
        )
        line = 'sisi'
        self.assertEqual(
            ['sisi'],
            aff_parsing.arc_easing_type.parse_string(line).as_list(),
        )
        line = 'soso'
        self.assertEqual(
            ['soso'],
            aff_parsing.arc_easing_type.parse_string(line).as_list(),
        )

    def test_arctap_hit_sound_type(self):
        line = 'none'
        self.assertEqual(
            ['none'],
            aff_parsing.arctap_hit_sound_type.parse_string(line).as_list(),
        )

    def test_skyline_judgment(self):
        line = 'true'
        self.assertEqual(
            ['true'],
            aff_parsing.skyline_judgment.parse_string(line).as_list(),
        )
        line = 'false'
        self.assertEqual(
            ['false'],
            aff_parsing.skyline_judgment.parse_string(line).as_list(),
        )

    def test_arctap(self):
        line = 'arctap(28666);'
        self.assertEqual(
            [[28666]],
            aff_parsing.arctap.parse_string(line).as_list(),
        )

    def test_arctap_nested(self):
        line = '[arctap(28666),arctap(28833)]'
        self.assertEqual(
            [[[28666], [28833]]],
            aff_parsing.arctap_nested.parse_string(line).as_list(),
        )

    def test_arc(self):
        line = 'arc(28666,28999,0.25,0.25,s,0.00,0.00,0,none,true)[arctap(28666),arctap(28833)];'
        self.assertEqual(
            [[28666, 28999, 0.25, 0.25, 's', 0.00, 0.00, 0, 'none', 'true'], [[28666], [28833]]],
            aff_parsing.arc.parse_string(line).as_list(),
        )
        line = 'arc(28666,28999,0.25,0.25,s,0.00,0.00,0,none,true);'
        self.assertEqual(
            [[28666, 28999, 0.25, 0.25, 's', 0.00, 0.00, 0, 'none', 'true'], []],
            aff_parsing.arc.parse_string(line).as_list(),
        )

    def test_camera_easing_type(self):
        line = 'qi'
        self.assertEqual(
            ['qi'],
            aff_parsing.camera_easing_type.parse_string(line).as_list(),
        )
        line = 'qo'
        self.assertEqual(
            ['qo'],
            aff_parsing.camera_easing_type.parse_string(line).as_list(),
        )
        line = 'reset'
        self.assertEqual(
            ['reset'],
            aff_parsing.camera_easing_type.parse_string(line).as_list(),
        )

    def test_camera(self):
        line = 'camera(106150,24.76,0.00,0.00,0.00,0.00,0.00,l,1);'
        self.assertEqual(
            [[106150, 24.76, 0.00, 0.00, 0.00, 0.00, 0.00, 'l', 1]],
            aff_parsing.camera.parse_string(line).as_list(),
        )

    def test_flick(self):
        line = 'flick(114514,0.00,0.00,1.00,-1.00);'
        self.assertEqual(
            [[114514, 0.00, 0.00, 1.00, -1.00]],
            aff_parsing.flick.parse_string(line).as_list(),
        )

    def test_hold(self):
        line = 'hold(95950,96617,2);'
        self.assertEqual(
            [[95950, 96617, 2]],
            aff_parsing.hold.parse_string(line).as_list(),
        )

    def test_scene_control(self):
        line = 'scenecontrol(0,hidegroup,0.00,1);'
        self.assertEqual(
            [[0, 'hidegroup', 0.00, 1]],
            aff_parsing.scene_control.parse_string(line).as_list(),
        )
        line = 'scenecontrol(102853,trackshow);'
        self.assertEqual(
            [[102853, 'trackshow']],
            aff_parsing.scene_control.parse_string(line).as_list(),
        )

    def test_timing(self):
        line = 'timing(37500,126.00,4.00);'
        self.assertEqual(
            [[37500, 126.00, 4.00]],
            aff_parsing.timing.parse_string(line).as_list(),
        )

    def test_timing_group(self):
        s = textwrap.dedent('''
        timinggroup(noinput){
            timing(0,126.00,4.00);
            timing(30476,0.00,4.00);
            arc(129200,154450,-0.13,-0.13,s,1.30,1.30,0,none,true)[arctap(140450),arctap(141284)];
            hold(114519,114578,1);
            arc(124996,124996,0.00,-0.25,s,0.60,0.20,0,none,true);
            scenecontrol(70472,trackhide);
            (72375,1);
        };''')
        self.assertEqual(
            {
                "timinggroup": [
                    [
                        [
                            "noinput"
                        ],
                        {
                            "arc": [
                                [
                                    [
                                        129200,
                                        154450,
                                        -0.13,
                                        -0.13,
                                        "s",
                                        1.3,
                                        1.3,
                                        0,
                                        "none",
                                        "true"
                                    ],
                                    [
                                        [
                                            140450
                                        ],
                                        [
                                            141284
                                        ]
                                    ]
                                ],
                                [
                                    [
                                        124996,
                                        124996,
                                        0.0,
                                        -0.25,
                                        "s",
                                        0.6,
                                        0.2,
                                        0,
                                        "none",
                                        "true"
                                    ],
                                    []
                                ]
                            ],
                            "hold": [
                                [
                                    [
                                        114519,
                                        114578,
                                        1
                                    ]
                                ]
                            ],
                            "scenecontrol": [
                                [
                                    [
                                        70472,
                                        "trackhide"
                                    ]
                                ]
                            ],
                            "tap": [
                                [
                                    [
                                        72375,
                                        1
                                    ]
                                ]
                            ],
                            "timing": [
                                [
                                    [
                                        0,
                                        126.0,
                                        4.0
                                    ]
                                ],
                                [
                                    [
                                        30476,
                                        0.0,
                                        4.0
                                    ]
                                ]
                            ]
                        }
                    ]
                ]
            },
            aff_parsing.timing_group.parse_string(s).as_dict(),
        )


if __name__ == '__main__':
    unittest.main()
