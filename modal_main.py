from modal import (
    Image,
    Stub,
    asgi_app,
    web_endpoint,
    gpu,
    Secret,
    Volume,
)

import env_vars
from api.fastapi import (
    txt2img,
    img2img,
    Txt2ImgParams,
    Img2ImgParams,
    User,
    get_token_header,
)

stub = Stub("comfyui")
models_volume = Volume.from_name("models", create_if_missing=True)

comfy_image = (
    Image.from_registry("irohith/comfyui:09.03.24")
    .dockerfile_commands(["RUN rm -rf /root/models/*"])
    .env({})
)

with comfy_image.imports():
    import os
    import json
    from fastapi import Depends, Response
    from api.fastapi import web_app, get_token_header, txt2img
    from api.models import Txt2ImgParams, User


@stub.cls(
    gpu=gpu.T4(count=1),
    allow_concurrent_inputs=8,
    concurrency_limit=5,
    image=comfy_image,
    container_idle_timeout=60,
    volumes={"/root/models": models_volume},
    secrets=[
        Secret.from_name("clerk"),
        Secret.from_name("cloudflare-r2"),
        Secret.from_name("db"),
    ],
)
class Model:
    from api.fastapi import (
        txt2img,
        img2img,
        Txt2ImgParams,
        Img2ImgParams,
        User,
        get_token_header,
    )

    @web_endpoint(method="POST")
    def _txt2img(self, params: Txt2ImgParams, user: User = Depends(get_token_header)):
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


@stub.function(
    cpu=1,
    memory=1024,
    allow_concurrent_inputs=1,
    concurrency_limit=500,
    image=comfy_image,
    container_idle_timeout=60,
    volumes={"/root/models": models_volume},
    secrets=[
        Secret.from_name("clerk"),
        Secret.from_name("cloudflare-r2"),
        Secret.from_name("db"),
    ],
)
@asgi_app()
def dl_app():
    from api.fastapi import web_app

    web_app.commit_cb = models_volume.commit
    return web_app
