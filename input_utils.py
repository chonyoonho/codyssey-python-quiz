"""사용자 입력을 안전하게 받는 도우미 함수 모음.

잘못된 입력이 들어와도 프로그램이 멈추지 않고, 안내 메시지를 보여 준 뒤
올바른 값이 들어올 때까지 다시 입력받는다.
"""


def read_int(prompt, low, high, commands=()):
    """low 이상 high 이하의 정수를 입력받아 돌려준다.

    처리하는 경우:
    - 입력 앞뒤 공백은 제거한다. (예: " 1 " -> 1)
    - 빈 입력(그냥 Enter)이면 안내 후 다시 입력받는다.
    - 숫자가 아니면(예: abc) 안내 후 다시 입력받는다.
    - 범위 밖의 숫자면(예: 메뉴 9) 안내 후 다시 입력받는다.

    commands: 숫자 대신 허용할 명령 글자 목록 (예: ("h",)).
    명령 글자를 입력하면 숫자 대신 그 글자(소문자)를 돌려준다.
    """
    allowed = "숫자" if not commands else "숫자 또는 " + "/".join(commands)
    while True:
        text = input(prompt).strip()
        if text == "":
            print(f"  ! 아무것도 입력하지 않았습니다. {allowed}를 입력해 주세요.")
            continue
        if text.lower() in commands:
            return text.lower()
        try:
            number = int(text)
        except ValueError:
            print(f"  ! '{text}'은(는) 숫자가 아닙니다. {allowed}만 입력해 주세요.")
            continue
        if number < low or number > high:
            print(f"  ! {low}~{high} 사이의 숫자를 입력해 주세요.")
            continue
        return number


def read_text(prompt, allow_empty=False):
    """문자열을 입력받아 돌려준다. (앞뒤 공백은 제거)

    allow_empty가 False(기본)이면 빈 입력을 거절하고 다시 묻는다.
    True이면 빈 입력도 그대로 받아들인다. (힌트처럼 선택 입력일 때 사용)
    """
    while True:
        text = input(prompt).strip()
        if text == "" and not allow_empty:
            print("  ! 빈 입력입니다. 내용을 입력해 주세요.")
            continue
        return text
