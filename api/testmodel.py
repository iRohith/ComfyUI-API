from .utils import comfyui_path
from comfy import cli_args
from comfy.cmd import cuda_malloc
import torch

cli_args.options.enable_args_parsing()
cli_args.args.cpu = not torch.cuda.is_available()
cli_args.args.cwd = comfyui_path

from comfy.nodes import *


def check(filename: str, folder: str):
    with torch.inference_mode():
        if folder == "checkpoints":
            try:
                cl = CheckpointLoaderSimple()
                m = cl.load_checkpoint(filename)
                del cl, m
                return True
            except:
                return False
        elif folder == "vae":
            try:
                vl = VAELoader()
                m = vl.load_vae(filename)
                del vl, m
                return True
            except:
                return False
        elif folder == "loras":
            try:
                cl = CheckpointLoaderSimple()
                model = cl.load_checkpoint("dreamshaper_8.safetensors")
                ll = LoraLoader()
                m = ll.load_lora(model[0], model[1], filename, 1, 1)
                del model, ll, m, cl
                return True
            except:
                return False
        elif folder == "embeddings":
            size = os.path.getsize(f"{comfyui_path}/models/{folder}/{filename}")
            return size < 1 * 1024 * 1024

        return False
