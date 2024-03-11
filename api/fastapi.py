from .models import User, Txt2ImgParams, Img2ImgParams
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from .utils import decode_jwt, get_public_key, comfyui_path
from .testmodel import check as check_model
from .txt2img import txt2img
from .img2img import img2img

import requests
import os
import subprocess
import json

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_token_header(token: str = Depends(oauth2_scheme)):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user_id = decode_jwt(token, get_public_key())["sub"]
    clerk_secret_key = os.environ["CLERK_SECRET_KEY"]
    response = requests.get(
        f"https://api.clerk.com/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {clerk_secret_key}"},
    )
    response.raise_for_status()
    user_data = response.json()
    return User(**user_data)


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
