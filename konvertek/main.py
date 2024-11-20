# coding: utf-8

from konvertek.parsing import get_args
from konvertek.process import video_processing, list_extensions_processing, problem_info_processing


def main():
    args = get_args()
    if args.command == "convert":
        video_processing(args)
    elif args.command == "list_extensions":
        list_extensions_processing(args)
    elif args.command == "problem_info":
        problem_info_processing(args)
    else:
        print("Failed successfully (main). ")


if __name__ == "__main__":
    main()
