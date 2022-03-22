from .._abc.function import *

from os import getpid
from time import time as now
from numpy.random.mtrand import RandomState
from math import log2


def gad_function_ilp(common_data, tasks_data=None):
    inst, slv, meas, info = common_data

    results = []
    bits = decode_bits(info)
    [dim_type, bd_type] = bits[:2]
    bd_base = to_number(bits[2:8], 6)
    mask_len = to_number(bits[8:24], 16)
    bd_mask = bits[24:mask_len + 24]

    backdoor = inst.get_backdoor2(bd_type, bd_base, bd_mask)
    bases = backdoor.get_bases()

    for task_data in tasks_data:
        st_timestamp = now()
        task_i, task_value = task_data

        if dim_type == NUMBERS:
            state = RandomState(seed=task_value)
            values = state.randint(0, bd_base, size=len(backdoor))
            # todo: apply backdoor.get_masks() to values
        else:
            values = decimal_to_base(task_value, bases)
            # todo: map values using backdoor.get_mappers()

        assumptions = inst.get_assumptions(backdoor, values)

        status, stats, _ = slv.solve(inst.clauses(), assumptions)
        time, value = stats['time'], meas.get(stats)
        results.append((task_i, getpid(), value, time, status, now() - st_timestamp))
    return results


class GuessAndDetermineILP(Function):
    type = 'gad_ilp'
    slug = 'function:gad_ilp'
    name = 'Function: Guess-and-Determine-ILP'

    def get_function(self):
        return gad_function_ilp

    def prepare_data(self, state, instance, backdoor, dim_type):
        if instance.has_intervals():
            # todo: add intervals bits to data
            pass

        bd_mask = instance.get_bd_mask(backdoor)
        return instance, self.solver, self.measure, encode_bits([
            *to_bits(dim_type, 1),
            *to_bits(backdoor.kind, 1),
            *to_bits(backdoor.base, 6),
            *to_bits(len(bd_mask), 16),
            *bd_mask
        ])

    def calculate(self, backdoor, *cases):
        statistic = {True: 0, False: 0, None: 0}
        process_time, time_sum, value_sum = 0, 0, 0

        for case in cases:
            time_sum += case[3]
            value_sum += case[2]
            process_time += case[5]
            statistic[case[4]] += 1

        time, value, = None, None
        count = backdoor.task_count()
        if count == len(cases):
            time, value = time_sum, value_sum
        elif len(cases) > 0:
            time = log2(float(time_sum) / len(cases)) + log2(count)
            value = log2(float(value_sum) / len(cases)) + log2(count)

        return {
            'time': time,
            'value': value,
            'count': len(cases),
            'statistic': statistic,
            'job_time': round(time_sum, 2),
            'job_value': round(value_sum, 2),
            'process_time': round(process_time, 2)
        }


__all__ = [
    'GuessAndDetermineILP'
]
