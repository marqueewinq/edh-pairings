import marshmallow as ma
from judge.loader import judge_versions


def lambda_factory(key):
    from constance import config

    return lambda: getattr(config, key)


class JudgeSchema(ma.Schema):
    # pairing judge config
    judge_version = ma.fields.String(
        load_default=lambda_factory("JUDGE_VERSION"), choices=judge_versions.keys()
    )
    judge_primary_weight = ma.fields.Float(
        load_default=lambda_factory("PRIMARY_WEIGHT")
    )
    judge_secondary_weight = ma.fields.Float(
        load_default=lambda_factory("SECONDARY_WEIGHT")
    )
    buy_primary_score = ma.fields.Int(
        load_default=lambda_factory("PRIMARY_SCORE_PER_BUY")
    )
    buy_secondary_score = ma.fields.Int(
        load_default=lambda_factory("SECONDARY_SCORE_PER_BUY")
    )

    # scores per result
    win_primary_score = ma.fields.Int(load_default=3)
    loss_primary_score = ma.fields.Int(load_default=0)
    tie_primary_score = ma.fields.Int(load_default=1)

    # common judge config
    shuffle_seats = ma.fields.Boolean(load_default=False)

    # version-specific judge config
    pass
