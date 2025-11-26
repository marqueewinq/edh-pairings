from copy import deepcopy as copy

import numpy as np
from django.test import TestCase
from judge.versions import judge_versions
from judge.versions.schemas import PodSchema, RoundSchema
from judge.versions.v1 import Judge


class JudgeIntegrationTestCase(TestCase):
    def setUp(self):
        self.players = [
            "Albert",
            "Bob",
            "Cathy",
            "Danny",
            "Eve",
            "Fred",
            "George",
            "Harry",
            "Iffy",
            "Jack",
        ]
        self.late_comers = [
            "Kay",
            "Lena",
        ]

    def assertDictNotEqual(self, one, other, message=None):
        with self.assertRaises(AssertionError):
            print(message)
            self.assertDictEqual(one, other)

    def _validate_all_rounds_before_late_comers(self, rnd):
        player_name_list = self.players

        RoundSchema().load(rnd)  # assert schema validates
        self.assertEqual(2, len(rnd["buys"]))
        for player_name in rnd["buys"]:
            self.assertIn(player_name, player_name_list)
        for pod in rnd["pods"]:
            PodSchema().load(pod)  # assert schema validates
            for player_name in pod["players"]:
                self.assertIn(player_name, player_name_list)

    def _validate_all_rounds_after_late_comers(self, rnd):
        player_name_list = self.players + self.late_comers

        RoundSchema().load(rnd)  # assert schema validates
        self.assertEqual(0, len(rnd["buys"]))
        for pod in rnd["pods"]:
            PodSchema().load(pod)  # assert schema validates
            for player_name in pod["players"]:
                self.assertIn(player_name, player_name_list)

    def _validate_all_rounds_after_late_comers_and_drops(self, rnd, dropped):
        player_name_list = self.players + self.late_comers

        RoundSchema().load(rnd)  # assert schema validates
        self.assertEqual(4, len(rnd["buys"]))

        n_found_in_dropped = 0
        n_found_not_in_dropped = 0
        for player_name in rnd["buys"]:
            self.assertIn(player_name, player_name_list)
            if player_name in dropped:
                n_found_in_dropped += 1
            else:
                n_found_not_in_dropped += 1
        self.assertEqual(2, n_found_in_dropped)
        self.assertEqual(2, n_found_not_in_dropped)

        for pod in rnd["pods"]:
            PodSchema().load(pod)  # assert schema validates
            for player_name in pod["players"]:
                self.assertIn(player_name, player_name_list)

        self.assertEqual(sorted(dropped), sorted(rnd["drop"]))

    def _play_all_games_for_round_id(self, data, judge, round_id):
        win_primary_score = judge.config["win_primary_score"]
        loss_primary_score = judge.config["loss_primary_score"]

        winner_list = []
        for pod in data[round_id]["pods"]:
            winner = np.random.choice(pod["players"])
            winner_list.append(winner)

            # use name length for secondary score
            scores = {
                player_name: [win_primary_score, len(player_name)]
                if player_name == winner
                else [loss_primary_score, len(player_name)]
                for player_name in pod["players"]
            }
            for player_name, score in scores.items():
                data = judge.update_result(
                    data, player_name=player_name, round_id=round_id, score=score
                )

        return data, winner_list

    def _run_integration_test_for(self, judge):
        win_primary_score = judge.config["win_primary_score"]
        loss_primary_score = judge.config["loss_primary_score"]
        buy_primary_score = judge.config["buy_primary_score"]
        buy_secondary_score = judge.config["buy_secondary_score"]

        # create first round
        data = judge.new_round(None, self.players)
        self.assertEqual(1, len(data))
        self._validate_all_rounds_before_late_comers(data[0])

        rounds_info = judge.get_rounds(data)
        self.assertEqual(1, rounds_info["n_rounds"])
        self.assertEqual(1, len(rounds_info["rounds"]))
        self.assertDictEqual(data[0], rounds_info["rounds"][0])

        # redo first round
        data_redone = judge.redo_last_round(data, self.players)
        self.assertEqual(1, len(data_redone))
        self._validate_all_rounds_before_late_comers(data_redone[0])
        self.assertDictNotEqual(data_redone, data)  # assert redo is different

        # play round 0
        for _ in range(3):
            # loop to assert repeated updates are not cumulative
            data, winner_list = self._play_all_games_for_round_id(
                data, judge, round_id=0
            )

        # validate standings after round 0
        standings = judge.get_standings(data)
        buyed_players = data[0]["buys"]
        self.assertEqual(len(self.players), len(standings))
        for idx in range(0, 2):
            item = standings[idx]

            self.assertIn(item["player_name"], winner_list)
            self.assertEqual(
                item["total_score"], (win_primary_score, len(item["player_name"]))
            )
        for item in standings[2:]:
            player_name = item["player_name"]
            total_score = item["total_score"]
            self.assertNotIn(player_name, winner_list)
            if player_name in buyed_players:
                self.assertEqual(total_score, (buy_primary_score, buy_secondary_score))
            else:
                self.assertEqual(total_score, (loss_primary_score, len(player_name)))

        data = judge.new_round(data, self.players)
        self.assertEqual(2, len(data))
        self._validate_all_rounds_before_late_comers(data[1])
        data_redone = judge.redo_last_round(data, self.players)
        self.assertEqual(2, len(data_redone))
        self._validate_all_rounds_before_late_comers(data_redone[1])
        self.assertDictNotEqual(data_redone, data)  # assert redo is different

        rounds_info = judge.get_rounds(data)
        self.assertEqual(2, rounds_info["n_rounds"])
        self.assertEqual(2, len(rounds_info["rounds"]))

        data, _ = self._play_all_games_for_round_id(data, judge, round_id=1)
        judge.get_standings(data)  # assert does not fail

        for player_name in self.late_comers:
            data = judge.player_set_all_buys(data, player_name)

        standings = judge.get_standings(data)
        n_found = 0
        for item in standings:
            if item["player_name"] in self.late_comers:
                # buys for 2x rounds
                self.assertEqual(
                    item["total_score"],
                    (2 * buy_primary_score, 2 * buy_secondary_score),
                )
                n_found += 1
        self.assertEqual(2, n_found, standings)

        data = judge.new_round(data, self.players + self.late_comers)
        data, _ = self._play_all_games_for_round_id(data, judge, round_id=2)
        self._validate_all_rounds_after_late_comers(data[2])

        # drop somebody
        dropped_01 = np.random.choice(self.players)
        dropped_02 = np.random.choice(self.late_comers)
        for dropped in [dropped_01, dropped_02]:
            data = judge.drop_player_from_tournament(data, dropped)

        data = judge.new_round(data, self.players + self.late_comers)
        data, _ = self._play_all_games_for_round_id(data, judge, round_id=3)

        self._validate_all_rounds_after_late_comers_and_drops(
            data[3], [dropped_01, dropped_02]
        )

    def test_integration_test(self):
        for version in judge_versions:
            judge_class = judge_versions[version]
            judge = judge_class(config={})

            self._run_integration_test_for(judge)


class JudgeV1UnitTestCase(TestCase):
    def setUp(self):
        self.judge = Judge(config={})

    def test_new_round_random(self):
        data = [
            {
                "pods": [
                    {
                        "players": ["Albert", "Fred", "George", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Zyra", "Sheldon", "Iffy"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                ],
                "buys": ["Leona"],
            },
            {
                "pods": [
                    {
                        "players": ["Albert", "Zyra", "Iffy", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Fred", "Sheldon", "Leona"],
                        "scores": [[1, 1], [1, 2], [1, 3], [1, 4]],
                    },
                ],
                "buys": ["George"],
            },
        ]
        new_data = self.judge.new_round_random(
            data,
            [
                "Albert",
                "Fred",
                "George",
                "Sexton",
                "Lily",
                "Zyra",
                "Sheldon",
                "Iffy",
                "Leona",
            ],
        )

        assert len(new_data) == 3
        assert len(new_data[2]["pods"]) == 2
        self.assertDictEqual(
            self.judge.get_standings(new_data)[0], self.judge.get_standings(data)[0]
        )
        assert len(new_data[2]["buys"]) == 1

    def test_get_probability_mat_for_players(self):
        score_list = [2, 2, 2, 2]
        mat = self.judge._get_probability_mat_for_players(score_list)
        for idx in range(len(score_list)):
            assert mat[idx][idx] == 0, mat

    def test_new_round_prob(self):
        np.printoptions(precision=2)
        data = [
            {
                "pods": [
                    {
                        "players": ["Albert", "Fred", "George", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Zyra", "Sheldon", "Iffy"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                ],
                "buys": ["Leona"],
            },
            {
                "pods": [
                    {
                        "players": ["Albert", "Zyra", "Iffy", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Fred", "Sheldon", "Leona"],
                        "scores": [[1, 1], [1, 2], [1, 3], [1, 4]],
                    },
                ],
                "buys": ["George"],
            },
        ]
        for _ in range(10):
            new_data = self.judge.new_round_with_history(copy(data))
            assert len(new_data) == 3
            assert len(new_data[2]["pods"]) == 2
            assert "Sexton" in new_data[2]["pods"][0]["players"]
            assert "Sexton" not in new_data[2]["buys"]
            assert "Iffy" not in new_data[2]["buys"]

    def test_get_pods(self):
        score_list = [1, 2, 300, 400, 500, 600]
        pods = self.judge.get_pods(score_list)
        assert len(pods) == 1
        assert 5 in pods[0]

        score_list = [1, 1, 1, 1, 1]
        pods = self.judge.get_pods(score_list)
        assert len(pods) == 1

    def test_get_pods_with_exclude(self):
        score_list = [1, 2, 300, 400, 500, 600]
        pods = self.judge.get_pods(score_list, exclude_list=[4, 5])
        assert len(pods) == 1
        assert 5 not in pods[0]
        assert 4 not in pods[0]
        assert 3 in pods[0]

    def test_redo_last_round(self):
        data = [
            {
                "pods": [
                    {
                        "players": ["Albert", "Fred", "George", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Zyra", "Sheldon", "Iffy"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                ],
                "buys": ["Leona"],
                "drop": [],
            },
            {
                "pods": [
                    {
                        "players": ["Albert", "Zyra", "Iffy", "Sexton"],
                        "scores": [[0, 1], [0, 2], [0, 3], [3, 4]],
                    },
                    {
                        "players": ["Lily", "Fred", "Sheldon", "Leona"],
                        "scores": [[1, 1], [1, 2], [1, 3], [1, 4]],
                    },
                ],
                "buys": ["George"],
                "drop": ["George"],
            },
        ]
        new_data = self.judge.redo_last_round(
            data,
            [
                "Albert",
                "Fred",
                "George",
                "Sexton",
                "Lily",
                "Zyra",
                "Sheldon",
                "Iffy",
                "Leona",
            ],
        )

        assert new_data[-1]["drop"] == ["George"]
        assert new_data[-1]["buys"] == ["George"]
