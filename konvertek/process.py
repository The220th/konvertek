# coding: utf-8

import os
import argparse
from ksupk import get_files_list
from konvertek.progress_handler import ProgressHandler
from konvertek.ffmpeg_handler import get_video_ext, transcode_video, do_ffmpeg_vf_flag


def video_processing(args: argparse.Namespace):
    ph = ProgressHandler(args.progress_file_path)
    video_ext = get_video_ext()
    d = ph.create_files_4_progress(args.folder_path_in, args.folder_path_out)
    for k_i in d:
        file_i = k_i
        if str(os.path.splitext(file_i)[1]).lower() not in video_ext:
            d.pop(file_i, None)
    ph.add_files(d)
    for k_i in d:
        file_i = k_i
        vf = do_ffmpeg_vf_flag(args.resolution, args.fps, args.interpolation)
        if not ph.file_status(file_i):
            file_i_in, file_i_out = ph.get_file_in_out(file_i)
            tvr = transcode_video(file_i_in, file_i_out,
                                  v_codec=args.v_codec, vf=vf,
                                  bitrate=args.bitrate,
                                  maxbitrate=args.maxbitrate,
                                  overwrite=args.not_replace)
            if tvr is None:
                ph.update(file_i, True, None)
            else:
                ph.update(file_i, False, tvr)
                if args.stop_if_error:
                    print(f"Error occurred: \n{tvr}")
                    exit(-1)


def list_extensions_processing(args: argparse.Namespace):
    files = get_files_list(args.folder_path)
    res = set()
    for file_i in files:
        # file_i_name = os.path.basename(file_i)
        # n, e = os.path.splitext(file_i_name)
        # n, e = str(n), str(e).lower()
        # res.add(e)
        res.add(str(os.path.splitext(file_i)[1]).lower())

    print(f"All file extensions encountered: {res}")