import pytest
from utils.phone_utils import format_phone_number

def test_format_phone_number():
    """测试电话号码格式化函数"""
    test_cases = [
        # 基本格式
        ("7132623300", "7132623300"),
        ("713-262-3300", "7132623300"),
        ("(713) 262-3300", "7132623300"),
        ("(713)262-3300", "7132623300"),
        ("(713)2623300", "7132623300"),  # 括号后直接跟数字，没有分隔符
        
        # 带国际前缀的格式
        ("+17132623300", "7132623300"),
        ("17132623300", "7132623300"),
        ("1-713-262-3300", "7132623300"),
        ("1(713)262-3300", "7132623300"),
        ("1 713 262 3300", "7132623300"),
        
        # 带点号的格式
        ("713.262.3300", "7132623300"),
        
        # 混合格式
        ("1.713.262.3300", "7132623300"),
        ("+1 (713) 262-3300", "7132623300"),
        ("1 (713) 262-3300", "7132623300"),
    ]
    
    for input_number, expected in test_cases:
        assert format_phone_number(input_number) == expected

def test_invalid_phone_numbers():
    """测试无效的电话号码格式"""
    invalid_numbers = [
        "",  # 空字符串
        "123",  # 太短
        "12345678901234",  # 太长
        "abcdefghij",  # 非数字
        "123-456-789",  # 缺少数字
        "+44 20 7946 0958",  # 非美国号码
    ]
    
    for number in invalid_numbers:
        with pytest.raises(ValueError):
            format_phone_number(number) 