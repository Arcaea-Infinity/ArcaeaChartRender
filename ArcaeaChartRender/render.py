__all__ = ['Render']

import os
from math import ceil, sin, cos, pi
from textwrap import dedent
from typing import Optional, Iterator

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .aff.decoder import parse_aff
from .aff.token import AffToken, Color
from .element import Tap, Arc, Hold, Timing, ArcTap
from .model import Song
from .theme_local import (
    width_track, height_track_reserved,
    width_chart, height_chart,
    width_note, height_note,
    width_arctap, height_arctap,
    width_hold, height_hold,
    additional_canvas_width,
    margin_bg,
    width_gap,
    width_chart_edge,
    width_cover, height_cover,
    default_text_x,
    default_text_size,
    arc_sampling_rate, resize,
    BaseTheme, LightTheme, ConflictTheme,
)
from .utils import read_file, ms_to_sexagesimal


class Coordinate(object):

    @staticmethod
    def from_cartesian(height_track: int, y: int, object_height: Optional[int] = None) -> int:
        """
        In the Cartesian coordinate system, X is the distance from the left
        boundary and Y is the distance from the lower boundary. However, in the
        Pillow coordinate system, Y is the distance from the upper boundary.

        This function converts coordinates between Cartesian and Pillow coordinate
        systems. 'object_height' is the height of the object whose coordinates
        are to be converted, and when this value is specified, objects with height
        can be converted to the correct coordinates.
        """
        return height_track - y - object_height if object_height else height_track - y

    @staticmethod
    def from_normalized(
            coordinate: tuple[float, float],
            transparency_range: tuple[int, int] = BaseTheme.default_transparency_range,
    ) -> tuple[int, int]:
        """
        Linearly converts the X-value of the normalized sample point to the actual
        X-value in the main track, and linearly converts the Z-value (or altitude)
        of the sample point to transparency according to a given transparency range.
        """
        x, z = coordinate
        tp_min, tp_max = transparency_range
        return (
            int(
                x * (width_gap * 6 + width_note * 2) +
                width_track - width_chart + width_chart_edge + width_gap * 2 + width_note
            ),
            int(tp_min + (tp_max - tp_min) * z)  # y: 0.0 ~ 1.0 -> tp_min ~ tp_max
        )


class Sample(object):

    def __init__(self, arc: Arc):
        self.start = arc.t1
        self.end = arc.t2
        self.x1, self.x2 = arc.x1, arc.x2
        self.y1, self.y2 = arc.y1, arc.y2
        self.easing = arc.easing

    def get_coordinate_list(
            self,
            sampling_rate: int,
            transparency_range: tuple[int, int] = BaseTheme.default_transparency_range,
    ) -> Iterator[tuple[int, int, int]]:
        """
        Sample the Arc and return the sampled coordinate values as an iterator.

        Return a list of int tuple ``(x, t, z)``::

            x: Same as the PIL coordinate system, i.e. the distance from the left boundary.
            t: Actual time, you should use coordinate_convert(t // resize) to convert it.
            z: The transparency of the sampling points (use given transparency range).
        """
        for t in range(self.start, self.end, sampling_rate):
            x, z = Coordinate.from_normalized(self.get_coordinate_tuple(t), transparency_range)
            yield x, t, z

    def get_coordinate_tuple(self, t: int) -> tuple[float, float]:
        """
        Get the original coordinates of the point in Arcaea at the given time.

        Return a float tuple ``(x, z)``::

            x: from -0.5 to 1.5
            z: from 0.0 to 1.0
        """
        p = (t - self.start) / (self.end - self.start)  # p is the normalized time
        easing = AffToken.Value.Easing

        x = {
            easing.straight: self._s,
            easing.bezier: self._b,
            easing.sine_in: self._i,
            easing.sine_in_in: self._i,
            easing.sine_in_out: self._i,
            easing.sine_out: self._o,
            easing.sine_out_in: self._o,
            easing.sine_out_out: self._o,
        }.get(self.easing, self._s)(p, self.x1, self.x2)
        z = {
            easing.straight: self._s,
            easing.sine_in: self._s,
            easing.sine_out: self._s,
            easing.bezier: self._b,
            easing.sine_in_in: self._i,
            easing.sine_out_in: self._i,
            easing.sine_in_out: self._o,
            easing.sine_out_out: self._o,
        }.get(self.easing, self._s)(p, self.y1, self.y2)

        return x, z

    @staticmethod
    def _s(p: float, start: float, end: float) -> float: return (1 - p) * start + p * end

    @staticmethod
    def _o(p: float, start: float, end: float) -> float: return start + (end - start) * (1 - cos(pi / 2 * p))

    @staticmethod
    def _i(p: float, start: float, end: float) -> float: return start + (end - start) * sin(pi / 2 * p)

    @staticmethod
    def _b(p: float, start: float, end: float) -> float:
        q = 1 - p
        return q ** 3 * start + 3 * q ** 2 * p * start + 3 * q * p ** 2 * end + p ** 3 * end


class Render(object):

    def __init__(self, aff_path: str, cover_path: str, song: Song, difficulty: int, constant: Optional[float] = None):
        self._aff_path = aff_path
        self._cover_path = cover_path
        self._song = song
        self._difficulty = difficulty
        self._constant = constant
        self._chart = parse_aff(read_file(aff_path))

        # the final height of the chart
        self.h = self._chart.end_time // resize + height_track_reserved

        self._render()

    def _render(self):
        self.theme = ConflictTheme if self._song.side == 1 else LightTheme  # for Colorless and Lephon
        self.im = Image.new('RGBA', (width_track + additional_canvas_width, self.h), self.theme.transparent_color)

        self._draw_track_tile()
        self._draw_track_bar()
        self._draw_track_split_line()
        self._draw_variable_speed_layer()
        self._draw_note_tap()
        self._draw_note_hold()
        self._draw_arc()
        self._draw_arc_tap()

        self._add_comment_bpm_change()
        self._post_processing_segment()
        self._post_processing_background()
        self._post_processing_song_cover()
        self._post_processing_song_meta()
        self._post_processing_add_slogan()

    def _draw_track_tile(self):
        """Tile the background image (track.png) to fill the track."""
        tile = Image.open(self.theme.tile_path).convert('RGBA').resize((width_chart, height_chart))
        for i in range(int(self.h / height_note) + 1):
            self.im.paste(tile, (width_track - width_chart, i * height_chart))

    def _draw_track_bar(self):
        """Draw the track bar line and time elapsed based on the actual bpm value."""
        bar_size = width_chart - 2 * width_chart_edge, width_gap
        bar_size_small = width_chart - 2 * width_chart_edge, width_gap // 2
        im_line_bar = Image.new('RGBA', bar_size, self.theme.line_bar_color)
        im_line_bar_small = Image.new('RGBA', bar_size_small, self.theme.line_bar_small_color)
        draw = ImageDraw.Draw(self.im)

        timing_position_list = self._chart.timing_position_list
        timing_value_list = self._chart.timing_value_list
        timing_beats_list = self._chart.timing_beats_list

        for index, bpm in enumerate(timing_value_list):
            timing_duration = timing_position_list[index + 1] - timing_position_list[index]
            if bpm < self._song.bpm_base // 10:
                continue  # abandon drawing lines with strange bpm (zero, negative or too small)
            bar_duration = 60000 / bpm
            for i in range(ceil(timing_duration / bar_duration + 1)):
                x = width_track - width_chart + width_chart_edge
                t = int(timing_position_list[index] + i * bar_duration) // resize
                if i % timing_beats_list[index] == 0:
                    self.im.alpha_composite(im_line_bar, (x, Coordinate.from_cartesian(self.h, t, width_gap)))
                    draw.text(
                        (default_text_x, Coordinate.from_cartesian(self.h, t)),
                        ms_to_sexagesimal(t * resize),
                        font=self.theme.font_Exo_SemiBold_20,
                        fill=self.theme.text_bar_time_color,
                        anchor='rs'
                    )  # draw time elapsed
                    draw.text(
                        (default_text_x, Coordinate.from_cartesian(self.h, t) - default_text_size),
                        str(self._chart.get_total_combo_before(t * resize)),
                        font=self.theme.font_Exo_SemiBold_20,
                        fill=self.theme.text_bar_time_color,
                        anchor='rs'
                    )  # draw combo before this bar
                else:  # draw lines for smaller beats
                    self.im.alpha_composite(im_line_bar_small, (x, Coordinate.from_cartesian(self.h, t, width_gap)))

    def _draw_track_split_line(self):
        """Draw 3 split lines on the track to separate each lane's area."""
        split_line = Image.new('RGBA', (width_gap, self.h), self.theme.track_split_line_color)
        for i in range(1, 4):
            x = width_track - width_chart + width_chart_edge + width_gap * (3 * i - 1) + width_note * i
            self.im.alpha_composite(split_line, (x, 0))

    def _draw_variable_speed_layer(self):
        """
        Overlap a layer of color in the chart to indicate that the segment's bpm
        is different from bpm_base.
        """
        im_variable_speed = Image.new('RGBA', self.im.size, self.theme.transparent_color)
        draw = ImageDraw.Draw(im_variable_speed)

        timing_position_list = self._chart.timing_position_list
        timing_value_list = self._chart.timing_value_list

        for index, bpm in enumerate(timing_value_list):
            if bpm != self._song.bpm_base:
                bpm_start_t = Coordinate.from_cartesian(self.h, timing_position_list[index] // resize)
                bpm_end_t = Coordinate.from_cartesian(self.h, timing_position_list[index + 1] // resize)
                draw.rectangle(
                    (width_track - width_chart, bpm_end_t, width_track, bpm_start_t),
                    self.theme.variable_speed_layer_color
                )

        self.im.alpha_composite(im_variable_speed)

    def _draw_note_tap(self):
        """Draw all Taps in the chart."""
        im_tap = Image.open(self.theme.tap_path).convert('RGBA').resize((width_note, height_note))
        for tap in self._chart.get_command_list_for_type(Tap, search_in_timing_group=True, exclude_noinput=False):
            lane = tap.lane
            x = width_track - width_chart + width_chart_edge + width_gap * (3 * lane - 2) + width_note * (lane - 1)
            t = tap.t // resize
            self.im.alpha_composite(im_tap, (int(x), Coordinate.from_cartesian(self.h, t, height_note)))

    def _draw_note_hold(self):
        """Draw all Holds in the chart."""
        im_hold = Image.open(self.theme.hold_path).convert('RGBA').resize((width_hold, height_hold))
        for hold in self._chart.get_command_list_for_type(Hold, search_in_timing_group=True, exclude_noinput=False):
            lane = hold.lane
            stretched_height_hold = (hold.t2 - hold.t1) // resize
            if not stretched_height_hold:  # t2 == t1
                continue
            im_stretched_hold = im_hold.resize((width_hold, stretched_height_hold))
            x = width_track - width_chart + width_chart_edge + width_gap * (3 * lane - 2) + width_note * (lane - 1)
            t = hold.t1 // resize
            self.im.alpha_composite(im_stretched_hold, (int(x), Coordinate.from_cartesian(self.h, t, stretched_height_hold)))


    def _draw_arc_tap(self):
        """Draw all ArcTaps on skyline."""
        im_arctap = Image.open(self.theme.arctap_path).convert('RGBA').resize((width_arctap, height_arctap))
        im_arctap_sfx = Image.open(self.theme.arctap_sfx_path).convert('RGBA')
        im_arctap_sfx = im_arctap_sfx.resize((width_arctap, height_arctap))
        im_arctap_designant = Image.open(self.theme.arctap_designant_path).convert(
            'RGBA').resize((width_arctap, height_arctap))

        def skyline_or_designant(arc: Arc) -> Image.Image:
            return im_arctap if arc.is_skyline is True else im_arctap_designant

        for arc in self._chart.get_command_list_for_type(Arc, search_in_timing_group=True, exclude_noinput=False):
            sample = Sample(arc)
            which_im_arctap = {
                AffToken.Value.HitSound.glass_wav: im_arctap_sfx,
                AffToken.Value.HitSound.voice_wav: im_arctap_sfx,
                AffToken.Value.HitSound.kick_wav: im_arctap_sfx,
            }.get(arc.hit_sound, skyline_or_designant(arc))
            for arctap in arc.arctap_list:  # An Arc with an empty arctap_list will be automatically skipped.
                x, z = Coordinate.from_normalized(sample.get_coordinate_tuple(arctap.tn))
                t = arctap.tn // resize
                which_im_arctap.putalpha(z)
                self.im.alpha_composite(
                    which_im_arctap,
                    (x - width_arctap // 2, Coordinate.from_cartesian(self.h, t, height_arctap))
                )

    def _draw_arc(self):
        """(use opencv2) Draw all Arcs in the chart. """
        matrix_size = *reversed(self.im.size), 4  # (width, height, 4)
        im_arc_red = np.zeros(matrix_size, dtype=np.uint8)
        im_arc_blue = np.zeros(matrix_size, dtype=np.uint8)
        im_arc_green = np.zeros(matrix_size, dtype=np.uint8)
        im_arc_skyline = np.zeros(matrix_size, dtype=np.uint8)

        for arc in self._chart.get_command_list_for_type(Arc, search_in_timing_group=True, exclude_noinput=False):
            # create sampling list
            arc_path_list = []
            arc_alpha_list = []
            for x, t, z in Sample(arc).get_coordinate_list(arc_sampling_rate):
                arc_path_list.append((x, Coordinate.from_cartesian(self.h, t // resize)))
                arc_alpha_list.append(z)
            # set parameters
            if not arc.is_skyline:
                im, color = {
                    Color.Red: (im_arc_red, self.theme.arc_red_color),
                    Color.Blue: (im_arc_blue, self.theme.arc_blue_color),
                    Color.Green: (im_arc_green, self.theme.arc_green_color),
                }.get(arc.color)
                thickness = self.theme.thickness_arc
            elif arc.is_skyline is True:
                im, color, thickness = im_arc_skyline, self.theme.arc_skyline_color, self.theme.thickness_skyline
            elif arc.is_skyline == 'Designant':
                im, color, thickness = im_arc_skyline, self.theme.arc_designant_color, self.theme.thickness_skyline
            else:
                raise TypeError(f'Unsupported arc type: {arc}')
            # draw arc or skyline
            for xy_start, xy_end, alpha in zip(arc_path_list, arc_path_list[1:], arc_alpha_list[1:]):
                cv2.line(im, xy_start, xy_end, (*color, alpha), thickness, cv2.LINE_AA)

        self.im.alpha_composite(Image.fromarray(im_arc_red))
        self.im.alpha_composite(Image.fromarray(im_arc_blue))
        self.im.alpha_composite(Image.fromarray(im_arc_green))
        self.im.alpha_composite(Image.fromarray(im_arc_skyline))

    def _add_comment_bpm_change(self):
        """Add comment for bpm change to the left of the chart """
        draw = ImageDraw.Draw(self.im)
        for timing in self._chart.get_command_list_for_type(Timing):
            text_t = Coordinate.from_cartesian(self.h, timing.t // resize)
            draw.text(
                (default_text_x + 2 * width_chart_edge, text_t),
                str(timing.bpm),
                fill=self.theme.text_bpm_change_color,
                font=self.theme.font_Exo_SemiBold_20, anchor='ls'
            )

    def _post_processing_segment(self):
        """Split the chart into multiple segments and then tile them from left to right."""
        bpm_proportion = self._chart.get_bpm_proportion()
        main_bpm = max(bpm_proportion, key=bpm_proportion.get)

        # ignore the bpm that is too small (Aleph-0 Present)
        if main_bpm < 10:
            main_bar_duration = 4 * 60000 / self._song.bpm_base
        else:
            main_bar_duration = 4 * 60000 / main_bpm

        segment = int(self._chart.end_time / 10000)
        segment_duration = (self._chart.end_time / segment // main_bar_duration or 1) * main_bar_duration
        segment_count = ceil(self._chart.end_time / segment_duration)
        segment_height = segment_duration / resize  # do not use int() here avoid accumulating errors

        size = segment_count * width_track + additional_canvas_width, int(segment_height)
        self.im_tiled_segments = Image.new('RGBA', size, self.theme.transparent_color)
        for i in range(segment_count):
            box = (
                0, Coordinate.from_cartesian(self.h, (i + 1) * segment_height),
                width_track + additional_canvas_width, Coordinate.from_cartesian(self.h, i * segment_height)
            )
            im_cropped = Image.Image.crop(self.im, box)
            self.im_tiled_segments.alpha_composite(im_cropped, (i * width_track, 0))
        self.im = self.im_tiled_segments

    def _post_processing_background(self):
        """Add background and overlay."""
        width_bg, height_bg = self.im.size[0] + margin_bg * 2, self.im.size[1] + height_chart * 4 + margin_bg * 2
        width_chart_overlay, height_chart_overlay = self.im.size[0] + margin_bg, self.im.size[1] + margin_bg
        width_text_overlay, height_text_overlay = self.im.size[0] + margin_bg, width_cover

        bg_path = os.path.join(self.theme.custom_bg_dir_path, f'{self._song.bg}.jpg')
        if not os.path.isfile(bg_path):
            bg_path = self.theme.default_bg_path
        im_bg = Image.open(bg_path).convert('RGBA')
        im_chart_overlay = Image.new('RGBA', (width_chart_overlay, height_chart_overlay), self.theme.overlay_color)
        im_text_overlay = Image.new('RGBA', (width_text_overlay, height_text_overlay), self.theme.overlay_color)

        width_bg_origin, height_bg_origin = im_bg.size  # size of original background image
        im_bg = im_bg.resize(
            (width_bg, int(width_bg * width_bg_origin / height_bg_origin))
        ).crop(
            (0, 0, width_bg, height_bg)
        )

        im_bg.alpha_composite(im_chart_overlay, (margin_bg // 2, margin_bg // 2))
        im_bg.alpha_composite(im_text_overlay, (margin_bg // 2, height_chart_overlay + margin_bg))
        im_bg.alpha_composite(self.im, (margin_bg, margin_bg))
        self.im = im_bg

    def _post_processing_song_cover(self):
        """Add song cover thumbnail to the left of text area."""
        im_song_cover = Image.open(self._cover_path).convert('RGBA').resize((width_cover, height_cover))
        self.im.alpha_composite(im_song_cover, (margin_bg // 2, self.im.size[1] - height_cover - margin_bg // 2))

    def _post_processing_song_meta(self):
        """Add song metadata at text area."""
        draw = ImageDraw.Draw(self.im)
        this_diff = next(x for x in self._song.difficulties if x.ratingClass == self._difficulty)
        # title
        draw.text(
            xy=(width_cover + margin_bg * 2, self.im.size[1] - height_cover - margin_bg // 2),
            text=self._song.title_localized.en,
            fill=self.theme.text_song_title_color,
            font=self.theme.font_Kazesawa_Regular_54,
            stroke_width=3,
            stroke_fill=self.theme.text_song_title_stroke_color
        )
        # artist / chart designer / jacket designer
        chart_designer = this_diff.chartDesigner.replace('\n', ' ')
        jacket_designer = this_diff.jacketDesigner.replace('\n', ' ')
        draw.text(
            xy=(width_cover + margin_bg * 2, self.im.size[1] - height_cover + 54),  # 54 is song title font size
            text=dedent(f'''\
            Artist: {self._song.artist}
            Chart Designer: {chart_designer}
            Jacket Designer: {jacket_designer}
            '''),
            fill=self.theme.text_other_info_color,
            font=self.theme.font_SourceHanMonoSC_Regular_40,
        )
        # combo / tap / arctap / hold / arc
        draw.text(
            xy=(self.im.size[0] // 2, self.im.size[1] - height_cover - margin_bg // 2),
            text=dedent(f'''\
            Combo  : {self._chart.get_total_combo()}
            Tap    : {self._chart.get_combo_of(Tap)}
            ArcTap : {self._chart.get_combo_of(ArcTap)}
            Hold   : {self._chart.get_combo_of(Hold)}
            Arc    : {self._chart.get_combo_of(Arc)}
            '''),
            fill=self.theme.text_other_info_color,
            font=self.theme.font_SourceHanMonoSC_Regular_34,
        )
        # duration / BPM / base BPM / difficulty / constant
        literal_difficulty = ['Past', 'Present', 'Future', 'Beyond', 'Eternal'][self._difficulty]
        draw.text(
            xy=(self.im.size[0] // 5 * 3, self.im.size[1] - height_cover - margin_bg // 2),
            text=dedent(f'''\
            Duration : {ms_to_sexagesimal(self._chart.end_time)}
            BPM      : {self._song.bpm}
            Base BPM : {self._song.bpm_base}
            Level    : {literal_difficulty} [{this_diff.rating}{'+' if this_diff.ratingPlus else ''}]
            Constant : {self._constant:.1f}
            '''),
            fill=self.theme.text_other_info_color,
            font=self.theme.font_SourceHanMonoSC_Regular_34,
        )

    def _post_processing_add_slogan(self):
        """Add slogan to the bottom right corner of the image."""
        draw = ImageDraw.Draw(self.im)
        draw.text(
            xy=(self.im.size[0] - margin_bg, self.im.size[1] - margin_bg),
            text=self.theme.slogan,
            fill=self.theme.text_other_info_color,
            font=self.theme.font_Exo_SemiBold_40,
            anchor='rs'
        )

    def save(self, path: str, **kwargs):
        self.im.save(path, **kwargs)

    def show(self):
        self.im.show()
