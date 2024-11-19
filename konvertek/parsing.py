# coding: utf-8

import argparse
import os
from konvertek.__init__ import __version__


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="konvertek. Convert media from folder.")

    parser.add_argument("--version", action="version", version=f"{__version__}", help="Check version. ")

    subparsers = parser.add_subparsers(dest='command', required=True)

    # convert
    main_parser = subparsers.add_parser('convert', help='Generate config file')
    main_parser.add_argument('folder_path_in', type=is_dir_path,
                             help="Path to source directory. konvertek will not change inside anything. "
                                  "It may be read only. ")
    main_parser.add_argument('folder_path_out', type=is_dir_path,
                             help="Path to destination folder. "
                                  "Each media file will be converted according to the instructions. "
                                  "The file hierarchy will be preserved exactly as in the original directory. ")
    main_parser.add_argument('progress_file_path',
                             # type=argparse.FileType("w+", encoding="utf-8"),
                             type=str,
                             help='Path to file with progress. It is json. ')
    parser.add_argument("--v_codec", type=str,  # avc=H.264, hevc=H.265
                        choices=["libx264", "h264_nvenc", "h264_amf", "h264_vaapi",
                                 "libx265", "hevc_amf", "hevc_nvenc", "h265_vaapi",
                                 "libvpx-vp9", "vp9_qsv",
                                 "libaom-av1", "av1_vaapi",
                                 "libxvid", "rawvideo"],
                        default=None, required=False,
                        help="Chosen video codec for encoding video for destination folder {folder_path_out}. ")
    parser.add_argument("--resolution", type=str,
                        choices=["140p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p", "8640p"],
                        default=None, required=False,
                        help="Chosen video resolution for destination folder {folder_path_out}. ")
    parser.add_argument("--fps", type=int,
                        default=None, required=False,
                        help="Chosen video FPS for destination folder {folder_path_out}. ")
    parser.add_argument("--interpolation", type=str,
                        choices=["accurate", "drop", "blend", "dup"],
                        default=None, required=False,
                        help="Apply interpolation if you need to add new frames when increasing/decreasing FPS "
                             "for destination folder {folder_path_out}. "
                             "It is recommended to play with the parameter and see the results before using it.")
    parser.add_argument("--bitrate", type=str,
                        default=None, required=False,
                        help="Chosen video bitrate for destination folder {folder_path_out}. For example: 2M, 512K... ")
    parser.add_argument("--maxbitrate", default=False, action='store_true',
                        help="If set, the bitrate cannot exceed the value specified in flag \"--bitrate\". ")

    parser.add_argument("--not_replace", default=True, action='store_false',
                        help="If set, No need to replace the video if it already exists in the destination folder. ")
    parser.add_argument("--stop_if_error", default=False, action='store_true',
                        help="If set and error occurred while ffmpeg is running, konvertek will exit. ")

    # list_extensions
    list_extensions_parser = subparsers.add_parser('list_extensions', help='Print all file extensions')
    list_extensions_parser.add_argument('folder_path', type=is_dir_path, help='Path to folder. ')

    args = parser.parse_args()
    if args.command == "convert":
        if args.interpolation and not args.fps:
            parser.error("Flag --interpolation cannot be define without --fps. ")
            exit()

        if args.maxbitrate and not args.bitrate:
            parser.error("Flag --maxbitrate cannot be define without --bitrate. ")
            exit()

    return args


def is_dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)
