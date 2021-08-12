from .._type.job import Job
from .._type.futures import MethodFuture, EstimationFuture

from util.bitmask import to_bit
from collections import namedtuple
from numpy.random import randint, RandomState

Cache = namedtuple('Cache', 'active canceled estimated')


class Context:
    def __init__(self, seeds, instance, backdoor, cache, **context):
        self.index = None
        self.cache = cache
        self.instance = instance
        self.backdoor = backdoor

        self.function = context.get('function')
        self.sampling = context.get('sampling')
        self.executor = context.get('executor')
        self.observer = context.get('observer')

        self.state = {
            **seeds,
            'base': backdoor.base,
            'size': len(backdoor),
            'power': backdoor.task_count(),
        }

        self.dim_type = to_bit(self.state['power'] > self.sampling.max_size)

    def _get_indexes(self):
        if self.index is None:
            if self.sampling.order == self.sampling.RANDOM:
                rs = RandomState(seed=self.state['list_seed'])
                self.index = rs.permutation(self.state['power'])
            elif self.sampling.order == self.sampling.DIRECT:
                self.index = list(range(self.state['power']))
            elif self.sampling.order == self.sampling.REVERSED:
                self.index = list(range(self.state['power']))[::-1]
        return self.index

    def get_tasks(self, cases, offset):
        count = self.sampling.get_count(self.backdoor, values=cases)
        if count == 0: return []

        if self.dim_type:
            value = self.state['list_seed']
            tasks = [(i, value + i) for i in range(offset, offset + count)]
        else:
            values = self._get_indexes()
            tasks = [(i, values[i]) for i in range(offset, offset + count)]

        return tasks

    def get_limits(self, values, offset):
        return 0, None

    def is_reasonably(self, futures, values):
        return True


class Method:
    slug = 'method'
    name = 'Method'

    def __init__(self, function, executor, sampling, observer, **kwargs):
        self.function = function
        self.executor = executor
        self.sampling = sampling
        self.observer = observer

        self._cache = Cache({}, {}, {})
        self.seed = kwargs.get('seed', randint(2 ** 32 - 1))
        self.random_state = RandomState(seed=self.seed)

    def queue(self, instance, backdoor):
        if backdoor in self._cache.active:
            return self._cache.active[backdoor]

        if backdoor in self._cache.canceled:
            _, estimation = self._cache.estimated[backdoor]
            return EstimationFuture(estimation)

        if backdoor in self._cache.estimated:
            _, estimation = self._cache.estimated[backdoor]
            return EstimationFuture(estimation)

        seeds = {
            'list_seed': self.random_state.randint(0, 2 ** 31),
            'func_seed': self.random_state.randint(0, 2 ** 32 - 1)
        }

        job = Job(Context(
            seeds,
            instance,
            backdoor,
            self._cache,
            function=self.function,
            sampling=self.sampling,
            executor=self.executor,
            observer=self.observer
        )).start()

        self._cache.active[backdoor] = MethodFuture(job)
        return self._cache.active[backdoor]

    def __info__(self):
        return {
            'slug': self.slug,
            'name': self.name,
            'seed': self.seed,
            'function': self.function.__info__(),
            'sampling': self.sampling.__info__(),
            'observer': self.observer.__info__()
        }

    def __str__(self):
        return self.name


__all__ = [
    'Method'
]
