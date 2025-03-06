import pytest
from utils.phone_utils import format_phone_number

def test_format_phone_number():
    # 测试各种格式的电话号码
    test_cases = [
        ("6266308117", "6266308117"),
        ("(626)6308117", "6266308117"),
        ("(626)630-8117", "6266308117"),
        ("626-630-8117", "6266308117"),
        ("16266308117", "6266308117"),  # 带国际区号
    ]
    
    for input_number, expected in test_cases:
        assert format_phone_number(input_number) == expected

def test_invalid_phone_numbers():
    invalid_numbers = [
        "626630811",    # 太短
        "62663081171",  # 太长
        "abcdefghij",   # 非数字
        "",             # 空字符串
    ]
    
    for number in invalid_numbers:
        with pytest.raises(ValueError):
            format_phone_number(number) 