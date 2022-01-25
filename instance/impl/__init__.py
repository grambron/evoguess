from .cipher import *
from .instance import *
from .ilp_instance import *

instances = {
    Instance.slug: Instance,
    IlpInstance.slug: IlpInstance,
    StreamCipher.slug: StreamCipher
}

__all__ = [
    'Instance',
    'StreamCipher'
]
