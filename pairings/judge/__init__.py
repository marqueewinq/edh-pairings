import typing as ty

from judge.interfaces import Judge as AbstractJudge
from judge.v1 import Judge as Judge_v1
from judge.v2 import Judge as Judge_v2

judge_versions = {"v1": Judge_v1, "v2": Judge_v2}


def get_available_version_choices() -> ty.Tuple[ty.Tuple[str, str], ty.Tuple[str, str]]:
    return (("v2", "v2"), ("v1", "v1"))


def get_judge_class(version: ty.Optional[str] = None) -> ty.Type[AbstractJudge]:
    if version is None:
        from constance import config

        version = config.JUDGE_VERSION
    try:
        return judge_versions[version]
    except KeyError as e:
        print(f"Not found judge version {e}, falling back to `v1`")
        return judge_versions["v1"]


def Judge(*args, **kwargs) -> AbstractJudge:
    klass = get_judge_class(*args, **kwargs)
    return klass()
