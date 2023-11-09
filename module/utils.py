import re
import codecs
from enum import Enum
from magic import Magic
from pathlib import Path

__BLOCK_SIZE = 4096


class FileEncoding(Enum):
    BIG5 = 'big5'
    UTF8 = 'utf-8'
    ASCII = 'ascii'
    GB2312 = 'gb2312'
    USASCII = 'us-ascii'
    UTF8SIG = 'utf-8-sig'
    ISO8859_1 = 'iso-8859-1'

    def __str__(self) -> str:
        return self.value


def grep(pattern: str, file: Path, flag=0, revert: bool = False) -> bool:
    try:
        with open(file) as f:
            return revert ^ any([
                re.search(pattern, line.strip(), flag)
                for line in f
            ])
    except Exception as e:
        print(e)
        return False


def get_file_encoding(file_path: Path) -> FileEncoding:
    """
    get file encoding
    """

    with open(file_path, 'rb') as f:
        m = Magic(mime_encoding=True)
        encoding = m.from_buffer(f.read(__BLOCK_SIZE))
        return FileEncoding(encoding)


def change_file_encoding(
    file_path: Path,
    target_enc: FileEncoding = FileEncoding.UTF8
) -> None:
    """
    change file encoding to target_enc
    """

    original_enc = get_file_encoding(file_path)
    if original_enc == target_enc:
        return

    target_path = file_path.cwd().joinpath('temp.txt')
    with codecs.open(file_path, 'rb', str(original_enc)) as source:
        with codecs.open(target_path, 'w+', str(target_enc)) as target:
            while True:
                content = source.read(__BLOCK_SIZE)
                if len(content) == 0:
                    break
                target.write(content)

    file_path.unlink()
    target_path.rename(file_path)


def replace_all(pattern: str, repl: str, file_path: Path) -> None:
    """
    file replace 
    """

    target_path = file_path.cwd().joinpath('temp.txt')
    with codecs.open(file_path, 'r', 'utf-8') as source:
        with codecs.open(target_path, 'w+', 'utf-8') as target:
            content = re.sub(pattern, repl, source.read())
            target.write(content)

    target_path.rename(file_path)


def insert(content: str, file_path: Path) -> None:
    """
    insert content to file
    """

    target_path = file_path.cwd().joinpath('temp.txt')
    with codecs.open(file_path, 'r', 'utf-8') as source:
        with codecs.open(target_path, 'w+', 'utf-8') as target:
            target.write(content)
            for line in source.readlines():
                target.write(line)
    target_path.rename(file_path)


if __name__ == '__main__':
    file_path = Path('../cache/112550128_hw_01.cpp')
    change_file_encoding(file_path)

    print(grep(r'^[sf]?scanf\ *\(.+\)', file_path))
    print(grep(r'#pragma\ +warning\ *\(\ *disable\ *:\ *4996\ *\)|#define\ +_CRT_SECURE_NO_WARNINGS', file_path))

    # insert('#include "vs_utils.h"', Path('../cache/112550128_hw_01.cpp'))
    # replace_all(
    #     r'gets_s\ *\(\ *(\w+)\ *\)',
    #     r'scanf\("%s", \1\)',
    #     Path('../cache/112550128_hw_01.cpp')
    # )
