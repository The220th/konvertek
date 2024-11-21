# coding: utf-8

import argparse
import os
from konvertek.__init__ import __version__


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="konvertek. Convert media from folder.")

    parser.add_argument("--version", action="version", version=f"V{__version__}", help="Check version. ")

    subparsers = parser.add_subparsers(dest='command', required=True)

    # convert
    main_parser = subparsers.add_parser('convert', help='transcode')
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
    main_parser.add_argument("--v_codec", type=str,  # avc=H.264, hevc=H.265
                             choices=["libx264", "h264_nvenc", "h264_amf", "h264_vaapi",
                                      "libx265", "hevc_nvenc", "hevc_amf", "h265_vaapi",
                                      "libvpx-vp9", "vp9_qsv",
                                      "libaom-av1", "av1_vaapi",
                                      "libxvid", "rawvideo"],
                             default=None, required=False,
                             help="Chosen video codec for encoding video for destination folder {folder_path_out}. ")
    main_parser.add_argument("--resolution", type=str,
                             choices=["140p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p",
                                      "8640p"],
                             default=None, required=False,
                             help="Chosen video resolution for destination folder {folder_path_out}. ")
    main_parser.add_argument("--fps", type=int,
                             default=None, required=False,
                             help="Chosen video FPS for destination folder {folder_path_out}. ")
    main_parser.add_argument("--interpolation", type=str,
                             choices=["dup", "accurate", "blend", "bilat", "motion", ""],
                             default=None, required=False,
                             help="Apply interpolation if you need to add new frames when increasing/decreasing FPS "
                                  "for destination folder {folder_path_out}. "
                                  "It is recommended to play with the parameter and see the results before using it.")
    main_parser.add_argument("--bitrate", type=str,
                             default=None, required=False,
                             help="Chosen video bitrate for destination folder {folder_path_out}. "
                                  "For example: 2M, 512K... ")
    main_parser.add_argument("--maxbitrate", default=False, action='store_true',
                             help="If set, the bitrate cannot exceed the value specified in flag \"--bitrate\". ")
    main_parser.add_argument("--force_bitrate", default=False, action='store_true',
                             help="If set and if the bitrate in the source file is less than in flag \"--bitrate\", "
                                  "it will still be forced to the bitrate specified in flag \"--bitrate\". "
                                  "This action will increase the size of the output file. ")

    main_parser.add_argument('--replace', action='store_true',
                             help="Replace the video if it already exists in the destination folder. ")
    main_parser.add_argument('--no-replace', dest='replace', action='store_false',
                             help="Ask if needed to replace a file in the destination folder. ")
    main_parser.set_defaults(replace=True)

    main_parser.add_argument("--stop_if_error", default=False, action='store_true',
                             help="If set and error occurred while ffmpeg is running, konvertek will exit. ")
    main_parser.add_argument("--print_command", default=False, action='store_true',
                             help="Output ffmpeg command. ")

    # problem_info
    problem_info_parser = subparsers.add_parser('problem_info', help='Print problems')
    problem_info_parser.add_argument('progress_file_path',
                                     type=str,
                                     help='Path to file with progress. It is json. ')
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

        if args.force_bitrate and not args.bitrate:
            parser.error("Flag --force_bitrate cannot be define without --bitrate. ")
            exit()

    return args


def is_dir_path(_string):
    if os.path.isdir(_string):
        return _string
    else:
        print(f"\"{_string}\" is not directory. ")
        raise NotADirectoryError(_string)
