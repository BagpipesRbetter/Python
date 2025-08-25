#!/usr/bin/env python3
import shutil
import subprocess
import sys
from pathlib import Path

# ---- CONFIG ----
MUSIC_ROOT = Path("/Users/evanbarclay/Music")  # change if needed
COVER_NAMES = [
    "folder.jpg", "folder.png",
    "cover.jpg", "cover.png",
    "front.jpg", "Front.jpg",
    "album.jpg", "Album.jpg", "AlbumArtSmall.jpg", "AlbumArt.jpg",
]
# ---------------

def have_fileicon() -> bool:
    return shutil.which("fileicon") is not None

def safe_iterdir(p: Path):
    try:
        return [c for c in p.iterdir() if not c.name.startswith(".")]
    except PermissionError:
        return []

def folder_has_custom_icon(folder: Path) -> bool:
    return (folder / "Icon\r").exists()

def find_best_cover_for_artist(artist_folder: Path) -> Path | None:
    """Scan one level of album subfolders for any known cover name.
       Pick the largest file by bytes."""
    best = None
    best_size = -1
    for album in safe_iterdir(artist_folder):
        if not album.is_dir():
            continue
        for name in COVER_NAMES:
            cand = album / name
            if cand.exists() and cand.is_file():
                try:
                    size = cand.stat().st_size
                except OSError:
                    continue
                if size > best_size:
                    best = cand
                    best_size = size
    return best

def set_folder_icon(folder: Path, image: Path) -> bool:
    try:
        subprocess.run(["fileicon", "set", str(folder), str(image)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    if not have_fileicon():
        print("❌ 'fileicon' not found. Install with: brew install fileicon")
        sys.exit(1)

    if not MUSIC_ROOT.exists():
        print(f"❌ Base path not found: {MUSIC_ROOT}")
        sys.exit(1)

    choice = input("Overwrite existing icons for ALL matched folders? [y/N]: ").strip().lower()
    overwrite_all = (choice == "y")

    total = matched = updated = skipped = 0

    for artist in safe_iterdir(MUSIC_ROOT):
        if not artist.is_dir():
            continue
        total += 1
        cover = find_best_cover_for_artist(artist)
        if not cover:
            # No cover in any album
            continue
        matched += 1
        if folder_has_custom_icon(artist) and not overwrite_all:
            print(f"➡️  Skipped (icon exists): {artist}")
            skipped += 1
            continue

        ok = set_folder_icon(artist, cover)
        if ok:
            print(f"✅ Set icon: {artist}  ←  {cover}")
            updated += 1
        else:
            print(f"❌ Failed to set icon: {artist}")

    print("\n--- Summary ---")
    print(f"Artists scanned: {total}")
    print(f"Artists with cover found: {matched}")
    print(f"Icons updated: {updated}")
    print(f"Skipped (existing icons): {skipped}")

if __name__ == "__main__":
    main()