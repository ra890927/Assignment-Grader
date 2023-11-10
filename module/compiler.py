from typing import List
from pathlib import Path
from subprocess import call
from configparser import ConfigParser

from .utils import grep, change_file_encoding


class Compiler:
    def __init__(self, code_pat: str, problem_num: int, exec_path: Path) -> None:
        self.code_pat = code_pat
        self.exec_path = exec_path
        self.problem_num = problem_num

        config = ConfigParser()
        config.read('./docs/config.ini')
        self.env_path = Path(config['compiler']['VISUAL_STUDIO_CMD'])

    def __call__(self, std_id: str) -> list[bool]:
        return [
            prep and c
            for prep, c in zip(
                self.__preprocessing(std_id),
                self.__compile()
            )
        ]

    def __preprocessing(self, std_id: str) -> List[bool]:
        legal = [True for _ in range(self.problem_num)]
        for pid in range(1, self.problem_num + 1):
            file_path = self.exec_path.joinpath(self.code_pat.format(std_id, pid))
            try:
                change_file_encoding(file_path)
                self.__check_legal(file_path)
            except:
                legal[pid - 1] = False
        return legal

    def __check_legal(self, file_path) -> bool:
        return all([
            not grep(r'#include\ *<iostream>', file_path),
            not grep(r'#include\ *<cstring>', file_path),
            not grep(r'#include\ *<cstdlib>', file_path),
            not grep(r'#include\ *<cstdio>', file_path)
        ])

    def __compile(self) -> bool:
        # compile
        for pid in range(1, self.problem_num + 1):
            code_name = self.code_pat.format('*', pid)
            call(
                f'cl /W4 /sdl {self.exec_path}\\{code_name} /Fe{self.exec_path}\\std_exec_{pid:02d}.exe',
                shell=True, executable=self.env_path
            )

        legal = [True for _ in range(self.problem_num)]
        for pid in range(1, self.problem_num + 1):
            try:
                assert self.exec_path.joinpath(f'std_exec_{pid:02d}.exe').exists()
            except:
                legal[pid - 1] = False
        return legal
