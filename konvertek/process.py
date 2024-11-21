# coding: utf-8

import os
import argparse
import shutil
from tqdm import tqdm
from ksupk import get_files_list, get_dirs_needed_for_files, mkdir_with_p
from konvertek.progress_handler import ProgressHandler
from konvertek.ffmpeg_handler import get_video_ext, get_audio_ext, get_image_ext, transcode_video, do_ffmpeg_vf_flag
from konvertek.ffmpeg_handler import get_video_bitrate, parse_bitrate


def video_processing(args: argparse.Namespace):
    ph = ProgressHandler(args.progress_file_path)
    video_ext = get_video_ext()
    d = ph.create_files_4_progress(args.folder_path_in, args.folder_path_out)

    needed_dirs = get_dirs_needed_for_files([os.path.join(str(args.folder_path_out), file_i) for file_i in d.keys()])
    for dir_i in needed_dirs:
        mkdir_with_p(dir_i)

    d_with_media = {}
    for k_i in d:
        file_i = k_i
        if str(os.path.splitext(file_i)[1]).lower() in video_ext:
            d_with_media[file_i] = d[file_i]

    ph.add_files(d)

    ok_files, shitty_files = [], []
    pbar = tqdm(d)
    for k_i in pbar:
        file_i = k_i
        pbar.set_postfix({"current file": f"{file_i}"})
        if not ph.file_status(file_i):
            if file_i in d_with_media:
                vf = do_ffmpeg_vf_flag(args.resolution, args.fps, args.interpolation)
                file_i_in, file_i_out = ph.get_file_in_out(file_i)

                bitrate_i = args.bitrate
                if args.bitrate is not None and not args.force_bitrate:
                    cur_bitrate = get_video_bitrate(file_i_in)
                    target_bitrate = parse_bitrate(bitrate_i)
                    # print(f"1. {cur_bitrate}_cur vs {target_bitrate}_target")
                    if cur_bitrate is not None and target_bitrate > cur_bitrate:
                        bitrate_i = str(cur_bitrate)

                tvr = transcode_video(file_i_in, file_i_out,
                                      v_codec=args.v_codec, vf=vf,
                                      bitrate=bitrate_i,
                                      maxbitrate=args.bitrate if args.maxbitrate else None,
                                      overwrite=args.replace,
                                      print_command=args.print_command,)
                if tvr is None:
                    ph.update(file_i, True, None)
                    ok_files.append(file_i)
                    # print(f"2. {get_video_bitrate(file_i_out)}")
                else:
                    ph.update(file_i, False, tvr)
                    shitty_files.append(file_i)
                    if args.stop_if_error:
                        print(f"Error occurred: \n{tvr}")
                        exit(-1)
            else:
                shutil.copy(*ph.get_file_in_out(file_i))
                ph.update(file_i, True, None)
                ok_files.append(file_i)

    print(f"Total files: {len(ok_files)+len(shitty_files)}, processed: {len(ok_files)}, failed: {len(shitty_files)}")
    if len(shitty_files) > 0:
        print(f"This files were not processed (transcode): ")
        for file_i in shitty_files:
            print(f"- \"{file_i}\"")
        print(f"\n For more details type command: \n> konvertek problem_info {args.progress_file_path}")


def problem_info_processing(args: argparse.Namespace):
    if not os.path.isfile(args.progress_file_path):
        print(f"No such file: {args.progress_file_path}")
    ph = ProgressHandler(args.progress_file_path)
    files, errors = ph.get_files(), ph.get_errors()
    no_processed = []
    for file_i in files:
        if not ph.file_status(file_i):
            no_processed.append(file_i)
    if len(no_processed) > 0:
        print(f"These files were not processed/transcoded: ")
        for file_i in no_processed:
            print(f"- \"{file_i}\"")
    if len(errors.keys()) > 0:
        for k_i in errors:
            print(f"\n{'='*80}\nFile \"{k_i}\": \n{errors[k_i]}{'='*80}")
    else:
        print("No problems output from ffmpeg. ")


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
    buff1, buff_ext1 = [], get_video_ext()
    for ext_i in res:
        if ext_i in buff_ext1:
            buff1.append(ext_i)
    if len(buff1) > 0:
        print(f"Video formats: {set(buff1)}")
    buff2, buff_ext2 = [], get_audio_ext()
    for ext_i in res:
        if ext_i in buff_ext2:
            buff2.append(ext_i)
    if len(buff2) > 0:
        print(f"Audio formats: {set(buff2)}")
    buff3, buff_ext3 = [], get_image_ext()
    for ext_i in res:
        if ext_i in buff_ext3:
            buff3.append(ext_i)
    if len(buff3) > 0:
        print(f"Image formats: {set(buff3)}")
    buff = []
    for ext_i in res:
        if ext_i in buff_ext1 or ext_i in buff_ext2 or ext_i in buff_ext3:
            pass
        else:
            buff.append(ext_i)
    if len(buff) > 0 and len(buff1)+len(buff2)+len(buff3) > 0:
        print(f"Other formats: {set(buff)}")
