from app.core.exceptions import BizException

def generate_mock_reply(message: str) -> str:
    if "违规" in message:
       raise BizException(
            message="输入内容不符合规范，请修改后重试",
            code=400,
            error_code="INVALID_CHAT_CONTENT"
       )
    
    if message == "系统异常":
        raise RuntimeError("模拟系统异常")

    return f"你刚才说的是：{message}"