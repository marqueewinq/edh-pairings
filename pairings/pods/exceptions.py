from rest_framework import exceptions


class PlayerNameNotInTournamentError(exceptions.APIException):
    status_code = 409
    default_detail = "Specified player name is not in this tournament"
    default_code = "player_name_not_in_tournament_error"
