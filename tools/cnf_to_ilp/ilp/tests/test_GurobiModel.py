import unittest

from tools.cnf_to_ilp.cnf_parser.Parser import parse, parse_backdoor
from tools.cnf_to_ilp.ilp.GurobiModel import GurobiModel
from tools.cnf_to_ilp.ilp.settings import GenerationMode

test_cases = [
    ['input/input1.txt', 'backdoors/backdoor1.txt', False],
    ['input/input2.txt', 'backdoors/backdoor2.txt', True],
    ['input/input3.txt', 'backdoors/backdoor3.txt', False],
    ['input/input4.txt', 'backdoors/backdoor4.txt', True],
    ['input/input5.txt', 'backdoors/backdoor5.txt', True],
    ['input/input6.txt', 'backdoors/backdoor6.txt', False],
    ['input/input7.txt', 'backdoors/backdoor7.txt', False],
    ['input/input8.txt', 'backdoors/backdoor8.txt', False],
    ['input/input9.txt', 'backdoors/backdoor9.txt', True]
]


class TestGurobiModel(unittest.TestCase):

    def test_model(self):
        for case in test_cases:
            input_file = case[0]
            backdoor = case[1]
            result = case[2]

            print(f"Testing {input_file}, {backdoor} -> {result}")
            self.base_test(input_file, backdoor, result)

    def base_test(self, cnf_file: str, backdoor_file: str, result: bool):
        cnf = parse(cnf_file)
        backdoor = parse_backdoor(backdoor_file)

        model = GurobiModel(cnf, backdoor)
        solution = model.resolve(GenerationMode.all)
        self.assertEqual(result, solution)

