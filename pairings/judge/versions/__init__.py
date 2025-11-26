from .pure_random import Judge as Judge_pure_random
from .v1 import Judge as Judge_v1
from .v2 import Judge as Judge_v2

judge_versions = {
    "soft_random": Judge_v1,
    "deterministic": Judge_v2,
    "pure_random": Judge_pure_random,
}

__all__ = [
    "judge_versions",
]
