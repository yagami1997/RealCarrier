import re

def format_phone_number(phone):
    """
    格式化电话号码，支持多种输入格式：
    - 7132623300
    - (713) 262-3300
    - (713)262-3300
    - (713)2623300  # 括号后直接跟数字，没有分隔符
    - 713-262-3300
    - 713.262.3300
    - +17132623300
    - 1-713-262-3300
    - 1(713)262-3300
    - 1 713 262 3300
    
    返回统一的10位数字格式
    """
    if not phone:
        raise ValueError("电话号码不能为空")
    
    # 移除所有空格、点号和多余的字符
    phone = phone.strip().replace(' ', '').replace('.', '')
    
    # 处理可能带有+号的国际格式
    if phone.startswith('+'):
        phone = phone[1:]
    
    # 尝试匹配不同的格式
    patterns = [
        r'^\(?(\d{3})\)?[-\s]?(\d{3})[-\s]?(\d{4})$',  # (713)262-3300 或 (713) 262-3300 或 713-262-3300
        r'^\((\d{3})\)(\d{7})$',  # (713)2623300 - 括号后直接跟7位数字
        r'^1\(?(\d{3})\)?[-\s]?(\d{3})[-\s]?(\d{4})$',  # 1(713)262-3300 或 1-713-262-3300
        r'^(\d{3})(\d{3})(\d{4})$',  # 7132623300
        r'^1(\d{3})(\d{3})(\d{4})$',  # 17132623300
        r'^(\d{3})[-\.](\d{3})[-\.](\d{4})$',  # 713-262-3300 或 713.262.3300
        r'^1[-\s]?(\d{3})[-\s]?(\d{3})[-\s]?(\d{4})$',  # 1 713 262 3300 或 1-713-262-3300
    ]
    
    for pattern in patterns:
        match = re.match(pattern, phone)
        if match:
            # 特殊处理(713)2623300格式
            if len(match.groups()) == 2 and re.match(r'^\((\d{3})\)(\d{7})$', phone):
                area_code = match.group(1)
                rest = match.group(2)
                prefix = rest[:3]
                line = rest[3:]
                return f"{area_code}{prefix}{line}"
            else:
                area_code, prefix, line = match.groups()
                return f"{area_code}{prefix}{line}"
    
    # 如果没有匹配任何格式，尝试提取所有数字
    digits = ''.join(filter(str.isdigit, phone))
    
    # 处理可能带有国际区号的情况
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    
    # 验证最终结果
    if len(digits) != 10:
        raise ValueError(f"无效的电话号码格式: {phone}")
    
    return digits 