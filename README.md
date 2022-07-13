# <p align="center">ArcaeaChartRender
<p align="center">Another chart previewing library for Arcaea.

## Usage

Render an Arcaea Chart simply.

```python
from ArcaeaChartRender.model import Song
from ArcaeaChartRender.render import Render
from ArcaeaChartRender.utils import fetch_song_info

song = fetch_song_info('./songs/songlist', 'panicbounceattack')

render = Render(
    aff_path='./songs/panicbounceattack/2.aff',
    cover_path='./songs/panicbounceattacki/base.jpg',
    song=Song(**song),
    difficulty=2,
    constant=7.0,
)

render.show()
render.save('panicbounceattack_2.png')
```

## Example

![eample](./assets/panicbounceattack_2.png)

 - The yellow area means that the BPM in that area is not equal to the `bpm_base` of the song.

## Side Usage

In addition to rendering charts, you can use the library to do the following things.

### chart syntax check

A minimal syntax check for individual commands in a chart.

```python
from ArcaeaChartRender.aff_decoder import parse_aff
from ArcaeaChartRender.utils import read_file

chart = parse_aff(read_file('./songs/panicbounceattacki/2.aff'))
for cmd in chart.command_list:
    print(cmd.syntax_check(), cmd)
```

### chart statistics

Statistical information such as combo calculation.

See [`element.py`](./element.py) for more information.

```python
from ArcaeaChartRender.aff_decoder import parse_aff
from ArcaeaChartRender.element import Tap
from ArcaeaChartRender.utils import read_file

chart = parse_aff(read_file('./songs/panicbounceattacki/2.aff'))
print(chart.get_total_combo())
print(chart.get_combo_of(Tap))
print(chart.get_bpm_proportion())
print(chart.get_interval())
...
```

### aff plain text parsing

Easily convert plain text of aff file to `dict` or `list`.

See [`aff_parsing.py`](./aff_parsing.py) for more information.

```python
from ArcaeaChartRender.aff_parsing import command
from ArcaeaChartRender.utils import read_file

content = read_file('./songs/panicbounceattacki/2.aff')
print(command.parse_string(content).as_dict())
print(command.parse_string(content).as_list())
...
```

## TODO

 - [ ] beautify text style (at text area)
 - [ ] add support for segmented combo count (per bar)
 - [ ] add support for custom background (when `Song.bg` field is not `None`)
 - [ ] other chart statistics (density, multi-finger, crossed hand, etc.)

## License

 - `BOFXVI - PANIC! BOUNCE! ATTACK!!!` from [Arcaea-Infinity/FanmadeCharts](https://github.com/Arcaea-Infinity/FanmadeCharts) under `616 SB License`
 - `Aff2Preview` from [Arcaea-Infinity/Aff2Preview](https://github.com/Arcaea-Infinity/Aff2Preview) under `616 SB License`
 - `pyparsing` from [pyparsing/pyparsing](https://github.com/pyparsing/pyparsing) under `MIT License`
 - `opencv2` from [opencv/opencv-python](https://github.com/opencv/opencv-python) under `MIT License`
 - `Pillow` from [python-pillow/Pillow](https://github.com/python-pillow/Pillow) under `HPND License`

This project is licensed under the terms of the [`616 SB License`](./LICENSE).
