# ghibgen/utils.py
import time, random
from pathlib import Path
from django.conf import settings

def ensure_media():
    Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)

def unique_png(prefix="ghibli"):
    ts = int(time.time() * 1000)
    return f"{prefix}_{ts}_{random.randint(1000,9999)}.png"
