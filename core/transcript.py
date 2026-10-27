"""YouTube link -> transcript.txt + video.json inside an episode folder.

    .venv/bin/python -m core.transcript <url> <episode_dir>

1. yt-dlp captions (manual first, then auto; Hindi, English, then whatever exists).
2. No captions -> download audio and transcribe with mlx-whisper. It is installed into
   .venv on first use and its model is cached in Series_Backtest/_models/ (never outside).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yt_dlp

from core.paths import MODELS, ROOT

LANGS = ["hi", "en", "en-IN", "hi-IN", "en-orig", "hi-orig"]
WHISPER_MODEL = "mlx-community/whisper-large-v3-turbo"


def _vtt_to_text(vtt: str) -> str:
    lines, last = [], None
    for line in vtt.splitlines():
        if "-->" in line or not line.strip() or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        text = re.sub(r"<[^>]+>", "", line).strip()
        if text and text != last:  # auto-captions repeat each line as it scrolls
            lines.append(text)
            last = text
    return "\n".join(lines)


def _pick(tracks: dict) -> str | None:
    for lang in LANGS:
        if lang in tracks:
            return lang
    return next(iter(tracks), None)


def _local_tools_on_path():
    """yt-dlp needs deno (YouTube JS) and ffmpeg; both live in .venv, exposed for this process only."""
    import imageio_ffmpeg

    bin_dir = ROOT / ".venv" / "ffbin"
    bin_dir.mkdir(exist_ok=True)
    link = bin_dir / "ffmpeg"
    if not link.exists():
        link.symlink_to(imageio_ffmpeg.get_ffmpeg_exe())
    os.environ["PATH"] = os.pathsep.join([str(bin_dir), str(ROOT / ".venv" / "bin"), os.environ["PATH"]])


def fetch(url: str, out: Path) -> Path:
    _local_tools_on_path()
    out.mkdir(parents=True, exist_ok=True)
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as y:
        info = y.extract_info(url, download=False)
    meta = {k: info.get(k) for k in ("id", "title", "channel", "uploader", "upload_date", "duration",
                                     "webpage_url", "description")}
    subs, auto = info.get("subtitles") or {}, info.get("automatic_captions") or {}
    lang, manual = _pick(subs), True
    if not lang:
        lang, manual = _pick(auto), False
    if lang:
        opts = {"quiet": True, "skip_download": True, "writesubtitles": manual, "writeautomaticsub": not manual,
                "subtitleslangs": [lang], "subtitlesformat": "vtt", "outtmpl": str(out / "captions")}
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])
        vtt = next(out.glob("captions*.vtt"))
        text = _vtt_to_text(vtt.read_text())
        meta["transcript_source"] = f"{'manual' if manual else 'auto'} captions ({lang})"
    else:
        text = _whisper(url, out)
        meta["transcript_source"] = f"whisper ({WHISPER_MODEL})"
    (out / "transcript.txt").write_text(text)
    (out / "video.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print(f"{meta['title']} — {meta['channel']}\n{meta['transcript_source']}: {len(text.split())} words -> {out}")
    return out / "transcript.txt"


def _whisper(url: str, out: Path) -> str:
    try:
        import mlx_whisper
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "mlx-whisper"], check=True)
        import mlx_whisper
    opts = {"quiet": True, "format": "bestaudio/best", "outtmpl": str(out / "audio.%(ext)s"),
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "wav"}]}
    with yt_dlp.YoutubeDL(opts) as y:
        y.download([url])
    os.environ["HF_HOME"] = str(MODELS)
    res = mlx_whisper.transcribe(str(out / "audio.wav"), path_or_hf_repo=WHISPER_MODEL)
    (out / "audio.wav").unlink(missing_ok=True)
    return "\n".join(s["text"].strip() for s in res["segments"])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    fetch(sys.argv[1], Path(sys.argv[2]) / "source")
