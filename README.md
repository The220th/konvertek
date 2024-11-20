# konvertek

konvertek konvert all video files from one folder to another with certain video encoder, bitrate, resolution and fps. 
The file hierarchy will be preserved exactly as in the original directory.


# Installation and usage

Install by typing:

```bash
pip3 install konvertek
```

Run:

```bash
konvertek convert /path/to/source/dir /path/to/destenation/dir /path/to/progress.json \
                  --v_codec libx265 --bitrate 3M \ 
                  --resolution 720p --fps 24

         # progress.json is file, which contains transcode progress. 
         # If failed or power outages, this file will store progress.
         # Just retype command again with same progress.json
```

If needed hardware acceleration, use video encoder (`--v_codec`) `hevc_nvenc` (H.265) or `h264_nvenc` (H.264) for nvidia 
and  `h265_vaapi` (H.265) or `h264_vaapi` (H.264) for amd. Use `--help` for more parameters.
