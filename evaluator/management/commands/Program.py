import filecmp
import os
from enum import Enum, auto
from pathlib import Path
import subprocess

EXECUTABLE_PATH_PREFIX = '/home/ubuntu/code_evaluator/executables/'
SOURCE_PATH_PREFIX = '/home/ubuntu/code_evaluator/source_codes/'
EXPECTED_OUTPUT_PATH_PREFIX = '/home/ubuntu/code_evaluator/expected_output/'
INPUT_PATH_PREFIX = '/home/ubuntu/code_evaluator/input/'

STATUS_CODES = {
    200: 'OK',
    201: 'CORRECT ANSWER',
    400: 'WRONG ANSWER',
    401: 'COMPILATION ERROR',
    402: 'RUNTIME ERROR',
    403: 'INVALID FILE',
    404: 'FILE NOT FOUND',
    408: 'TIME LIMIT EXCEEDED'
}

def code_evaluator(prof_code, student_code, input, time_limit):

    # run professor code
    prof_prog = Program(prof_code, input, 'professor_output', time_limit)
    prof_prog.preprocess_path()

    prof_prog.compile()
    prof_prog.run()


    # run student code
    new_prog = Program(student_code, input, 'professor_output', time_limit)
    new_prog.preprocess_path()

    compile_code = new_prog.compile()
    if compile_code[0] != 200:
        print("compile error of professor code: ", compile_code)
        return compile_code

    excute_code = new_prog.run()
    if excute_code[0] != 200:
        print("runtime error of professor code: ", excute_code)
        return excute_code

    # compare
    compare_code = match(prof_prog.expected_output_path, new_prog.expected_output_path)
    print(compare_code)


class StrEnum(str, Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name



class ProgrammingLanguage(StrEnum):
    unknown = auto()
    cpp = auto()
    c = auto()



class Program:
    def __init__(self, source_path, input_path, expected_output_path, timelimit):
        self.source_path = source_path
        self.executable_path = ''
        self.input_path  = input_path
        self.expected_output_path = expected_output_path
        self.language    = ProgrammingLanguage.c
        self.file_name   = ''
        self.timelimit   = timelimit



    def preprocess_path(self):

        if self.source_path[0] != '/':
            self.source_path = SOURCE_PATH_PREFIX + self.source_path
        if self.input_path != '/':
            self.input_path = INPUT_PATH_PREFIX + self.input_path
        if self.expected_output_path != '/':
            self.expected_output_path = EXPECTED_OUTPUT_PATH_PREFIX + self.expected_output_path

        self.executable_path = EXECUTABLE_PATH_PREFIX + Path(self.source_path).stem


        if not os.path.exists(self.input_path):
            print(self.input_path, "doesn't exist")
            return 403, STATUS_CODES[403]

        # if not os.path.exists(self.expected_output_path):
        #     print(self.expected_output_path, "doesn't exist")
        #     return 403


    def compile(self):

        # Remove previous executables
        if os.path.isfile(self.executable_path):
            os.remove(self.executable_path)


        if not os.path.exists(self.source_path):
            # print(self.source_path, "doesn't exist")
            return 403,  STATUS_CODES[403]
        self.language = os.path.splitext(self.source_path)[-1][1:]


        if self.language == ProgrammingLanguage.c:
            proc = subprocess.run(['gcc', self.source_path, '-o', self.executable_path], stderr=subprocess.PIPE)
        elif self.language == ProgrammingLanguage.cpp:
            proc = subprocess.run(['g++', self.source_path, '-o', self.executable_path], stderr=subprocess.PIPE)

        # Check for errors
        if proc.returncode != 0:
            return 401, proc.stderr
        else:
            return 200, STATUS_CODES[200]



    def run(self):
        if not os.path.exists(self.executable_path):
            return 403, self.executable_path + " doesn't exist"
        try:
            with open(self.expected_output_path, 'w') as fout:
                fin = None
                if self.input_path and os.path.isfile(self.input_path):
                    fin = open(self.input_path, 'r')
                proc = subprocess.run(
                    self.executable_path,
                    stdin=fin,
                    stdout=fout,
                    stderr=subprocess.PIPE,
                    timeout=self.timelimit,
                    universal_newlines=True
                )

            # Check for errors
            if proc.returncode != 0:
                return 402, proc.stderr
            else:
                return 200, STATUS_CODES[200]

        except subprocess.TimeoutExpired as tle:
            return 408, tle
        except subprocess.CalledProcessError as e:
            print(e.output)

        # Perform cleanup
        os.remove(self.executable_path)


def match(expected_output_file, actual_outputFile):
    if os.path.isfile(actual_outputFile) and os.path.isfile(expected_output_file):
        result = filecmp.cmp(actual_outputFile, expected_output_file)
        if result:
            return 201, STATUS_CODES[201]
        else:
            return 400, STATUS_CODES[400]
    else:
        return 404, STATUS_CODES[404]


# main
code_evaluator("instructor.cpp", "student.cpp", "test_input",3)
