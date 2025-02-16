import base64
import io
import json

import requests
from PIL import Image, PngImagePlugin

url = "http://10.62.161.193:7865"  # "http://10.62.161.193:7865"

payload = {"prompt": "puppy dog", "steps": 5}

response = requests.post(url=f"{url}/sdapi/v1/txt2img", json=payload)

r = response.json()

for i in r["images"]:
    image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

    png_payload = {"image": "data:image/png;base64," + i}
    response2 = requests.post(url=f"{url}/sdapi/v1/png-info", json=png_payload)

    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("parameters", response2.json().get("info"))
    image.save("output.png", pnginfo=pnginfo)
