from program import *
from parser_driver import *
from utils import ordered_yaml
import json

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

    def evaluate_code(self, prof_code, student_code, input_cases):

        prof_prog = Program(prof_code,
                            self.config_dict['expectedOutputPath'],
                            self.config_dict['timelimit']
                            )

        prof_prog.preprocess_path()
        prof_prog.compile()

        # run student code
        new_prog = Program(student_code,
                           self.config_dict['expectedOutputPath'],
                           self.config_dict['timelimit'])
        new_prog.preprocess_path()

        self.result_dict['compile_code'] = new_prog.compile()
        if self.result_dict['compile_code'][0] != 200:
            return

        self.result_dict['execute_code'] = []
        self.result_dict['compare_code'] = []

        pass_all = 1
        for idx, input_case in enumerate(input_cases):
            # run professor code
            prof_prog.run(input_case)

            self.result_dict['execute_code'].append(new_prog.run(input_case))
            if self.result_dict['execute_code'][idx][0] != 200:
                self.result_dict['compare_code'].append(402)
                pass_all = 0
                return
            self.result_dict['compare_code'].append(
                match(prof_prog.expected_output_path, new_prog.expected_output_path))
            # compare
            # self.result_dict['compare_code'] = match(prof_prog.expected_output_path, new_prog.expected_output_path)


        # if self.result_dict['compare_code'][0] == 201:
        if pass_all:
            if self.config_dict['parseCheck']['FuncDef']:
                config = self.config_dict['FuncDefDetails']
                functions = zip(config['names'], config['return_types'], config['param_types'])
                self.result_dict['FuncDef'] = show_func_defs(new_prog.source_path, functions)

            if self.config_dict['parseCheck']['FuncCall']:
                config = self.config_dict['FuncCallDetails']
                self.result_dict['FuncCall'] = show_func_calls(new_prog.source_path, config['names'])

            if self.config_dict['parseCheck']['DeclDef']:
                config = self.config_dict['DeclDefDetails']
                self.result_dict['DeclDef'] = show_decl_defs(new_prog.source_path, config['names'])

if __name__ == '__main__':
    evaluator = Evaluator("/home/ubuntu/code_evaluator/config.yml")

    evaluator.evaluate_code("macro_example.c", "macro_example.c", ["test_input", "test_input1", "test_input2"])
    json_val = json.dumps(evaluator.result_dict)