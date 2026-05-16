import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline

# Load text-to-image pipeline
text2img_pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
text2img_pipe = text2img_pipe.to("cpu")

# Load img2img pipeline
img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
img2img_pipe = img2img_pipe.to("cpu")

def generate(
    prompt,
    negative="",
    guidance=7.5,
    steps=18,
    aspect="3:2",
    seed=None,
    lora=None,
    speed_mode=True,
    upscale_mode="auto",
    upscale_factor=2,
):
    width, height = _aspect_to_resolution(aspect)
    generator = torch.Generator(device="cpu")
    if seed is not None:
        generator = generator.manual_seed(seed)

    image = text2img_pipe(
        prompt=prompt,
        negative_prompt=negative,
        guidance_scale=guidance,
        num_inference_steps=steps,
        width=width,
        height=height,
        generator=generator,
    ).images[0]

    return image

def generate_img2img(
    prompt,
    init_image,
    negative="",
    guidance=7.5,
    steps=18,
    strength=0.35,
    seed=None,
    lora=None,
    speed_mode=True,
    upscale_mode="auto",
    upscale_factor=2,
):
    generator = torch.Generator(device="cpu")
    if seed is not None:
        generator = generator.manual_seed(seed)

    image = img2img_pipe(
        prompt=prompt,
        image=init_image,
        negative_prompt=negative,
        guidance_scale=guidance,
        num_inference_steps=steps,
        strength=strength,
        generator=generator,
    ).images[0]

    return image

def _aspect_to_resolution(aspect):
    # Simple aspect ratio to resolution mapping
    table = {
        "1:1": (512, 512),
        "3:2": (576, 384),
        "2:3": (384, 576),
        "4:3": (640, 480),
        "16:9": (768, 432),
    }
    return table.get(aspect, (576, 384))