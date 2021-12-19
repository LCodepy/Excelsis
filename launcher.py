import os

from skec.ide.main.main import IDE


if __name__ == "__main__":
    os.system("cls")
    # file_to_load = input("Load file (return if don't want to load): ")
    # file_to_save = input("Save file (return if don't want to load or '=' if the same as load file): ")
    # print()
    # print("Loading...")
    #
    # if not os.path.exists(file_to_load):
    #     print(f"Failed to load file: {file_to_load!r}")
    #     file_to_load = None
    # elif not file_to_load.endswith(".pkl"):
    #     print(f"Invalid file extension, '.pkl' required!")
    #     file_to_load = None
    #
    # if file_to_save in ("=", "'='"):
    #     file_to_save = file_to_load
    # if not os.path.exists(file_to_save):
    #     print(f"Failed to load file: {file_to_save!r}")
    #     file_to_save = None
    # elif not file_to_save.endswith(".pkl"):
    #     print(f"Invalid file extension, '.pkl' required!")
    #     file_to_save = None

    app = IDE()  # (file_to_load, file_to_save)
    app.run()
