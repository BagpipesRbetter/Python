import os
import subprocess
import sys
import logging
from pathlib import Path
import colorama

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class DummyFore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        CYAN = ""
    class DummyStyle:
        RESET_ALL = ""
    Fore, Style = DummyFore(), DummyStyle()

logging.basicConfig(
    level=logging.INFO,
    format=f"{Fore.CYAN}[%(levelname)s]{Style.RESET_ALL} %(message)s"
)

def is_alac(file_path):
    """Check if a file is actually ALAC using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
             "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        codec = result.stdout.decode().strip().lower()
        return codec == "alac"
    except subprocess.CalledProcessError:
        logging.warning(f"{Fore.YELLOW}Could not probe file:{Style.RESET_ALL} {file_path}")
        return False

def convert_alac_to_flac(root_folder):
    converted_count = 0
    skipped_count = 0
    failed_count = 0

    for path in Path(root_folder).rglob("*"):
        if path.is_file() and path.suffix.lower().strip() in ('.m4a', '.alac'):
            if not is_alac(path):
                logging.info(f"{Fore.YELLOW}Skipping (not ALAC):{Style.RESET_ALL} {path}")
                skipped_count += 1
                continue

            flac_path = path.with_suffix(".flac")
            if flac_path.exists():
                logging.warning(f"{Fore.YELLOW}Skipping (already exists):{Style.RESET_ALL} {path}")
                skipped_count += 1
                continue

            logging.info(f"Converting: {path}")
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(path), "-c:a", "flac", "-map_metadata", "0", str(flac_path)],
                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                path.unlink()  # Remove original
                logging.info(f"{Fore.GREEN}✅ Converted and deleted:{Style.RESET_ALL} {path}")
                converted_count += 1

            except FileNotFoundError:
                logging.error(f"{Fore.RED}❌ ffmpeg not found. Please install it.{Style.RESET_ALL}")
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                logging.error(f"{Fore.RED}❌ Error converting {path}:{Style.RESET_ALL}\n{e.stderr.decode('utf-8', errors='ignore')}")
                failed_count += 1

    logging.info(
        f"\n{Fore.CYAN}Summary:{Style.RESET_ALL} "
        f"{Fore.GREEN}{converted_count} converted{Style.RESET_ALL}, "
        f"{Fore.YELLOW}{skipped_count} skipped{Style.RESET_ALL}, "
        f"{Fore.RED}{failed_count} failed{Style.RESET_ALL}"
    )

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python convert_alac_to_flac.py /path/to/folder")
        sys.exit(1)

    folder = Path(sys.argv[1])
    if not folder.is_dir():
        logging.error("Invalid folder path.")
        sys.exit(1)

    convert_alac_to_flac(folder)