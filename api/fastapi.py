from .models import User, Txt2ImgParams, Img2ImgParams
from fastapi import FastAPI, Depends
from fastapi.responses import Response
from .utils import comfyui_path
from .auth import get_token_header
from .testmodel import check as check_model
from .txt2img import txt2img
from .img2img import img2img

import requests
import os
import subprocess
import json


web_app = FastAPI()
web_app.commit_cb = None


@web_app.post("/txt2img")
async def _txt2img(params: Txt2ImgParams, user: User = Depends(get_token_header)):
    return Response(
        json.dumps(
            txt2img(
                p=params,
                user=user,
                account_id=os.environ["CLOUDFLARE_IMAGES_ACCOUNT_ID"],
                api_key=os.environ["CLOUDFLARE_IMAGES_API_KEY"],
            )
        )
    )


@web_app.post("/img2img")
async def _img2img(params: Img2ImgParams, user: User = Depends(get_token_header)):
    return Response(
        json.dumps(
            img2img(
                p=params,
                user=user,
                account_id=os.environ["CLOUDFLARE_IMAGES_ACCOUNT_ID"],
                api_key=os.environ["CLOUDFLARE_IMAGES_API_KEY"],
            )
        )
    )


@web_app.post("/upload_model")
async def _upload_model(params: dict, user: User = Depends(get_token_header)):
    url = params["url"]
    folder = params["folder"]
    filename = params["filename"]
    path = f"{comfyui_path}/models/{folder}/{filename}"

    subprocess.call(
        f'aria2c -x16 --split=16 -d / -o "{path}" "{url}"',
        shell=True,
    )
    try:
        if check_model(filename, folder):
            if web_app.commit_cb is not None:
                web_app.commit_cb()
            return {"success": True}
        else:
            raise Exception()
    except Exception as e:
        print("Error", e)
        subprocess.call(["rm", "-f", path])
        return {"success": False}


@web_app.post("/delete_model")
async def _delete_model(params: dict, user: User = Depends(get_token_header)):
    folder = params["folder"]
    filename = params["filename"]
    path = f"{comfyui_path}/models/{folder}/{filename}"

    subprocess.call(
        f'rm -f "{path}"',
        shell=True,
    )
    try:
        if not check_model(filename, folder):
            if web_app.commit_cb is not None:
                web_app.commit_cb()
            return {"success": True}
        else:
            return {"success": False}
    except:
        return {"success": False}
