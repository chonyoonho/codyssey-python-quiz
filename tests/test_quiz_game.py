"""퀴즈 게임 자동 테스트.  실행: python -m unittest discover -s tests -v"""

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# tests 폴더에서 실행해도 프로젝트 루트의 모듈을 불러올 수 있게 한다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game import QuizGame  # noqa: E402
from input_utils import read_int, read_text  # noqa: E402
from quiz import Quiz  # noqa: E402


def quiet(function, *args, **kwargs):
    """함수를 실행하되 화면 출력은 숨기고, (결과, 출력 내용)을 돌려준다."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = function(*args, **kwargs)
    return result, buffer.getvalue()


class QuizTest(unittest.TestCase):
    def test_is_correct(self):
        quiz = Quiz("문제", ["a", "b", "c", "d"], 2)
        self.assertTrue(quiz.is_correct(2))
        self.assertFalse(quiz.is_correct(3))

    def test_dict_round_trip(self):
        quiz = Quiz("문제", ["a", "b", "c", "d"], 4)
        copy = Quiz.from_dict(quiz.to_dict())
        self.assertEqual(
            (copy.question, copy.choices, copy.answer), (quiz.question, quiz.choices, 4)
        )

    def test_from_dict_rejects_bad_data(self):
        good_choices = ["a", "b", "c", "d"]
        bad_items = [
            None,
            {},
            {"question": "", "choices": good_choices, "answer": 1},
            {"question": "q", "choices": ["a", "b", "c"], "answer": 1},
            {"question": "q", "choices": good_choices, "answer": 0},
            {"question": "q", "choices": good_choices, "answer": 5},
            {"question": "q", "choices": good_choices, "answer": "2"},
            {"question": "q", "choices": good_choices, "answer": True},
        ]
        for item in bad_items:
            with self.subTest(item=item):
                with self.assertRaises(ValueError):
                    Quiz.from_dict(item)


class InputTest(unittest.TestCase):
    def test_read_int_retries_until_valid(self):
        # 빈 입력 -> 숫자 아님 -> 범위 밖 -> 공백 포함 정상 입력
        with mock.patch("builtins.input", side_effect=["", "abc", "9", " 3 "]):
            number, output = quiet(read_int, "> ", 1, 5)
        self.assertEqual(number, 3)
        self.assertEqual(output.count("!"), 3)  # 안내 메시지 3번

    def test_read_text_rejects_empty(self):
        with mock.patch("builtins.input", side_effect=["   ", "  안녕  "]):
            text, _ = quiet(read_text, "> ")
        self.assertEqual(text, "안녕")


class QuizGameTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "state.json"

    def new_game(self):
        game, _ = quiet(QuizGame, self.path)
        return game

    def test_first_run_uses_default_quizzes(self):
        game = self.new_game()
        self.assertGreaterEqual(len(game.quizzes), 5)
        self.assertIsNone(game.best_score)

    def test_data_persists_after_restart(self):
        game = self.new_game()
        game.quizzes.append(Quiz("새 문제", ["가", "나", "다", "라"], 3))
        game.update_best_score(75)
        quiet(game.save_state)

        again = self.new_game()
        self.assertEqual(again.quizzes[-1].question, "새 문제")
        self.assertEqual(again.best_score, 75)

    def test_saved_file_is_utf8_json(self):
        game = self.new_game()
        quiet(game.save_state)
        text = self.path.read_text(encoding="utf-8")
        data = json.loads(text)
        self.assertEqual(set(data), {"quizzes", "best_score"})
        self.assertIn("대규모 언어 모델", text)  # 한글이 \\u 코드가 아닌 글자로 저장됨

    def test_corrupted_file_is_recovered(self):
        broken_contents = [
            "{ not json",
            "[]",
            '{"quizzes": "x"}',
            '{"quizzes": [], "best_score": 150}',
        ]
        for contents in broken_contents:
            with self.subTest(contents=contents):
                self.path.write_text(contents, encoding="utf-8")
                game, output = quiet(QuizGame, self.path)
                self.assertIn("복구", output)
                self.assertGreaterEqual(len(game.quizzes), 5)

    def test_non_utf8_file_is_recovered(self):
        self.path.write_bytes(b"\xff\xfe\xfa")
        game, output = quiet(QuizGame, self.path)
        self.assertIn("복구", output)
        self.assertGreaterEqual(len(game.quizzes), 5)

    def test_best_score_only_goes_up(self):
        game = self.new_game()
        self.assertTrue(game.update_best_score(60))
        self.assertFalse(game.update_best_score(40))
        self.assertTrue(game.update_best_score(80))
        self.assertEqual(game.best_score, 80)

    def test_calculate_score(self):
        self.assertEqual(QuizGame.calculate_score(8, 8), 100)
        self.assertEqual(QuizGame.calculate_score(0, 8), 0)
        self.assertEqual(QuizGame.calculate_score(1, 3), 33)

    def test_play_with_no_quizzes(self):
        game = self.new_game()
        game.quizzes = []
        _, output = quiet(game.play_quiz)
        self.assertIn("등록된 퀴즈가 없습니다", output)
        _, output = quiet(game.show_quiz_list)
        self.assertIn("등록된 퀴즈가 없습니다", output)

    def test_score_before_playing(self):
        game = self.new_game()
        _, output = quiet(game.show_score)
        self.assertIn("아직 퀴즈를 풀지 않았습니다", output)

    def test_run_exits_safely_on_interrupt(self):
        game = self.new_game()
        for error in (KeyboardInterrupt, EOFError):
            with self.subTest(error=error.__name__):
                with mock.patch("builtins.input", side_effect=error):
                    _, output = quiet(game.run)
                self.assertIn("안전하게 종료", output)
        self.assertTrue(self.path.exists())  # 종료 전에 저장됨


class HintDataTest(unittest.TestCase):
    def test_hint_is_saved_in_dict(self):
        quiz = Quiz("문제", ["a", "b", "c", "d"], 1, "힌트 내용")
        self.assertEqual(quiz.to_dict()["hint"], "힌트 내용")
        self.assertEqual(Quiz.from_dict(quiz.to_dict()).hint, "힌트 내용")

    def test_old_data_without_hint_still_loads(self):
        old_format = {"question": "q", "choices": ["a", "b", "c", "d"], "answer": 2}
        self.assertEqual(Quiz.from_dict(old_format).hint, "")

    def test_non_string_hint_is_rejected(self):
        bad = {"question": "q", "choices": ["a", "b", "c", "d"], "answer": 2, "hint": 5}
        with self.assertRaises(ValueError):
            Quiz.from_dict(bad)

    def test_default_quizzes_have_hints(self):
        from default_quizzes import create_default_quizzes

        for quiz in create_default_quizzes():
            self.assertTrue(quiz.hint, quiz.question)

    def test_read_text_allow_empty(self):
        with mock.patch("builtins.input", side_effect=["   "]):
            text, _ = quiet(read_text, "> ", allow_empty=True)
        self.assertEqual(text, "")

    def test_add_quiz_with_and_without_hint(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        game, _ = quiet(QuizGame, Path(folder.name) / "state.json")
        count = len(game.quizzes)

        with mock.patch("builtins.input", side_effect=["Q1", "a", "b", "c", "d", "2", "힌트!"]):
            quiet(game.add_quiz)
        with mock.patch("builtins.input", side_effect=["Q2", "a", "b", "c", "d", "3", ""]):
            quiet(game.add_quiz)

        self.assertEqual(len(game.quizzes), count + 2)
        self.assertEqual(game.quizzes[-2].hint, "힌트!")
        self.assertEqual(game.quizzes[-1].hint, "")


class ReverseRng:
    """sample()이 항상 목록을 거꾸로 돌려주는 가짜 무작위 도구. (순서를 예측하려고 사용)"""

    def sample(self, population, k):
        return list(reversed(population))[:k]


class PlayOrderAndCountTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "state.json"

    def make_game(self, rng=None):
        game, _ = quiet(QuizGame, self.path, rng)
        # 정답이 모두 1번인 퀴즈 3개 (문제 이름: Q-A, Q-B, Q-C)
        game.quizzes = [
            Quiz(name, ["정답", "오답", "오답", "오답"], 1) for name in ("Q-A", "Q-B", "Q-C")
        ]
        return game

    def play(self, game, inputs):
        with mock.patch("builtins.input", side_effect=inputs):
            _, output = quiet(game.play_quiz)
        return output

    def test_questions_are_asked_in_random_order(self):
        game = self.make_game(rng=ReverseRng())
        output = self.play(game, ["3", "1", "1", "1"])
        self.assertLess(output.index("Q-C"), output.index("Q-B"))
        self.assertLess(output.index("Q-B"), output.index("Q-A"))

    def test_real_random_keeps_every_quiz_once(self):
        game = self.make_game()
        output = self.play(game, ["3", "1", "1", "1"])
        for name in ("Q-A", "Q-B", "Q-C"):
            self.assertEqual(output.count(name), 1)

    def test_player_can_choose_question_count(self):
        game = self.make_game()
        output = self.play(game, ["2", "1", "1"])
        self.assertIn("총 2문제", output)
        self.assertIn("2문제 중 2문제 정답", output)

    def test_count_input_is_validated(self):
        game = self.make_game()
        # 빈 입력, 문자, 0, 범위 초과(4)를 모두 거절한 뒤 1문제를 선택
        output = self.play(game, ["", "abc", "0", "4", "1", "1"])
        self.assertEqual(output.count("  ! "), 4)  # 경고 메시지(앞에 '  ! ')만 센다
        self.assertIn("총 1문제", output)

    def test_single_quiz_skips_count_question(self):
        game = self.make_game()
        game.quizzes = game.quizzes[:1]
        output = self.play(game, ["1"])
        self.assertNotIn("풀 문제 수", output)
        self.assertIn("총 1문제", output)


if __name__ == "__main__":
    unittest.main()
