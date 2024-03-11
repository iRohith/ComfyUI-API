import os
from typing import Union
import requests
from .models import Txt2ImgParams
import jwt
from jwt.algorithms import RSAAlgorithm
import json
import math

comfyui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def upload_image(
    img: Union[bytes, str], account_id: str, api_key: str, name: str = "image"
):
    try:
        # Check if img is a URL or a file
        if isinstance(img, str):
            url = img
            file_data = None
        else:
            url = None
            file_data = img

        # Prepare FormData
        form_data = {"requireSignedURLs": "false"}

        if url:
            form_data["url"] = url
        else:
            form_data["file"] = (name, file_data)

        # Make the request to Cloudflare API
        response = requests.post(
            f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1",
            headers={"Authorization": f"Bearer {api_key}"},
            files=form_data,
        )

        # Process the response
        data = response.json()

        if response.ok and data["success"] and len(data["result"]["variants"]) > 0:
            return {"success": True, "data": data["result"]["variants"][0]}
        else:
            return {"success": False, "error": "Image upload failed {data}"}
    except Exception as err:
        return {"success": False, "error": f"Image upload failed: {err}"}


def calculate_tokens(p):
    if isinstance(p, Txt2ImgParams):
        tokens = (
            p.batch
            * math.ceil(p.width / 512)
            * math.ceil(p.height / 512)
            * math.ceil(p.steps / 25)
        )
        size = os.path.getsize(
            os.path.join(comfyui_path, "models", "checkpoints", p.checkpoint)
        )
        is_sdxl = size > 3 * 1024 * 1024
        is_sc = size > 7 * 1024 * 1024

        if is_sc:
            tokens *= 4
        elif is_sdxl:
            tokens *= 2

        return math.ceil(tokens)


def get_public_key():
    response = requests.get(os.environ["CLERK_JWKS_URL"])
    response.raise_for_status()
    jwks = response.json()

    for key in jwks["keys"]:
        if key["kid"] == os.environ["CLERK_KID"]:
            return RSAAlgorithm.from_jwk(json.dumps(key))
    raise ValueError("Key not found in JWKS")


def decode_jwt(token, public_key):
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Signature has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
