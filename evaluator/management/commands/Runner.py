import Program
from evaluator.models import Assignment


class Runner:
    def __init__(self, file_name):
        self.correct_code;
        self.test_case;
        self.expected_output;
        self.file_name;


    def run(self):

        # step 1 : 모델에서 교수님 코드랑 input 가져오기
        correct_code = Assignment.name
        test_case = Assignment.test_case


        # step 2 : 교수님 정답 코드 돌려서 expected output 생성
        Program.generateoutput(


        )

        # step 3: 학생 코드 돌려서 expected output이랑 비교 -> 결과 리턴
        Program.codechecker(
            filename=self.file_name,  # Source code file
            inputfile=self.test_case,  # Input file
            expectedoutput=self.expected_output,  # Expected output
            timeout=1,  # Time limit
            check=True  # Set to true to check actual output against expected output
        )


