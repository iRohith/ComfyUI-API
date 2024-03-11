import os
from .utils import comfyui_path
from comfy import cli_args
import comfy.cmd.cuda_malloc
import random
import torch

cli_args.options.enable_args_parsing()
cli_args.args.cpu = not torch.cuda.is_available()
cli_args.args.cwd = comfyui_path

from comfy.nodes import (
    CheckpointLoaderSimple,
    EmptyLatentImage,
    CLIPTextEncode,
    KSampler,
    VAEDecode,
    SaveImage,
    LoraLoader,
    VAELoader,
)

from .models import Txt2ImgParams, User
from .sql import *
from .utils import *


def txt2img(p: Txt2ImgParams, account_id: str, api_key: str, user: User):
    with torch.inference_mode():
        checkpointloadersimple = CheckpointLoaderSimple()
        vaeloader = VAELoader()
        emptylatentimage = EmptyLatentImage()
        cliptextencode = CLIPTextEncode()
        ksamplersimple = KSampler()
        vaedecode = VAEDecode()
        saveimage = SaveImage()

        basemodel = checkpointloadersimple.load_checkpoint(ckpt_name=p.checkpoint)
        vae = vaeloader.load_vae(p.vae) if p.vae is not None else basemodel[2]

        model = basemodel

        for lora in p.loras:
            model = LoraLoader().load_lora(
                basemodel[0], basemodel[1], lora[0], lora[1], 1
            )

        emptylatentimage = emptylatentimage.generate(
            width=p.width, height=p.height, batch_size=p.batch
        )
        cliptextencode_pos = cliptextencode.encode(text=p.pos, clip=model[1])
        cliptextencode_neg = cliptextencode.encode(text=p.neg, clip=model[1])
        seed = random.randint(1, 2**64) if p.seed == -1 else p.seed

        ksamplersimple_out = ksamplersimple.sample(
            model=model[0],
            seed=seed,
            steps=p.steps,
            cfg=p.cfg,
            sampler_name=p.sampler,
            scheduler=p.scheduler,
            positive=cliptextencode_pos[0],
            negative=cliptextencode_neg[0],
            latent_image=emptylatentimage[0],
            denoise=1,
        )

        vaedecode_Out = vaedecode.decode(samples=ksamplersimple_out[0], vae=vae)

        saveimage_out = saveimage.save_images(
            filename_prefix="ComfyUI", images=vaedecode_Out[0]
        )

        res = []
        for img in map(
            lambda x: os.path.join(
                comfyui_path,
                "output",
                x["subfolder"],
                x["filename"],
            ),
            saveimage_out["ui"]["images"],
        ):
            ur = upload_image(
                open(img, "rb").read(), account_id, api_key, f"{user.username}_t2i"
            )
            if ur["success"]:
                res.append(ur["data"])
            else:
                return ur

        user = session.query(Users).filter(Users.username == user.username).first()
        user.tokens = user.tokens - calculate_tokens(p)
        session.commit()

        return res
