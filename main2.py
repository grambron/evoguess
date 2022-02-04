import json

from util import build
from output import Output
from method import Method
from executor import Executor
from function import Function
from instance import Instance
from algorithm import Algorithm

if __name__ == '__main__':
    args = json.dumps({
        'algorithm': {
            'mu': 1, 'lmbda': 1,
            'size': 8, 'elites': 2,
            'slug': 'iterable:elitism',
            'limit': {
                'value': '00:00:10',
                'slug': 'limit:walltime',
            },
            'selection': {
                'slug': 'selection:roulette',
            },
            'mutation': {
                'slug': 'mutation:doer'
            },
            'crossover': {
                'slug': 'crossover:two-point'
            }
        },
        'output': {
            'slug': 'output:json',
            'path': 'test/ilp',
        },
        'instance': {
            'slug': 'ilp_instance',
            'ilp': {
                'slug': 'gurobi_ilp',
                'path': 'ilp/input.lp'
            },
            'supbs': {
                'slug': 'interval',
                'start': 1, 'length': 9
            },
            'input_set': {
                'slug': 'interval',
                'start': 1, 'length': 9
            }
        },
        'method': {
            'slug': 'method',
            'sampling': {
                'slug': 'sampling:const',
                'count': 100
            },
            'observer': {
                'slug': 'observer:timeout',
            }
        },
        'function': {
            'slug': 'function:gad_ilp',
            'solver': {
                'slug': 'solver:gurobi'
            },
            'measure': {
                'slug': 'measure:time'
            },
            'max_n': 30
        },
        'executor': {
            'workers': 4,
            'slug': 'executor:process',
            'shaping': {
                'slug': 'shaping:chunks',
                'chunk_rate': 4
            },
        },
        'backdoors': [
            {
                'slug': 'backdoor:base',
                # "_list": [132, 239, 355, 613, 620, 706, 1064, 1142, 1753, 1884, 2948, 2975]
            }
        ],
    })
    configuration = json.loads(args)

    _, algorithm = build(
        {Algorithm: [
            Output,
            Instance,
            {Method: [
                Function,
                Executor
            ]},
        ]}, **configuration
    )

    backdoors = [
        algorithm.instance.get_backdoor(**backdoor)
        for backdoor in configuration['backdoors']
    ]
    solution = algorithm.start(*backdoors)
