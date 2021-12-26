import os
import sys
import time
from dataclasses import field

import src
from src.ide.main.main import IDE

if __name__ == "__main__":
    os.system("cls")
    sys.modules['skec'] = src
    sys.modules['skec.ide'] = src.ide
    sys.path.append("src")
    file_to_load = input("Load file (return if don't want to load): ").replace("\\", "/")
    file_to_save = input("Save file (return if don't want to load or '=' if the same as load file): ").replace("\\", "/")
    print()
    print("Loading...")

    if not os.path.exists(file_to_load) and file_to_load != "":
        print(f"Failed to load file: {file_to_load!r}")
        file_to_load = None
    elif not file_to_load.endswith(".pkl") and file_to_load != "":
        print(f"Invalid file extension, '.pkl' required!")
        file_to_load = None

    if file_to_save in ("=", "'='"):
        file_to_save = file_to_load
    if (
        file_to_save is not None
        and not file_to_save.endswith(".pkl")
        and file_to_save != ""
    ):
        print(f"Invalid file extension, '.pkl' required!")
        file_to_save = None

    time.sleep(2)
    app = IDE(file_to_load or None, file_to_save or None)
    app.run()
