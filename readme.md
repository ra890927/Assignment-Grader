# Assignment Grader

## Introduction

This is a python script for grading homework, which compiled by Visual Studio 2019.

Host: Windows 10 (x86)
Platform: Visual Studio 2019

## Environment

### python package list
```
pandas
python-magic
python-magic-bin
```

### preprocessing

1. config setting

```
# for exmaple
[compiler]
VISUAL_STUDIO_CMD = C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat
```

2. student list

Include all students' student id

3. score setting

```json
{
    "pid": {
        "0101": 10,
        "0102": 10,
        ...
    }
}
```

4. testdata

```
testdata
├───0101.in
├───0101.out
├───0102.in
├───0102.out
├───0201.in
├───0201.out
├───0202.in
└───0202.out
```

## Execution

```
usage: main.py [-h] [--id ID] [--pid_mask [PID_MASK ...]] [--zip_pat ZIP_PAT] [--code_pat CODE_PAT]
               assignment problems

positional arguments:
  assignment            Assignment id
  problems              The number of homework

optional arguments:
  -h, --help            show this help message and exit
  --id ID               Test specific student id
  --pid_mask [PID_MASK ...]
                        Test pids
  --zip_pat ZIP_PAT     The pattern for zip file
  --code_pat CODE_PAT   The pattern for code file
```