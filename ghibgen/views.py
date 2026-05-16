# ghibgen/views.py
from django.conf import settings
from django.shortcuts import render
from PIL import Image
import logging, random

from .forms import GenerateForm
from .pipeline_sd import generate, generate_img2img
from .utils import ensure_media, unique_png

logger = logging.getLogger(__name__)

def _apply_text2img_preset(preset: str, guidance, steps):
    if guidance is None and steps is None:
        if preset == "speed": return 7.0, 14
        if preset == "quality": return 8.0, 24
        return 7.5, 18
    if guidance is None:
        guidance = {"speed": 7.0, "quality": 8.0}.get(preset, 7.5)
    if steps is None:
        steps = {"speed": 14, "quality": 24}.get(preset, 18)
    return guidance, steps

def _apply_img2img_preset(preset: str, guidance, steps, strength):
    table = {
        "faithful": (6.0, 14, 0.25),
        "balanced": (6.5, 16, 0.35),
        "stylized": (7.0, 18, 0.55),
        "speed":    (6.3, 12, 0.30),
        "quality":  (7.2, 20, 0.40),
    }
    g_def, s_def, str_def = table.get(preset, table["balanced"])
    return (g_def if guidance is None else guidance,
            s_def if steps    is None else steps,
            str_def if strength is None else strength)

def index(request):
    form = GenerateForm(request.POST or None, request.FILES or None)
    img_url, error, used = None, None, {}

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        try:
            ensure_media()

            preset   = data.get("preset") or "balanced"
            prompt   = data["prompt"]
            negative = data.get("negative_prompt") or ""
            aspect   = data.get("aspect") or "3:2"
            lora     = data.get("lora") or None
            upscale_mode   = data.get("upscale_mode") or "auto"
            upscale_factor = int(data.get("upscale_factor") or "2")

            guidance = data.get("guidance_scale")
            steps    = data.get("num_inference_steps")

            seed = data.get("seed")
            if seed is None:
                seed = random.randrange(0, 2**31 - 1)

            init = data.get("init_image")
            if init:
                strength = data.get("strength")
                guidance, steps, strength = _apply_img2img_preset(preset, guidance, steps, strength)
                with Image.open(init) as im:
                    pil_init = im.convert("RGB")
                pil_img = generate_img2img(
                    prompt=prompt,
                    init_image=pil_init,
                    negative=negative,
                    guidance=guidance,
                    steps=steps,
                    strength=float(strength),
                    seed=seed,
                    lora=lora,
                    speed_mode=True,
                    upscale_mode=upscale_mode,
                    upscale_factor=upscale_factor,
                )
            else:
                guidance, steps = _apply_text2img_preset(preset, guidance, steps)
                pil_img = generate(
                    prompt=prompt,
                    negative=negative,
                    guidance=guidance,
                    steps=steps,
                    aspect=aspect,
                    seed=seed,
                    lora=lora,
                    speed_mode=True,
                    upscale_mode=upscale_mode,
                    upscale_factor=upscale_factor,
                )

            fname = unique_png()
            out_path = settings.MEDIA_ROOT / fname
            pil_img.save(out_path)
            img_url = settings.MEDIA_URL + fname

            used = {
                "preset": preset, "guidance": guidance, "steps": steps,
                "aspect": aspect, "seed": seed, "upscale_mode": upscale_mode, "upscale_factor": upscale_factor,
                "lora": lora or "—",
                "mode": "img2img" if init else "text2img",
            }

        except Exception as e:  # noqa: BLE001 (broad-except acceptable at boundary)
            logger.exception("Generation failed")
            error = f"Generation failed: {e}"

    return render(request, "index.html", {"form": form, "img_url": img_url, "error": error, "used": used})
