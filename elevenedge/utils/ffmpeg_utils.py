from pathlib import Path
import subprocess


def extract_audio(video_path: Path, audio_path: Path) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        'ffmpeg',
        '-y',
        '-i',
        str(video_path),
        '-vn',
        '-acodec',
        'pcm_s16le',
        '-ar',
        '16000',
        '-ac',
        '1',
        str(audio_path),
    ]
    subprocess.run(command, check=True, capture_output=True)


def generate_clip(input_path: Path, output_path: Path, start_seconds: float, end_seconds: float) -> None:
    duration = max(0.1, end_seconds - start_seconds)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        'ffmpeg',
        '-y',
        '-ss',
        str(start_seconds),
        '-i',
        str(input_path),
        '-t',
        str(duration),
        '-c:v',
        'libx264',
        '-c:a',
        'aac',
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True)
