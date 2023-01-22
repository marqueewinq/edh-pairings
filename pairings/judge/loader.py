import typing as ty

from judge.versions import judge_versions
from judge.versions.interfaces import Judge as AbstractJudge

legacy_to_modern_version = {
    "v1": "soft_random",
    "v2": "deterministic",
}


def get_available_version_choices() -> ty.Iterable[ty.Tuple[str, str]]:
    return tuple((version, version) for version in judge_versions)


def get_judge_class(version: ty.Optional[str] = None) -> ty.Type[AbstractJudge]:
    from constance import config

    if version in judge_versions:
        return judge_versions[version]
    if version in legacy_to_modern_version:
        return judge_versions[legacy_to_modern_version[version]]
    return judge_versions[config.JUDGE_VERSION]


def Judge(config) -> AbstractJudge:
    klass = get_judge_class(version=config["judge_version"])
    return klass(config)  # type: ignore
