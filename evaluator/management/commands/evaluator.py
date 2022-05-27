import yaml

from program import *
from utils import ordered_yaml

class Evaluator:

    def __init__(self, config_path):
        self.config_path = config_path
        self.config_dict = None

        self.result_dict = {
            'config_path': self.config_path
        }

        with open(config_path) as fp:
            yaml_loader, _ = ordered_yaml()
            self.config_dict = yaml.load(fp, Loader=yaml_loader)

    def evaluate_code(self, prof_code, student_code, input_case):

        # run professor code
        prof_prog = Program(prof_code,
                                    input_case,
                                    self.config_dict['expectedOutputPath'],
                                    self.config_dict['timelimit']
                                    )

        prof_prog.preprocess_path()
        prof_prog.compile()
        prof_prog.run()

        # run student code
        new_prog = Program(student_code,
                                   input_case,
                                   self.config_dict['expectedOutputPath'],
                                   self.config_dict['timelimit'])
        new_prog.preprocess_path()
        self.result_dict['compile_code'] = new_prog.compile()
        if self.result_dict['compile_code'][0] != 200:
            return

        self.result_dict['execute_code'] = new_prog.run()
        if self.result_dict['execute_code'][0] != 200:
            return

        # compare
        self.result_dict['compare_code'] = match(prof_prog.expected_output_path, new_prog.expected_output_path)

        if self.result_dict['compare_code'][0] == 200:
            if self.config_dict['parseCheck']['FuncDef']:
                print("TODO")



if __name__ == '__main__':
    evaluator = Evaluator("/home/ubuntu/code_evaluator/config.yml")
    evaluator.evaluate_code("professor.cpp", "student.cpp", "input")