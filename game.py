"""퀴즈 게임 전체를 관리하는 QuizGame 클래스."""

from default_quizzes import create_default_quizzes
from input_utils import read_int


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

    def run(self):
        """프로그램을 시작한다. 종료(5)를 고를 때까지 메뉴를 반복한다."""
        while True:
            self.show_menu()
            choice = read_int("메뉴 번호를 선택하세요 (1~5): ", 1, 5)
            if choice == 1:
                print("\n[준비 중] 퀴즈 풀기 기능은 아직 만들어지지 않았습니다.")
            elif choice == 2:
                print("\n[준비 중] 퀴즈 추가 기능은 아직 만들어지지 않았습니다.")
            elif choice == 3:
                print("\n[준비 중] 퀴즈 목록 기능은 아직 만들어지지 않았습니다.")
            elif choice == 4:
                print("\n[준비 중] 점수 확인 기능은 아직 만들어지지 않았습니다.")
            else:
                print("\n퀴즈 게임을 종료합니다. 안녕히 가세요!")
                break
