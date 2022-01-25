from .gad import *
from .ilp_gad import *
from .ilp_gad import *
from .up_gad import *
from .incr_gad import *

functions = {
    GuessAndDetermine.slug: GuessAndDetermine,
    GuessAndDetermineILP.slug: GuessAndDetermineILP,
    UPGuessAndDetermine.slug: UPGuessAndDetermine,
    IncrGuessAndDetermine.slug: IncrGuessAndDetermine
}

__all__ = [
    'GuessAndDetermine',
    'GuessAndDetermineILP',
    'UPGuessAndDetermine'
]
