# coding: utf-8

import ffmpeg
import os


def transcode_video(input_file, output_file,
                    v_codec: str = None, vf: str = None,
                    bitrate: str = None, maxbitrate: str = None,
                    overwrite: bool = True, print_command: bool = False) -> str | None:
    if not overwrite and os.path.isfile(output_file):
        return None
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

    if print_command:
        try:
            process = (
                ffmpeg.input(input_file).output(
                    output_file, **out_params
                ).global_args(*[])
            )
            command = process.compile()
            print(' '.join(command))
        except ffmpeg.Error as e:
            print("Cannot print ffmpeg-command. ")

    try:
        ffmpeg.input(input_file).output(
            output_file, **out_params
        ).global_args(*[]).run(overwrite_output=overwrite, capture_stderr=True, capture_stdout=True)

    except ffmpeg.Error as e:
        return e.stderr.decode("utf8")
        # return e.stdout.decode("utf8")

    return None


def remove_p_from_resolution(s: str) -> int:
    return int(s[:len(s) - 1])


def do_ffmpeg_vf_flag(resolution: str | None, fps: int | None, interpolation: str | None) -> str | None:
    s = ""
    res_to_width = {720: 1280, 1080: 1920, 1440: 2560, 2160: 3840, 4320: 7680, 8640: 15360}
    # "vf": "scale='if(gt(iw,ih),1280,-2):if(gt(iw,ih),-2,720)'",
    # "vf": "scale=-2:'if(gt(ih,720),720,ih)'"
    # "scale=-2:'if(gt(ih,720),720,ih)',fps=60:flags=blend"
    # -vf "minterpolate='fps=60:mi_mode=mci:me=bilat'"
    # scale=-2:'if(gt(ih,720),720,ih)',minterpolate=fps=300:mi_mode=accurate
    if resolution is not None:
        res_int = remove_p_from_resolution(resolution)
        if res_int in res_to_width:
            needed_w = res_to_width[res_int]
            s += f"scale='if(gt(iw,{needed_w}),{needed_w},iw)':-2"
        else:
            s += f"scale=-2:'if(gt(ih,{res_int}),{res_int},ih)'"
    if fps is not None:
        if s != "":
            s += ","
        if interpolation is not None:
            s += f"minterpolate=fps={fps}:mi_mode='{interpolation}'"
        else:
            s += f"fps={fps}"
    return s if s != "" else None


def get_video_ext() -> set:
    res = {".mp4", ".m4v", ".mkv", ".mk3d", ".mka", ".webm", ".avi", ".mov", ".wmv", ".wma", ".asf", ".ts", ".m2ts",
           ".flv",
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


def get_video_bitrate(file_path: str) -> int or None:
    try:
        probe = ffmpeg.probe(file_path)

        # first video stream
        video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']

        if not video_streams:
            return None

        video_stream = video_streams[0]

        bitrate = video_stream.get('bit_rate', None)

        if bitrate:
            return int(bitrate)  # bit/sec
        else:
            return None
    except ffmpeg.Error as e:
        return None


def parse_bitrate(bitrate_str: str) -> int:
    """
    Преобразует строку битрейта (например, '2M', '500K') в целое число (бит/сек).
    """

    suffix_multipliers = {
        'K': 10 ** 3,
        'M': 10 ** 6,
        'G': 10 ** 9
    }

    if bitrate_str[-1] in suffix_multipliers:
        number_part = bitrate_str[:-1]
        suffix = bitrate_str[-1].upper()

        try:
            return int(float(number_part) * suffix_multipliers[suffix])
        except ValueError:
            raise ValueError(f"Incorrect bitrate format: \"{bitrate_str}\"")
    else:
        try:
            return int(bitrate_str)
        except ValueError:
            raise ValueError(f"Incorrect bitrate format: \"{bitrate_str}\"")
