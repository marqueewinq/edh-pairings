import marshmallow as ma
from judge import JudgeSchema


class TournamentSettingsSchema(ma.Schema):
    round_timer_enabled = ma.fields.Boolean(load_default=False)
    round_timer_duration_minutes = ma.fields.Int(load_default=30)

    judge_config = ma.fields.Nested(
        JudgeSchema, load_default=lambda: JudgeSchema().load({})
    )
