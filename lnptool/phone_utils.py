import re

def format_phone_number(phone):
    """
    格式化电话号码，支持多种输入格式：
    - 6306233000
    - (630) 623-3000
    - (630)623-3000
    - 630-623-3000
    
    返回统一的10位数字格式
    """
    if not phone:
        raise ValueError("电话号码不能为空")
    
    # 移除所有空格和点号
    phone = phone.strip().replace('.', '')
    
    # 尝试匹配不同的格式
    patterns = [
        r'^\(?(\d{3})\)?[-\s]?(\d{3})[-\s]?(\d{4})$',  # (630)623-3000 或 (630) 623-3000 或 630-623-3000
        r'^1\(?(\d{3})\)?[-\s]?(\d{3})[-\s]?(\d{4})$',  # 1(630)623-3000 或 1-630-623-3000
        r'^(\d{3})(\d{3})(\d{4})$',  # 6306233000
        r'^1(\d{3})(\d{3})(\d{4})$'   # 16306233000
    ]
    
    for pattern in patterns:
        match = re.match(pattern, phone)
        if match:
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