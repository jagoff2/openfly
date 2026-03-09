from __future__ import annotations

import argparse
from pathlib import Path

import imageio.v2 as imageio


def read_frame(video_path: Path, frame_index: int):
    reader = imageio.get_reader(video_path)
    try:
        if frame_index >= 0:
            return reader.get_data(frame_index)
        frame = None
        for frame in reader:
            pass
        if frame is None:
            raise RuntimeError(f"No frames found in {video_path}")
        return frame
    finally:
        reader.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("videos", nargs="+")
    parser.add_argument("--frame-index", type=int, default=-1, help="0-based frame index, or -1 for the last frame")
    parser.add_argument("--output-dir", default="outputs/screenshots")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for video in args.videos:
        video_path = Path(video)
        frame = read_frame(video_path, args.frame_index)
        output_path = output_dir / f"{video_path.stem}.png"
        imageio.imwrite(output_path, frame)
        print(output_path)


if __name__ == "__main__":
    main()
