import os
import os.path as path
import pathlib

import __main__

project_name = "e6_scrapper"


def path_finder(relative_path: str) -> str:
    main_path = str(pathlib.Path(__main__.__file__))
    if main_path.split("\\")[-1] is project_name:
        project_dir = "\\".join(main_path.split("\\")[:-1])
        return path.normpath(path.join(project_dir, relative_path))
    else:
        file_path_l = main_path.split("\\")
        p = ""
        for i, d in enumerate(file_path_l):
            if d is project_name:
                p = main_path[:i]
                break
        p = "\\".join((p.split("\\"))[:-1])
        return path.normpath(path.join(p, relative_path))


def delete(file_path: str) -> None:
    try:
        temp = path_finder(file_path)
        os.remove(temp)
        print("Delete Successfully.")
    except FileNotFoundError:
        print("File not found or missing.")


def clear_dir(dir_path: str) -> None:
    try:
        temp = path_finder(dir_path)
        for file_name in os.listdir(temp):
            file_path = path.normpath(path.join(temp, file_name))
            if path.isfile(file_path):
                os.remove(file_path)
            else:
                os.rmdir(file_path)
        print("Cleared {}.".format(path.split(dir_path)[1]))
    except FileNotFoundError:
        print("Directory not found or missing.")


def output_log(l):
    with open("out.txt", "w") as out:
        for l in l:
            print(l, file=out)


def test() -> None:
    clear_dir("downloads")


if __name__ == "__main__":
    test()
