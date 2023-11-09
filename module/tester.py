import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


class Tester:
    def __init__(self, problem_num: int, timeout: int = 5) -> None:
        self.timeout = timeout
        self.problem_num = problem_num

        self.execute_path = Path('./cache')
        self.testcase_root_path = Path('./testdata')

        with open('./docs/score_setting.json') as f:
            self.score_setting = json.load(f)

    def __call__(self, mask_: List[bool] = []) -> List[Dict]:
        return_dict = {
            pid: {'score': 0, 'reason': []}
            for pid in range(1, self.problem_num + 1)
        }
        for pid in range(1, self.problem_num + 1):
            # ce will not test
            if len(mask_) and not mask_[pid]:
                return_dict[pid]['reason'] = ['CE']
            else:
                for task_id, score in self.score_setting[str(pid)].items():
                    input_path, result_path, output_path, exec_path = \
                        self.__get_test_all_path(pid, task_id)

                    return_code = self.__execute(
                        exec_path, input_path, output_path)
                    if return_code == 0:
                        if self.__file_cmp(output_path, result_path):
                            return_dict[pid]['score'] += score
                        else:
                            return_dict[pid]['reason'].append(task_id)
                    elif return_code == -2:
                        return_dict[pid]['reason'].append(f'{task_id}-TLE')
                    elif return_code == -3 or return_code == -4:
                        return_dict[pid]['reason'].append(
                            f'{task_id}-RE {self.exec_err}')
                    else:
                        return_dict[pid]['reason'] = ['CE']

            return_dict[pid]['reason'] = ', '.join(return_dict[pid]['reason'])

        return return_dict

    def __get_test_all_path(self, pid: int, task_id: str) -> Tuple[Path, Path, Path, Path]:
        input_path = self.testcase_root_path.joinpath(f'{task_id}.in')
        result_path = self.testcase_root_path.joinpath(f'{task_id}.out')
        output_path = self.execute_path.joinpath(f'user_{task_id}.out')
        exec_path = self.execute_path.joinpath('std_exec_{:02d}'.format(pid))
        return input_path, result_path, output_path, exec_path

    def __execute(self, exec_path: Path, input_path: Path, output_path: Path) -> int:
        with open(input_path) as inputf:
            try:
                p = subprocess.run(
                    exec_path, stdin=inputf, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, timeout=self.timeout
                )
                p.check_returncode()

                with open(output_path, 'w+', encoding='utf-8') as outputf:
                    outputf.write(p.stdout.decode())
                return 0
            except FileNotFoundError:
                return -1
            except subprocess.TimeoutExpired:
                return -2
            except subprocess.CalledProcessError:
                self.exec_err = p.stderr.decode()
                return -3
            except Exception as e:
                self.exec_err = e
                return -4

    def __file_cmp(self, file1: Path, file2: Path) -> bool:
        with open(file1) as f1, open(file2) as f2:
            f1_lines = list(filter(None, [line.strip() for line in f1.readlines()]))
            f2_lines = list(filter(None, [line.strip() for line in f2.readlines()]))
            return len(f1_lines) == len(f2_lines) and all([
                line1.strip() == line2.strip()
                for line1, line2 in zip(f1_lines, f2_lines)
            ])
