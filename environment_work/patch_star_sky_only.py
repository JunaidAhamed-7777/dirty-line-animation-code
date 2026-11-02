import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from star_sky_v2 import apply_star_sky
apply_star_sky(camera_strength=.45)
