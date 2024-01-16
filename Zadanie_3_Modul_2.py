import os
import sys
from pathlib import Path
import zipfile
import concurrent.futures

file_extensions_mapping = {
    'video': ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.3gp', '.3g2', '.mpg', '.mpeg', '.m4v', '.h264', '.flv',
              '.rm', '.swf', '.vob'],
    'audio': ['.mp3', '.wav', '.ogg', '.flac', '.aif', '.mid', '.midi', '.mpa', '.wma', '.wpl', '.cda'],
    'image': ['.jpg', '.png', '.bmp', '.ai', '.psd', '.ico', '.jpeg', '.ps', '.svg', '.tif', '.tiff'],
    'archives': ['.zip', '.rar', '.7z', '.z', '.gz', '.rpm', '.arj', '.pkg', '.deb'],
    'documents': ['.pdf', '.txt', '.doc', '.docx', '.rtf', '.tex', '.wpd', '.odt'],
}

known_extensions = {
    extension
    for extensions in file_extensions_mapping.values()
    for extension in extensions
}


def create_folders_from_list(folder_path, folder_names):
    for folder in folder_names:
        path = Path(folder_path, folder)
        if not path.exists():
            os.mkdir(path)


def sort_files(target_folder, folder, extensions):
    for directory, sub_folder, files in os.walk(target_folder):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(move_file, Path(directory, file), Path(target_folder, folder, file))
                       for file in files if Path(file).suffix in extensions]
            concurrent.futures.wait(futures)


def move_file(source_path, target_path):
    os.rename(source_path, target_path)


def normalize(text: str) -> str:
    substitute_mapping = {
        'Ą': 'A', 'ą': 'a', 'Ć': 'C', 'ć': 'c', 'Ę': 'E', 'ę': 'e', 'Ń': 'N',
        'ń': 'n', 'Ś': 'S', 'ś': 's', 'Ż': 'Z', 'ż': 'z', 'ó': 'o', 'Ó': 'O',
        'Ź': 'Z', 'ź': 'z', 'Ł': 'L', 'ł': 'l', " ": "_"
    }
    result = []
    for ch in text:
        if ch not in substitute_mapping:
            result.append(ch)
        else:
            result.append(substitute_mapping[ch])
    return "".join(result)


def normalize_files(root_folder):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(rename_file, Path(directory, file), normalize(file))
                   for directory, sub_folder, files in os.walk(root_folder) for file in files]
        concurrent.futures.wait(futures)


def rename_file(path, new_name):
    os.rename(path, Path(path.parent, new_name))


def delete_empty_folders(root_folder, exclude_folders=None):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(delete_folder, folder) for folder_name, sub_folders, filenames in
                   os.walk(root_folder, topdown=False) for sub_folder in sub_folders
                   if (exclude_folders is None or sub_folder not in exclude_folders) and not os.listdir(
                       os.path.join(folder_name, sub_folder))]
        concurrent.futures.wait(futures)


def delete_folder(folder_path):
    os.rmdir(folder_path)


def unpacking_files(target_folder):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(unpack_file, root, file) for root, dirs, files in os.walk(target_folder)
                   for file in files if file.endswith(('.zip', '.rar'))]
        concurrent.futures.wait(futures)


def unpack_file(root, file):
    archive_path = os.path.join(root, file)
    try:
        if file.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(os.path.splitext(archive_path)[0])
        # else:
        #     with rarfile.RarFile(archive_path, 'r') as rar_ref:
        #         rar_ref.extractall(os.path.splitext(archive_path)[0])
    except Exception as e:
        print(f"Error extracting {archive_path}: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: sortfiles <target_folder>")
        sys.exit(-1)

    target_path = sys.argv[1]

    if not os.path.exists(target_path):
        print(f"Target folder does not exist: {target_path}")
        sys.exit(-1)

    folders = list(file_extensions_mapping.keys())
    folders.append("unknowns")
    create_folders_from_list(target_path, folders)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(sort_files, target_path, file_type, extensions) for file_type, extensions in
                   file_extensions_mapping.items()]
        concurrent.futures.wait(futures)

    extensions_in_target_folder = set()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_extensions, target_path, extensions_in_target_folder) for directory, sub_folder,
                   files in os.walk(target_path)]
        concurrent.futures.wait(futures)

    unknown_extensions = extensions_in_target_folder - known_extensions
    sort_files(target_path, "unknowns", unknown_extensions)

    unpacking_files(target_path)

    delete_empty_folders(target_path, exclude_folders=folders)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(normalize_files, target_path)]
        concurrent.futures.wait(futures)


def get_extensions(directory, extensions_in_target_folder):
    for file in os.listdir(directory):
        extensions_in_target_folder.add(Path(file).suffix)


if __name__ == "__main__":
    main()
