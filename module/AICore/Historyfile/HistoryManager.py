# -*- coding: utf-8 -*-
from typing import Callable
from pconst import const


const.valid_roles = {"user", "system", "assistant"}

class HistHistoryManager:
    """
    历史消息管理器
    用于管理AI对话的历史记录，包括消息存储、token计数和限制控制
    """

    def __init__(self, messages: dict, system_prompt: str, token_callback: Callable[[str], int], maxtoken: int):
        """
        初始化历史管理器

        参数:
            messages: 消息字典，存储对话历史的基础模板
            system_prompt: 系统提示词，作为首个消息，用于设定AI的行为和角色
            token_callback: 计算token的回调函数，接收字符串返回token数量
            maxtoken: 最大token限制，超过此值需要裁剪历史消息
        """

        # ========== 参数校验 ==========

        # 校验 messages：必须是非空的字典类型
        if messages is None:
            raise ValueError("messages 不能为 None")
        if not isinstance(messages, dict):
            raise TypeError("messages 必须是字典类型")

        # 校验 system_prompt：必须是非空的字符串类型
        if system_prompt is None:
            raise ValueError("system_prompt 不能为 None")
        if not isinstance(system_prompt, str):
            raise TypeError("system_prompt 必须是字符串类型")

        # 校验 token_callback：必须是非空的可调用对象（函数、方法、lambda等）
        if token_callback is None:
            raise ValueError("token_callback 不能为 None")
        if not callable(token_callback):
            raise TypeError("token_callback 必须是可调用对象")

        # 校验 maxtoken：必须是大于0的整数
        if maxtoken is None:
            raise ValueError("maxtoken 不能为 None")
        if not isinstance(maxtoken, int):
            raise TypeError("maxtoken 必须是整数")
        if maxtoken <= 0:
            raise ValueError("maxtoken 必须大于 0")

        # ========== token 预检查 ==========

        # 计算系统提示词的token数量
        # 如果提示词本身就超过最大限制，说明配置有问题，直接抛出异常
        prompt_tokens = token_callback(system_prompt)
        if prompt_tokens > maxtoken:
            raise ValueError(f"system_prompt 的 token 数({prompt_tokens})超过最大限制({maxtoken})")

        # ========== 初始化成员变量 ==========

        # 消息字典：存储对话历史的基础模板
        self.messages: dict = messages

        # 系统提示词：作为首个消息，不会被裁剪
        self.system_prompt: str = system_prompt

        # token计数列表：记录每条消息的token数量，用于裁剪时快速计算
        # 初始化时包含系统提示词的token数
        self.token_counts: list[int] = [prompt_tokens]

        # 总token数：当前所有消息的token总和
        self.total_tokens: int = prompt_tokens

        # token计算回调：用于计算任意字符串的token数量
        self.token_callback: Callable[[str], int] = token_callback

        # 最大token限制：超过此值时需要从头开始裁剪历史消息
        self.const.maxtoken = maxtoken

    def read(self):
        return self.messages
    
    def write(self):
        pass
