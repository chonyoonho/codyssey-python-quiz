"""퀴즈 한 문제를 표현하는 Quiz 클래스."""


class Quiz:
    """객관식 퀴즈 한 문제.

    속성:
        question: 문제 (문자열)
        choices:  선택지 4개 (문자열 리스트)
        answer:   정답 번호 (1~4 중 하나, 정수)
        hint:     힌트 (문자열, 힌트가 없으면 빈 문자열)
    """

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer, hint=""):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint = hint

    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        title = f"Q{number}." if number is not None else "Q."
        print(f"\n{title} {self.question}")
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}) {choice}")

    def is_correct(self, user_answer):
        """사용자가 입력한 번호가 정답이면 True, 아니면 False."""
        return user_answer == self.answer

    def answer_text(self):
        """정답을 '2번 대규모 언어 모델(LLM)' 같은 문자열로 돌려준다."""
        return f"{self.answer}번 {self.choices[self.answer - 1]}"

    def to_dict(self):
        """JSON 파일에 저장할 수 있도록 딕셔너리로 바꾼다."""
        return {
            "question": self.question,
            "choices": list(self.choices),
            "answer": self.answer,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 Quiz 객체를 만든다.

        형식이 잘못된 데이터(손상된 파일 등)이면 ValueError를 일으킨다.
        """
        if not isinstance(data, dict):
            raise ValueError("퀴즈 항목이 딕셔너리 형식이 아닙니다.")

        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        # hint는 나중에 추가된 항목이라, 없는 옛 파일도 읽을 수 있게 기본값을 빈 문자열로 둔다.
        hint = data.get("hint", "")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("question(문제)이 올바르지 않습니다.")
        if (
            not isinstance(choices, list)
            or len(choices) != cls.CHOICE_COUNT
            or not all(isinstance(choice, str) and choice.strip() for choice in choices)
        ):
            raise ValueError(f"choices(선택지)는 문자열 {cls.CHOICE_COUNT}개여야 합니다.")
        if (
            isinstance(answer, bool)
            or not isinstance(answer, int)
            or not 1 <= answer <= cls.CHOICE_COUNT
        ):
            raise ValueError(f"answer(정답)는 1~{cls.CHOICE_COUNT} 사이의 정수여야 합니다.")
        if not isinstance(hint, str):
            raise ValueError("hint(힌트)는 문자열이어야 합니다.")

        return cls(question, choices, answer, hint)
