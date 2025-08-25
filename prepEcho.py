import os
from PIL import Image

def process_folder(folder_path):
    # Loop through everything in the folder
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # Skip macOS hidden resource fork files
            if file.startswith("._"):
                continue  

            file_path = os.path.join(root, file)

            # Convert .jpg to 500x500
            if file.lower().endswith(".jpg"):
                try:
                    with Image.open(file_path) as img:
                        if img.size == (500, 500):
                            print(f"Skipped (already 500x500): {file_path}")
                            continue
                        img_resized = img.resize((500, 500))
                        img_resized.save(file_path)
                        print(f"Resized: {file_path}")
                except Exception as e:
                    print(f"Error resizing {file_path}: {e}")

            # Delete .lrc files
            elif file.lower().endswith(".lrc"):
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")


if __name__ == "__main__":
    folder = input("Enter the folder path: ").strip()
    if os.path.isdir(folder):
        process_folder(folder)
    else:
        print("Invalid folder path")