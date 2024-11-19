# coding: utf-8

import ffmpeg
import subprocess


def transcode_video(input_file, output_file,
                    v_codec: str = None, vf: str = None,
                    bitrate: str = None, maxbitrate: str = None,
                    overwrite: bool = True) -> str | None:
    out_params = {
        "map": 0,
        "c:a": "copy",
        "c:s": "copy",
        }
    if v_codec is not None:
        out_params["c:v"] = v_codec
    if vf is not None:
        out_params["vf"] = vf
    if bitrate is not None:
        out_params["b:v"] = bitrate
    if maxbitrate is not None:
        out_params["maxrate"] = maxbitrate

    stdoe = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

    try:
        ffmpeg.input(input_file).output(
            output_file,
            **out_params
        ).run(overwrite_output=overwrite, **stdoe)
    except ffmpeg.Error as e:
        return e.stderr.decode()

    return None


def remove_p_from_resolution(s: str) -> int:
    return int(s[:len(s)-1])


def do_ffmpeg_vf_flag(resolution: str | None, fps: int | None, interpolation: str | None) -> str | None:
    s = ""
    # "vf": "scale='if(gt(iw,ih),1280,-2):if(gt(iw,ih),-2,720)'",
    # "vf": "scale=-2:'if(gt(ih,720),720,ih)'"
    # "scale=-2:'if(gt(ih,720),720,ih)',fps=60:flags=blend"
    # -vf "minterpolate='fps=60:mi_mode=mci:me=bilat'"
    res_int = remove_p_from_resolution(resolution)
    if resolution is not None:
        s += f"scale=-2:'if(gt(ih,{res_int}),{res_int},ih)'"
    if fps is not None:
        if s != "":
            s += ","
        s += f"fps={fps}"
    if interpolation is not None:
        s += f":flags={interpolation}"
    return s if s != "" else None


def get_video_ext() -> set:
    res = {".mp4", ".m4v", ".mkv", ".mk3d", ".mka", ".webm", ".avi", ".mov", ".wmv", ".wma", ".asf", ".ts", ".m2ts", ".flv",
     ".3gp", ".3g2", ".rm", ".rmvb", ".divx", ".mxf", ".gxf", ".nut", ".psp"}

    return res


def get_audio_ext() -> set:
    res = {".mp3", ".wav", ".aac", ".flac", ".ogg", ".oga", ".amr"}
    return res


def get_image_ext() -> set:
    res = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp", ".svg", ".heif", ".hei", ".ico",
           ".ppm", ".pgm", ".pbm", ".pnm",
           ".pcx", ".dds", ".tga", ".icb", ".vda", ".vst", ".exr", ".jp2", ".j2k", ".pgf", ".xbm"}
    return res
