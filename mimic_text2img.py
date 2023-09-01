import base64
import json
import random
from datetime import datetime

import requests


def create_stable_diffusion_images(options=None):
    if options is None:
        raise ValueError("options is required")

    webui_host_url = "http://your-webui-host-url"  # Replace with your URL
    webui_options = fetch_options(webui_host_url)

    model = options.get("input", {}).get("model", "")
    sampler = options.get("input", {}).get("sampler", "")
    initial_image = options.get("input", {}).get("initialImage", "")

    options["count"] = options.get("count", get_stable_diffusion_default_count())

    is_upscale = options.get("input", {}).get("initialImage", {}).get("weight", 0) == 1 and model == "esrgan-v1-x2plus"

    if model and model != webui_options["sd_model_checkpoint"] and not is_upscale:
        model_response = set_options(webui_host_url, {"sd_model_checkpoint": model})
        if model_response.ok:
            print("applied model")

    data = construct_payload(
        options, is_upscale, settings["upscaler"].value
    )  # The 'settings' and 'construct_payload' should be defined elsewhere in your code

    endpoint = "/sdapi/v1/txt2img"
    if initial_image:
        endpoint = "/sdapi/v1/extra-single-image" if is_upscale else "/sdapi/v1/img2img"

    response = requests.post(
        f"{webui_host_url}{endpoint}", headers={"Content-Type": "application/json"}, data=json.dumps(data)
    )
    response_data = response.json()

    images = []
    created_at = datetime.now()

    if is_upscale:
        # Upscaling only returns one image
        blob = base64.b64decode(response_data["image"])

        image = {
            "id": str(random.random() * 10000000),
            "createdAt": created_at,
            "blob": blob,
            "input": {"model": model},
        }
        images.append(image)
    else:
        # Image generation returns an array of images
        start_index = 1 if len(response_data["images"]) > data["batch_size"] else 0
        for i in range(start_index, len(response_data["images"])):
            blob = base64.b64decode(response_data["images"][i])
            image = {
                "id": str(random.random() * 10000000),
                "createdAt": created_at,
                "blob": blob,
                "input": {
                    "prompts": options.get("input", {}).get("prompts", []),
                    "steps": options.get("input", {}).get("steps", 0),
                    "seed": response_data["images"][i]["seed"],
                    "model": model,
                    "width": options.get("input", {}).get("width", 512),
                    "height": options.get("input", {}).get("height", 512),
                    "cfgScale": options.get("input", {}).get("cfgScale", 7),
                    "sampler": sampler,
                },
            }
            images.append(image)

    return {
        "id": str(random.random() * 10000000),
        "images": images,
    }
