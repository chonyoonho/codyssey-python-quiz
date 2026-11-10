"""퀴즈 게임 전체를 관리하는 QuizGame 클래스."""

import json
import os
import random
from datetime import datetime
from pathlib import Path

from default_quizzes import create_default_quizzes
from input_utils import read_int, read_text
from quiz import Quiz

# 데이터 파일 위치: 프로젝트 루트(이 파일이 있는 폴더)의 state.json
STATE_FILE = Path(__file__).resolve().parent / "state.json"


class QuizGame:
    """퀴즈 목록과 최고 점수를 관리하고, 메뉴에 따라 기능을 실행하는 게임 클래스.

    속성:
        quizzes:    Quiz 객체 리스트
        best_score: 최고 점수 (100점 만점, 아직 안 풀었으면 None)
        history:    지금까지 푼 모든 게임 기록 (딕셔너리 리스트, 오래된 것이 앞)
    """

    EXIT_MENU = 5
    HINT_CREDIT = 0.5  # 힌트를 쓰고 맞힌 문제가 인정받는 비율 (0.5 = 절반)
    HISTORY_VIEW_COUNT = 5  # 점수 확인 화면에서 보여 줄 최근 기록 수
    HISTORY_KEYS = ("played_at", "total", "correct", "hints_used", "score")

    def __init__(self, state_path=STATE_FILE, rng=None, clock=None):
        self.state_path = Path(state_path)
        # rng, clock: 무작위 도구와 현재 시각. 테스트할 때 정해진 값을 쓰려고 바꿀 수 있게 했다.
        self.rng = rng if rng is not None else random.Random()
        self.clock = clock if clock is not None else datetime.now
        self.quizzes = []
        self.best_score = None
        self.history = []
        self.load_state()

    # ------------------------------------------------------------------
    # 파일 저장 / 불러오기 (state.json)
    # ------------------------------------------------------------------
    def reset_to_default(self):
        """기본 퀴즈와 '점수 없음' 상태로 되돌린다."""
        self.quizzes = create_default_quizzes()
        self.best_score = None
        self.history = []

    @staticmethod
    def is_int(value):
        """정수인지 검사한다. (True/False는 파이썬에서 정수로 취급되므로 따로 제외)"""
        return isinstance(value, int) and not isinstance(value, bool)

    @classmethod
    def check_history_item(cls, item):
        """게임 기록 한 건의 형식을 검사한다. 잘못되었으면 ValueError."""
        if not isinstance(item, dict):
            raise ValueError("history 항목이 딕셔너리 형식이 아닙니다.")

        played_at = item.get("played_at")
        total = item.get("total")
        correct = item.get("correct")
        hints_used = item.get("hints_used")
        score = item.get("score")

        if not isinstance(played_at, str) or not played_at.strip():
            raise ValueError("history의 played_at(날짜/시간)이 올바르지 않습니다.")
        if not (cls.is_int(total) and total >= 1):
            raise ValueError("history의 total(푼 문제 수)이 올바르지 않습니다.")
        if not (cls.is_int(correct) and 0 <= correct <= total):
            raise ValueError("history의 correct(정답 수)가 올바르지 않습니다.")
        if not (cls.is_int(hints_used) and 0 <= hints_used <= total):
            raise ValueError("history의 hints_used(힌트 사용 수)가 올바르지 않습니다.")
        if not (cls.is_int(score) and 0 <= score <= 100):
            raise ValueError("history의 score(점수)는 0~100 사이의 정수여야 합니다.")

    def apply_state(self, data):
        """파일에서 읽은 데이터를 검사한 뒤 게임에 반영한다.

        형식이 잘못되었으면 ValueError를 일으키고, 이 경우 게임 상태는 바뀌지 않는다.
        """
        if not isinstance(data, dict):
            raise ValueError("최상위 데이터가 딕셔너리 형식이 아닙니다.")

        raw_quizzes = data.get("quizzes")
        if not isinstance(raw_quizzes, list):
            raise ValueError("quizzes 항목이 리스트가 아닙니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]

        best_score = data.get("best_score")
        if best_score is not None and (
            isinstance(best_score, bool)
            or not isinstance(best_score, int)
            or not 0 <= best_score <= 100
        ):
            raise ValueError("best_score는 0~100 사이의 정수 또는 null이어야 합니다.")

        # history는 나중에 추가된 항목이라, 없는 옛 파일은 빈 기록으로 취급한다.
        raw_history = data.get("history", [])
        if not isinstance(raw_history, list):
            raise ValueError("history 항목이 리스트가 아닙니다.")
        for item in raw_history:
            self.check_history_item(item)

        self.quizzes = quizzes
        self.best_score = best_score
        self.history = [
            {key: item[key] for key in self.HISTORY_KEYS} for item in raw_history
        ]

    def load_state(self):
        """state.json을 불러온다.

        - 파일이 없으면(첫 실행) 기본 퀴즈로 시작한다.
        - 파일이 손상되었거나 읽을 수 없으면 안내 후 기본 데이터로 복구한다.
        """
        if not self.state_path.exists():
            print("저장된 데이터가 없어 기본 퀴즈로 시작합니다.")
            self.reset_to_default()
            return

        try:
            with open(self.state_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.apply_state(data)
            best = f"{self.best_score}점" if self.best_score is not None else "없음"
            print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고 점수 {best})")
        except (OSError, ValueError) as error:
            # JSONDecodeError, UnicodeDecodeError는 ValueError의 한 종류이다.
            print(f"저장 파일을 읽을 수 없습니다. ({error})")
            print("기본 퀴즈 데이터로 복구하여 시작합니다.")
            self.backup_broken_file()
            self.reset_to_default()
            self.save_state()

    def backup_broken_file(self):
        """손상된 파일을 지우지 않고 state.json.broken 이름으로 옮겨 둔다."""
        backup_path = self.state_path.with_name(self.state_path.name + ".broken")
        try:
            os.replace(self.state_path, backup_path)
            print(f"손상된 파일은 {backup_path.name} 으로 보관했습니다.")
        except OSError:
            pass  # 옮기지 못해도 게임 진행에는 문제가 없다.

    def save_state(self):
        """퀴즈 목록, 최고 점수, 게임 기록을 state.json에 UTF-8로 저장한다. 성공하면 True."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        temp_path = self.state_path.with_name(self.state_path.name + ".tmp")
        try:
            # 임시 파일에 먼저 쓰고 교체하면, 쓰는 도중 꺼져도 기존 파일이 안전하다.
            with open(temp_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.state_path)
            return True
        except OSError as error:
            print(f"  ! 저장 중 오류가 발생했습니다: {error}")
            return False

    def show_menu(self):
        print("\n" + "=" * 36)
        print("     AI·업무 자동화 퀴즈 게임")
        print("=" * 36)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록 / 삭제")
        print("4. 점수 확인")
        print("5. 종료")
        print("-" * 36)

    def choose_quiz_count(self):
        """이번에 풀 문제 수를 고르게 한다. 퀴즈가 1개뿐이면 묻지 않고 1을 돌려준다."""
        available = len(self.quizzes)
        if available == 1:
            return 1
        return read_int(f"풀 문제 수를 선택하세요 (1~{available}): ", 1, available)

    def play_quiz(self):
        """퀴즈를 무작위 순서로 출제하고, 정답/오답 여부를 알려 준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록해 주세요.")
            return

        total = self.choose_quiz_count()
        # sample: 전체에서 total개를 겹치지 않게 뽑는다. 뽑힌 순서가 곧 출제 순서(무작위)이다.
        selected = self.rng.sample(self.quizzes, total)
        correct = 0  # 맞힌 문제 수
        hints_used = 0  # 힌트를 본 문제 수
        earned = 0.0  # 인정받은 점수 (문제당 최대 1점, 힌트를 쓰고 맞히면 0.5점)
        print(f"\n퀴즈를 시작합니다! 총 {total}문제입니다. (문제 순서는 무작위)")
        for number, quiz in enumerate(selected, start=1):
            quiz.display(number)
            user_answer, used_hint = self.ask_answer(quiz)
            if used_hint:
                hints_used += 1
            if quiz.is_correct(user_answer):
                correct += 1
                earned += self.HINT_CREDIT if used_hint else 1
                note = " (힌트를 써서 절반 점수)" if used_hint else ""
                print(f"  [정답] 맞았습니다!{note}")
            else:
                print(f"  [오답] 아쉽네요. 정답은 {quiz.answer_text()} 입니다.")

        self.show_result(correct, total, earned, hints_used)

    def ask_answer(self, quiz):
        """정답 번호를 입력받는다. 힌트가 있는 문제는 h를 입력해 힌트를 볼 수 있다.

        (정답 번호, 힌트를 봤는지 여부)를 돌려준다.
        """
        if quiz.hint:
            prompt = f"정답 번호 (1~{Quiz.CHOICE_COUNT}, 힌트 보기: h): "
            commands = ("h",)
        else:
            prompt = f"정답 번호 (1~{Quiz.CHOICE_COUNT}): "
            commands = ()

        used_hint = False
        while True:
            answer = read_int(prompt, 1, Quiz.CHOICE_COUNT, commands)
            if answer != "h":
                return answer, used_hint
            print(f"  [힌트] {quiz.hint}")
            if not used_hint:
                percent = int(self.HINT_CREDIT * 100)
                print(f"  (힌트를 쓰면 이 문제는 맞혀도 {percent}%만 점수로 인정됩니다.)")
            used_hint = True

    @staticmethod
    def calculate_score(earned, total):
        """인정받은 점수를 100점 만점으로 바꾼다. (예: 8문제 중 6개 -> 75점)

        earned는 정답 수와 같은 단위이다. 힌트를 쓰고 맞힌 문제는 0.5로 계산해 넘긴다.
        """
        return round(earned / total * 100)

    def show_result(self, correct, total, earned, hints_used):
        """모든 문제를 푼 뒤 결과를 보여 준다."""
        score = self.calculate_score(earned, total)
        print("\n" + "-" * 36)
        print(f"결과: {total}문제 중 {correct}문제 정답")
        if hints_used:
            print(f"힌트 사용: {hints_used}회 (힌트를 쓴 문제는 절반 점수)")
        print(f"이번 점수: {score}점 (100점 만점)")
        if self.update_best_score(score):
            print("새로운 최고 점수입니다! 축하합니다!")
        else:
            print(f"현재 최고 점수는 {self.best_score}점입니다.")
        print("-" * 36)

        self.record_game(total, correct, hints_used, score)
        self.save_state()

    def record_game(self, total, correct, hints_used, score):
        """이번 게임의 날짜/시간, 푼 문제 수, 정답 수, 힌트 사용 수, 점수를 기록에 남긴다."""
        self.history.append(
            {
                "played_at": self.clock().strftime("%Y-%m-%d %H:%M:%S"),
                "total": total,
                "correct": correct,
                "hints_used": hints_used,
                "score": score,
            }
        )

    def update_best_score(self, score):
        """이번 점수가 최고 점수보다 높으면 갱신하고 True를 돌려준다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            return True
        return False

    def show_score(self):
        """최고 점수와 최근 풀이 기록을 보여 준다. 아직 퀴즈를 풀지 않았다면 안내한다."""
        if self.best_score is None:
            print("\n아직 퀴즈를 풀지 않았습니다. '퀴즈 풀기'에 도전해 보세요!")
            return

        detail = ""
        for record in self.history:  # 최고 점수를 처음 받은 게임의 정답 수를 함께 보여 준다.
            if record["score"] == self.best_score:
                detail = f" ({record['total']}문제 중 {record['correct']}문제 정답)"
                break
        print(f"\n최고 점수: {self.best_score}점{detail}")
        self.show_history()

    def show_history(self):
        """최근 풀이 기록을 최신순으로 보여 준다. 기록이 없으면 아무것도 출력하지 않는다."""
        if not self.history:
            return

        recent = self.history[-self.HISTORY_VIEW_COUNT :]
        print(f"\n--- 최근 풀이 기록 (최근 {len(recent)}회 / 전체 {len(self.history)}회) ---")
        for record in reversed(recent):
            hint_note = f", 힌트 {record['hints_used']}회" if record["hints_used"] else ""
            print(
                f"{record['played_at']}  "
                f"{record['total']}문제 중 {record['correct']}문제 정답{hint_note} "
                f"-> {record['score']}점"
            )

    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
        print("\n--- 새 퀴즈 추가 ---")
        question = read_text("문제: ")
        choices = []
        for number in range(1, Quiz.CHOICE_COUNT + 1):
            choices.append(read_text(f"선택지 {number}: "))
        answer = read_int(
            f"정답 번호 (1~{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT
        )

        hint = read_text("힌트 (없으면 그냥 Enter): ", allow_empty=True)

        self.quizzes.append(Quiz(question, choices, answer, hint))
        print(f"퀴즈가 추가되었습니다. (현재 총 {len(self.quizzes)}개)")
        self.save_state()

    def show_quiz_list(self):
        """저장된 퀴즈를 번호와 함께 목록으로 보여 준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. '퀴즈 추가'로 새 퀴즈를 만들어 보세요.")
            return

        print(f"\n--- 퀴즈 목록 (총 {len(self.quizzes)}개) ---")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"{number}. {quiz.question}")
            print(f"   정답: {quiz.answer_text()}")
            if quiz.hint:
                print(f"   힌트: {quiz.hint}")

    def manage_quiz_list(self):
        """퀴즈 목록을 보여 준 뒤, 원하면 이어서 퀴즈를 삭제할 수 있게 한다."""
        self.show_quiz_list()
        if self.quizzes:
            self.delete_quiz()

    def delete_quiz(self):
        """삭제할 퀴즈 번호를 입력받아 지우고, 바로 파일에 반영한다."""
        count = len(self.quizzes)
        number = read_int(f"삭제할 퀴즈 번호 (1~{count}, 삭제하지 않으려면 0): ", 0, count)
        if number == 0:
            return

        quiz = self.quizzes[number - 1]
        print(f"삭제할 퀴즈: {quiz.question}")
        if read_int("정말 삭제할까요? (1: 삭제, 2: 취소): ", 1, 2) == 2:
            print("삭제를 취소했습니다.")
            return

        del self.quizzes[number - 1]
        print(f"퀴즈를 삭제했습니다. (남은 퀴즈 {len(self.quizzes)}개)")
        self.save_state()

    def menu_loop(self):
        """메뉴를 반복해서 보여 주고, 고른 번호의 기능을 실행한다. (종료는 5번)"""
        actions = {
            1: self.play_quiz,
            2: self.add_quiz,
            3: self.manage_quiz_list,
            4: self.show_score,
        }
        while True:
            self.show_menu()
            choice = read_int(f"메뉴 번호를 선택하세요 (1~{self.EXIT_MENU}): ", 1, self.EXIT_MENU)
            if choice == self.EXIT_MENU:
                return
            actions[choice]()

    def run(self):
        """프로그램을 시작한다.

        Ctrl+C(KeyboardInterrupt)나 입력 스트림 종료(EOFError)가 일어나도
        오류 화면 없이 안내 메시지를 보여 주고 안전하게 끝낸다.
        """
        try:
            self.menu_loop()
        except (KeyboardInterrupt, EOFError):
            print("\n\n입력이 중단되었습니다. 데이터를 저장하고 안전하게 종료합니다.")
        self.save_state()
        print("퀴즈 게임을 종료합니다. 안녕히 가세요!")
