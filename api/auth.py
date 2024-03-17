import os
import requests

from fastapi import FastAPI, Depends, HTTPException, status
from .utils import decode_jwt, get_public_key, comfyui_path
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from .models import User

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
