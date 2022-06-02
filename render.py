from utils import read_file
from aff_decoder import parse_aff
from time import time
import PIL


base_bpm: float = 153.0

chart = parse_aff(read_file(aff_path))
