"""퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """객관식 퀴즈 한 문제.

    속성:
        question: 문제 (문자열)
        choices:  선택지 4개 (문자열 리스트)
        answer:   정답 번호 (1~4 중 하나, 정수)
    """

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer

    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        title = f"Q{number}." if number is not None else "Q."
        print(f"\n{title} {self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}) {choice}")

    def is_correct(self, user_answer):
        """사용자가 입력한 번호가 정답이면 True, 아니면 False."""
        return user_answer == self.answer
