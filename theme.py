__all__ = ['BaseTheme', 'LightTheme', 'ConflictTheme']

from abc import ABC

from PIL import ImageFont

ColorTuple = tuple[int, int, int, int]


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
    arc_red_color = (255, 105, 180)
    arc_blue_color = (49, 218, 231)
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
