import os

playlists_dir = "/Volumes/MUSIC/playlists"

for folder in os.listdir(playlists_dir):
    folder_path = os.path.join(playlists_dir, folder)
    if os.path.isdir(folder_path):
        m3u_path = os.path.join(playlists_dir, f"{folder}.m3u")
        with open(m3u_path, "w", encoding="utf-8") as m3u:
            for file in sorted(os.listdir(folder_path)):
                if file.lower().endswith(('.mp3', '.m4a', '.flac', '.wav', '.ogg')):
                    m3u.write(os.path.join(folder_path, file) + "\n")
        print(f"Created playlist: {m3u_path}")