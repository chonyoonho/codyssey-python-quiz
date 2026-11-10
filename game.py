"""퀴즈 게임 전체를 관리하는 QuizGame 클래스."""

from default_quizzes import create_default_quizzes
from input_utils import read_int, read_text
from quiz import Quiz


class QuizGame:
    """메뉴를 보여 주고, 사용자가 고른 기능을 실행하는 게임 클래스."""

    def __init__(self):
        self.quizzes = create_default_quizzes()
        self.best_score = None

    def show_menu(self):
        print("\n" + "=" * 36)
        print("     AI·업무 자동화 퀴즈 게임")
        print("=" * 36)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("-" * 36)

    def play_quiz(self):
        """저장된 퀴즈를 차례로 출제하고, 정답/오답 여부를 알려 준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 '퀴즈 추가'로 퀴즈를 등록해 주세요.")
            return

        total = len(self.quizzes)
        correct = 0
        print(f"\n퀴즈를 시작합니다! 총 {total}문제입니다.")
        for number, quiz in enumerate(self.quizzes, start=1):
            quiz.display(number)
            user_answer = read_int("정답 번호 (1~4): ", 1, Quiz.CHOICE_COUNT)
            if quiz.is_correct(user_answer):
                print("  [정답] 맞았습니다!")
                correct += 1
            else:
                print(f"  [오답] 아쉽네요. 정답은 {quiz.answer_text()} 입니다.")

        self.show_result(correct, total)

    @staticmethod
    def calculate_score(correct, total):
        """정답 수를 100점 만점 점수로 바꾼다. (예: 8문제 중 6개 -> 75점)"""
        return round(correct / total * 100)

    def show_result(self, correct, total):
        """모든 문제를 푼 뒤 결과를 보여 준다."""
        score = self.calculate_score(correct, total)
        print("\n" + "-" * 36)
        print(f"결과: {total}문제 중 {correct}문제 정답")
        print(f"이번 점수: {score}점 (100점 만점)")
        if self.update_best_score(score):
            print("새로운 최고 점수입니다! 축하합니다!")
        else:
            print(f"현재 최고 점수는 {self.best_score}점입니다.")
        print("-" * 36)

    def update_best_score(self, score):
        """이번 점수가 최고 점수보다 높으면 갱신하고 True를 돌려준다."""
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            return True
        return False

    def show_score(self):
        """최고 점수를 보여 준다. 아직 퀴즈를 풀지 않았다면 안내한다."""
        if self.best_score is None:
            print("\n아직 퀴즈를 풀지 않았습니다. '퀴즈 풀기'에 도전해 보세요!")
        else:
            print(f"\n최고 점수: {self.best_score}점 (100점 만점)")

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

        self.quizzes.append(Quiz(question, choices, answer))
        print(f"퀴즈가 추가되었습니다. (현재 총 {len(self.quizzes)}개)")

    def show_quiz_list(self):
        """저장된 퀴즈를 번호와 함께 목록으로 보여 준다."""
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. '퀴즈 추가'로 새 퀴즈를 만들어 보세요.")
            return

        print(f"\n--- 퀴즈 목록 (총 {len(self.quizzes)}개) ---")
        for number, quiz in enumerate(self.quizzes, start=1):
            print(f"{number}. {quiz.question}")
            print(f"   정답: {quiz.answer_text()}")

    def run(self):
        """프로그램을 시작한다. 종료(5)를 고를 때까지 메뉴를 반복한다."""
        while True:
            self.show_menu()
            choice = read_int("메뉴 번호를 선택하세요 (1~5): ", 1, 5)
            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_quiz_list()
            elif choice == 4:
                self.show_score()
            else:
                print("\n퀴즈 게임을 종료합니다. 안녕히 가세요!")
                break
