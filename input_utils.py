"""사용자 입력을 안전하게 받는 도우미 함수 모음.

잘못된 입력이 들어와도 프로그램이 멈추지 않고, 안내 메시지를 보여 준 뒤
올바른 값이 들어올 때까지 다시 입력받는다.
"""


def read_int(prompt, low, high):
    """low 이상 high 이하의 정수를 입력받아 돌려준다.

    처리하는 경우:
    - 입력 앞뒤 공백은 제거한다. (예: " 1 " -> 1)
    - 빈 입력(그냥 Enter)이면 안내 후 다시 입력받는다.
    - 숫자가 아니면(예: abc) 안내 후 다시 입력받는다.
    - 범위 밖의 숫자면(예: 메뉴 9) 안내 후 다시 입력받는다.
    """
    while True:
        text = input(prompt).strip()
        if text == "":
            print("  ! 아무것도 입력하지 않았습니다. 숫자를 입력해 주세요.")
            continue
        try:
            number = int(text)
        except ValueError:
            print(f"  ! '{text}'은(는) 숫자가 아닙니다. 숫자만 입력해 주세요.")
            continue
        if number < low or number > high:
            print(f"  ! {low}~{high} 사이의 숫자를 입력해 주세요.")
            continue
        return number


def read_text(prompt):
    """비어 있지 않은 문자열을 입력받아 돌려준다. (앞뒤 공백은 제거)"""
    while True:
        text = input(prompt).strip()
        if text == "":
            print("  ! 빈 입력입니다. 내용을 입력해 주세요.")
            continue
        return text
