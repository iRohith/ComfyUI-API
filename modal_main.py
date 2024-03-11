from modal import (
    Image,
    Stub,
    asgi_app,
    gpu,
    Secret,
    Volume,
)

stub = Stub("comfyui")
models_volume = Volume.from_name("models", create_if_missing=True)

comfy_image = (
    Image.from_registry("irohith/comfyui:09.03.24")
    .dockerfile_commands(["RUN rm -rf /root/models/*"])
    .env({})
)

with comfy_image.imports():
    from api.fastapi import web_app


@stub.function(
    gpu=gpu.A10G(count=1),
    allow_concurrent_inputs=10,
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
@asgi_app()
def img_app():
    from api.fastapi import web_app

    return web_app


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
