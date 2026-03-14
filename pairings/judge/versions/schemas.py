import marshmallow as ma


class PodSchema(ma.Schema):
    """
    Example:
    ```
    {
        "scores": [[3, 1], [0, 2], [0, 3], [0, 4]],
        "players": ["Jack", "Bob", "Eve", "Fred"],
    }
    ```
    """

    players = ma.fields.List(ma.fields.Str)
    scores = ma.fields.List(ma.fields.List(ma.fields.Int(allow_none=True)))

    @ma.validates("scores")
    def validate_scores(self, scores):
        length = None
        for score in scores:
            if length is None:
                length = len(score)
                continue
            if length != len(score):
                raise ma.ValidationError(f"All scores must have the same length, got {scores}")

    def validate(self, data):
        if len(data["players"]) != len(data["scores"]):
            raise ma.ValidationError(
                f"players length ({len(data['players'])}) != scores length ({len(data['scores'])})"
            )


class RoundSchema(ma.Schema):
    pods = ma.fields.Nested(PodSchema, many=True)
    buys = ma.fields.List(ma.fields.Str, required=False)
    drop = ma.fields.List(ma.fields.Str, required=False)

    def validate(self, data):
        pass
