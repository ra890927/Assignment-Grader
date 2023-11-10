import json
from glob import glob
from pathlib import Path
from subprocess import call
from pandas import DataFrame
from shutil import copy, rmtree
from argparse import ArgumentParser, Namespace

from module.tester import Tester
from module.compiler import Compiler

class AssignmentGrader:
    def __init__(self, hw_id: int, problem_num: int, args: Namespace) -> None:
        self.args = args
        self.hw_id = hw_id
        self.problem_num = problem_num

        self.columns = ['student_id']
        for i in range(problem_num):
            self.columns += [
                'problem_{:02d}'.format(i + 1),
                'reason_{:02d}'.format(i + 1)
            ]

        self.exec_path = Path('./cache')
        self.test_root = Path('./testdata')
        self.assignments_root = Path('./assignments')
        self.student_list_path = Path('./docs/student_list.json')

        self.check_environment()

        if self.args.id != None:
            self.student_list = [self.args.id]
        else:
            with open(self.student_list_path, 'r') as f:
                self.student_list = json.load(f)

        self.tester = Tester(problem_num, timeout=10)
        self.compiler = Compiler(args.code_pat, problem_num, self.exec_path)

    def __reset_exec(self) -> None:
        if self.exec_path.exists():
            rmtree(self.exec_path)
        self.exec_path.mkdir()

    def check_environment(self) -> None:
        # student list
        assert self.student_list_path.is_file(), 'Missing student list file'
        # student assignments
        assert self.assignments_root.is_dir(), 'Missing assignments'
        # testdata
        assert self.test_root.is_dir(), 'Missing testdata'

    def preprocessing(self, std_id: str) -> bool:
        zip_name = self.args.zip_pat.format(std_id, self.hw_id)
        assignment_root = glob(
            rf'{self.assignments_root}/{std_id}*/{zip_name}')
        assert len(assignment_root) <= 1, 'Has same student id folder'

        if len(assignment_root) == 0:
            return False

        assignment_zip = assignment_root[0]
        copy(assignment_zip, self.exec_path)
        assignment_zip = Path(assignment_zip).name

        call(f'tar -xf {self.exec_path}/{assignment_zip} -C {self.exec_path}', shell=True)

        for pid in range(1, self.problem_num + 1):
            for i in range(1, 3):
                inner_path = '*/' * i
                code_name = self.args.code_pat.format(std_id, pid)
                find_res = glob(f'{self.exec_path}/{inner_path}{code_name}')
                if len(find_res):
                    pid_code_path = find_res[0]
                    copy(pid_code_path, self.exec_path)

        return True

    def grade(self) -> DataFrame:
        records = []
        for std_id in self.student_list:
            self.__reset_exec()
            if (self.preprocessing(std_id)):
                pid_legal_list = [False] + self.compiler(std_id)
                test_result = self.tester(pid_legal_list)
            else:
                test_result = {
                    pid: {'score': 0, 'reason': 'put off'}
                    for pid in range(1, self.problem_num + 1)
                }

            record = {'student_id': std_id}
            for pid in range(1, self.problem_num + 1):
                record.update({
                    f'problem_{pid:02d}': test_result[pid]['score'],
                    f'reason_{pid:02d}': test_result[pid]['reason']
                })

            records.append(record)
            call('del *.obj', shell=True)

        if not self.args.id:
            rmtree(self.exec_path)
        
        result_df = DataFrame.from_records(records)
        result_df.to_csv(f'hw_{self.hw_id:02d}.csv', index=False)

        return result_df


def parse_argument() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('assignment', type=int, help='Assignment id')
    parser.add_argument('problems', type=int, help='The number of homework')
    parser.add_argument('--id', type=str, help='Test specific student id')
    parser.add_argument('--pid_mask', type=int, nargs='*', help='Test pids')
    parser.add_argument('--zip_pat', type=str, default='{}_hw_w{:02d}.zip',
                                                help='The pattern for zip file')
    parser.add_argument('--code_pat', type=str, default='{}_hw_{:02d}.cpp',
                                                help='The pattern for code file')
    return parser.parse_args()


def main() -> None:
    args = parse_argument()
    assignment = args.assignment
    problems = args.problems
    args.pid_mask = list(map(int, args.pid_mask)) if len(args.pid_mask) \
                    else [pid for pid in range(1, problems + 1)]

    grader = AssignmentGrader(assignment, problems, args)
    grader.grade()


if __name__ == '__main__':
    main()
