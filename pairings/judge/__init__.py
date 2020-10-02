from typing import Optional
from judge.v1 import Judge as Judge_v1
from judge.v2 import Judge as Judge_v2
from judge.interfaces import Judge as AbstractJudge

judge_versions = {"v1": Judge_v1, "v2": Judge_v2}


def get_available_version_choices():
    return (("v2", "v2"), ("v1", "v1"))


def get_judge_class(version: Optional[str] = None) -> AbstractJudge:
    if version is None:
        from constance import config

        version = config.JUDGE_VERSION
        print(f"version: {version}")

    try:
        return judge_versions[version]
    except KeyError as e:
        print(f"Not found judge version {e}, falling back to `v1`")
        return judge_versions["v1"]


def Judge(*args, **kwargs) -> AbstractJudge:
    klass = get_judge_class(*args, **kwargs)
    print(klass)
    return klass()
