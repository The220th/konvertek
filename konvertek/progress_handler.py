# coding: utf-8

from ksupk import singleton_decorator, restore_json, save_json
from ksupk import get_files_list
from threading import Lock
import os


@singleton_decorator
class ProgressHandler:
    def __init__(self, json_path: str):
        self.__lock = Lock()
        self.__path = json_path

        self.__old_containers = [".avi"]

        if not os.path.isfile(json_path):
            self.create_new()
        self.db = restore_json(json_path)

    def flush(self):
        with self.__lock:
            save_json(self.__path, self.db)

    def add_files(self, files: dict):
        for k_i in files:
            self.db["files"][k_i] = files[k_i]
        self.flush()

    def update(self, file: str, doned: bool, error_text: str | None):
        self.db["files"][file]["status"] = doned
        if error_text is not None:
            self.db["errors"][file] = error_text
        else:
            self.db["errors"].pop(file, None)
        self.flush()

    def file_status(self, file: str) -> bool:
        return self.db["files"][file]["status"]

    def get_file_in_out(self, file: str) -> tuple:
        return self.db["files"][file]["in"], self.db["files"][file]["out"]

    def get_db(self) -> dict:
        return self.db.copy()

    def set_error(self, file: str, error_text: str):
        self.db["errors"][file] = error_text
        self.flush()

    def get_errors(self) -> dict:
        return self.db["errors"]

    def get_files(self) -> dict:
        return self.db["files"]

    def create_new(self):
        d = {
            "files": {},
            "errors": {}
        }
        self.db = d
        self.flush()

    def create_files_4_progress(self, dir_in: str, dir_out: str) -> dict:
        d = {}
        files = get_files_list(os.path.abspath(dir_in))
        files = [os.path.relpath(file_i, dir_in) for file_i in files]
        for file_i in files:
            status = False
            if file_i in self.db["files"]:
                if "status" in self.db["files"][file_i]:
                    status = self.db["files"][file_i]["status"]
            out_file_path = self.define_save_path(dir_out, file_i)
            d[file_i] = {"in": os.path.join(dir_in, file_i),
                         "out": out_file_path,
                         "status": status
                         }
        return d

    def define_save_path(self, out_folder: str, file: str) -> str:
        if str(os.path.splitext(file)[1]).lower() in self.__old_containers:
            p, e = os.path.splitext(file)
            return os.path.join(out_folder, f"{p}.mp4")
        else:
            return os.path.join(out_folder, file)
