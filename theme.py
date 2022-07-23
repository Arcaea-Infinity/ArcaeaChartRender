__all__ = [
    'BaseTheme', 'LightTheme', 'ConflictTheme',
    'width_track', 'height_track_reserved', 'width_chart', 'height_chart', 'width_note', 'height_note',
    'width_arctap', 'height_arctap', 'width_hold', 'height_hold',
    'additional_canvas_width', 'margin_bg', 'width_gap', 'width_chart_edge', 'width_cover', 'height_cover',
    'default_text_x', 'default_text_size',
    'arc_sampling_rate', 'resize',
]

from abc import ABC

from PIL import ImageFont

ColorTuple = tuple[int, int, int, int]

# size configuration
width_track, height_track_reserved = (320, 250)  # the main track, including comment area (1/5) and chart area (4/5)
width_chart, height_chart = (254, 64)  # the size of tile of the chart area
width_note, height_note = (54, 18)  # the size of (ground) tap
width_arctap, height_arctap = (width_note, 12)  # the size of arctap
width_hold, height_hold = (width_note, 379)  # the size of (ground) hold, 379 is the height of resource

additional_canvas_width = width_chart // 4  # to draw out-of-bounds chart (like testify BYD)
margin_bg = additional_canvas_width // 2  # the margin of the background
width_gap = 2  # the distance from note boundary to lane split line, also the weight of the lane split line
width_chart_edge = 8  # the edge width of the chart area
width_cover = height_cover = height_chart * 4 - margin_bg // 2  # the size of song cover (square)

default_text_x = width_track - width_chart - width_gap * 2  # x-coordinate for comment text
default_text_size = 20

# performance configuration
# Warning: Modifying sampling rate will significantly affect the overall plotting speed.
arc_sampling_rate = 10
resize = 4  # 1/4 of the original assets size


class BaseTheme(ABC):
    tile_path: str  # assets/img/track.png
    tap_path: str  # assets/img/note.png
    hold_path: str  # assets/img/note_hold.png
    arctap_path: str  # assets/img/wall.png
    default_bg_path: str  # assets/img/bg/base_light.jpg

    track_split_line_color: ColorTuple  # 3 vertical split lines to divide track into 4 lanes
    line_bar_color: ColorTuple  # split line of bar
    line_bar_small_color: ColorTuple  # split line of small bar (like quarter note)
    text_bar_time_color: ColorTuple  # comment for bar time
    text_bpm_change_color: ColorTuple  # comment for bpm changes
    text_other_info_color: ColorTuple  # comment for other info
    variable_speed_layer_color: ColorTuple  # a layer for variable speed area
    overlay_color = ColorTuple  # a layer between track and bg

    default_transparency_range = (100, 220)

    transparent_color = (255, 255, 255, 0)
    arc_red_color = (185, 118, 180)  # another: (255, 105, 180)
    arc_blue_color = (76, 141, 184)  # another: (49, 218, 231)
    arc_green_color = (124, 252, 0)
    arc_alpha = (0, 0, 0)  # for arc whose color is Color.Alpha (like PRAGMATISM BYD)
    arc_skyline_color = (144, 138, 144)
    text_song_title_color = (222, 222, 222, 255)  # color for song title at text area
    text_song_title_stroke_color = (70, 70, 70, 255)

    thickness_arc = 10
    thickness_skyline = 2

    # for comment on the left side of the chart
    font_Exo_SemiBold_20 = ImageFont.truetype('./assets/Fonts/Exo-SemiBold.ttf', 20)
    # for song title at text area
    font_Kazesawa_Regular_54 = ImageFont.truetype('./assets/Fonts/Kazesawa-Regular.ttf', 54)
    # for artist / chart designer / jacket designer at text area
    font_SourceHanMonoSC_Regular_40 = ImageFont.truetype('./path/to/SourceHanMonoSC-Regular.otf', 40)
    # for statistics at text area
    font_SourceHanMonoSC_Regular_34 = ImageFont.truetype('./path/to/SourceHanMonoSC-Regular.otf', 34)


class LightTheme(BaseTheme):
    tile_path = './assets/img/track.png'
    tap_path = './assets/img/note.png'
    hold_path = './assets/img/note_hold.png'
    arctap_path = './assets/img/wall.png'
    default_bg_path = './assets/img/bg/base_light.jpg'

    track_split_line_color = (46, 31, 60, 192)
    line_bar_color = (210, 210, 210, 180)
    line_bar_small_color = (128, 128, 128, 25)
    text_bar_time_color = (0, 0, 0, 255)
    text_bpm_change_color = (0, 102, 255, 255)
    text_other_info_color = (12, 12, 12, 255)
    variable_speed_layer_color = (255, 255, 102, 50)
    overlay_color = (200, 200, 200, 120)


class ConflictTheme(BaseTheme):
    tile_path = './assets/img/track_dark.png'
    tap_path = './assets/img/note_dark.png'
    hold_path = './assets/img/note_hold_dark.png'
    arctap_path = './assets/img/wall.png'
    default_bg_path = './assets/img/bg/base_conflict.jpg'

    track_split_line_color = (210, 210, 210, 40)
    line_bar_color = (100, 100, 100, 180)
    line_bar_small_color = (240, 248, 255, 8)
    text_bar_time_color = (233, 233, 233, 255)
    text_bpm_change_color = (51, 102, 255, 255)
    text_other_info_color = (233, 233, 233, 255)
    variable_speed_layer_color = (255, 255, 102, 50)
    overlay_color = (50, 50, 50, 200)
