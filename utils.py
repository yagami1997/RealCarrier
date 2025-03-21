from rich.console import Console

def phone_input(prompt="请输入电话号码: ", use_rich=False):
    """获取用户输入的电话号码并格式化。
    
    Args:
        prompt (str): 提示用户的文本
        use_rich (bool): 是否使用rich库增强显示
        
    Returns:
        str: 格式化后的电话号码，格式为E.164(+1XXXXXXXXXX)
    """
    while True:
        try:
            # 使用提供的提示获取用户输入，确保+1后有空格
            if use_rich:
                console = Console()
                number = console.input(prompt)
            else:
                number = input(prompt)
            
            # 清理输入的电话号码(移 
            return formatted_number  # 返回处理后的号码
        except Exception as e:
            print(f"输入错误: {str(e)}，请重试")

def formatted_number(number):
    # 实现格式化逻辑
    pass

def formatted_number(number):
    # 实现格式化逻辑
    pass 