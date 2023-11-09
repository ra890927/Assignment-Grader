from typing import List
from pathlib import Path
from subprocess import call
from shutil import copy, copytree

from .utils import grep, insert, replace_all, change_file_encoding


class Compiler:
    def __init__(self, problem_num: int, exec_path: Path) -> None:
        self.exec_path = exec_path
        self.problem_num = problem_num
        self.makefile_path = self.__gen_makefile()
        self.additional_path = Path('./additional')

    def __del__(self) -> None:
        try:
            self.makefile_path.unlink()
        except:
            pass

    def __call__(self, std_id: str) -> list[bool]:
        return [
            prep and c
            for prep, c in zip(
                self.__preprocessing(std_id),
                self.__compile()
            )
        ]

    def __gen_makefile(self) -> Path:
        makefile_path = Path('./Makefile')
        with open(makefile_path, 'w+', encoding='utf-8') as f:
            f.write('all:\n')
            for pid in range(1, self.problem_num + 1):
                f.write(
                    '\tg++ -O2 -w *_hw_{:02d}.cpp -lm -o std_exec_{:02d}\n'
                    .format(pid, pid)
                )
        return makefile_path

    def __preprocessing(self, std_id: str) -> List[bool]:
        legal = [True for _ in range(self.problem_num)]
        for pid in range(1, self.problem_num + 1):
            file_path = self.exec_path.joinpath(
                '{}_hw_{:02d}.cpp'.format(std_id, pid)
            )
            try:
                change_file_encoding(file_path)
                self.__replace(file_path)
                self.__check_legal(file_path)
            except:
                legal[pid - 1] = False
        return legal

    def __replace(self, file_path: Path) -> None:
        insert('#include <stdbool.h>\n', file_path)
        insert('#include "vs_utils.h"\n', file_path)
        # remove system(pause)
        replace_all(
            r'system\(\ *pause\ *\)',
            '',
            file_path
        )

    def __check_legal(self, file_path) -> bool:
        return all([
            not grep(r'#include\ *<iostream>', file_path),
            not grep(r'#include\ *<cstring>', file_path),
            not grep(r'#include\ *<cstdlib>', file_path),
            not grep(r'#include\ *<cstdio>', file_path)
        ])

    def __compile(self) -> bool:
        copy(self.makefile_path, self.exec_path)
        copytree(self.additional_path, self.exec_path, dirs_exist_ok=True)

        call(f'cd {self.exec_path}; make', shell=True)

        legal = [True for _ in range(self.problem_num)]
        for pid in range(1, self.problem_num + 1):
            try:
                assert self.exec_path.joinpath(f'std_exec_{pid:02d}').exists()
            except:
                legal[pid - 1] = False
        return legal
