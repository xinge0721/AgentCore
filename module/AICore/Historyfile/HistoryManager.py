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

        # 最大token限制：超过此值时需要从头开始裁剪历史消息（私有属性，通过property只读访问）
        self._maxtoken = maxtoken

    @property
    def maxtoken(self) -> int:
        """最大token限制（只读）"""
        return self._maxtoken

    def read(self):
        return self.messages
    
    async def write(self, role: str, message: str) -> bool:
        """
        异步写入新消息到历史记录

        参数:
            role: 角色（user/assistant/system）
            message: 最新消息内容

        返回:
            bool: 写入是否成功
        """
        # ========== 参数校验 ==========
        # 校验 role
        if role not in const.valid_roles:
            raise ValueError(f"无效的角色: {role}")

        # 校验 message
        if message is None:
            raise ValueError("message 不能为 None")
        if not isinstance(message, str):
            raise TypeError("message 必须是字符串类型")

        # ========== 安全防护 ==========
        # SQL注入防护（预留接口）
        # sanitized_message = await self._sanitize_message(message)

        # ========== token计算 ==========
        # 第一步：计算新消息token
        new_token = self.token_callback(message)

        # ========== 裁剪判断 ==========
        # 第二步：加上总token，第三步：检查是否超过最大token
        if self.total_tokens + new_token > self.maxtoken:
            # 第四步：超过则裁剪
            deficit = self.maxtoken - (self.total_tokens + new_token)
            if not await self._trim(deficit):
                return False

        # ========== 写入 ==========
        # 第五步：累加token_counts和messages
        self.token_counts.append(new_token)
        self.total_tokens += new_token
        self.messages["messages"].append({"role": role, "content": message})

        return True

    async def _trim(self, deficit: int) -> bool:
        """
        裁剪历史消息
        参数:
            deficit: maxtoken - (total_tokens + new_token)，负数表示超出的token数
        返回:
            bool: 裁剪是否成功（True表示裁剪后有足够空间）
        """
        # 没有可裁剪的消息（只有system_prompt）
        if len(self.token_counts) <= 1:
            return False

        # 从索引1开始（跳过system_prompt），累加直到deficit变为正数
        trim_index = 0

        for i in range(1, len(self.token_counts)):
            deficit += self.token_counts[i]
            trim_index = i
            if deficit > 0:
                break

        # 遍历完所有消息后deficit仍然不为正，裁剪所有消息也不够
        if deficit <= 0:
            return False

        # 计算被裁剪的token总数
        trimmed_tokens = sum(self.token_counts[1:trim_index + 1])

        # 裁剪token_counts（保留索引0的system_prompt）
        self.token_counts = [self.token_counts[0]] + self.token_counts[trim_index + 1:]

        # 裁剪messages（messages[i] 对应 token_counts[i+1]）
        self.messages["messages"] = self.messages["messages"][trim_index:]

        # 更新总token数
        self.total_tokens -= trimmed_tokens

        return True

    async def _sanitize_message(self, message: str) -> str:
        """SQL注入防护（预留接口）"""
        pass
# ==================== 测试代码 ====================
if __name__ == "__main__":
    import asyncio

    # 简单的token计算：1个字符 = 1个token
    def simple_token_counter(text: str) -> int:
        return len(text)

    async def test_trim():
        print("=" * 50)
        print("测试裁剪逻辑")
        print("=" * 50)

        # 测试1：正常写入，不需要裁剪
        print("\n【测试1】正常写入，不需要裁剪")
        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="sys",# 3tokens
            token_callback=simple_token_counter,
            maxtoken=100
        )
        result = await mgr.write("user", "hello")  # 5 tokens
        print(f"写入结果: {result}")
        print(f"  total_tokens: {mgr.total_tokens}")
        print(f"  token_counts: {mgr.token_counts}")
        print(f"  messages: {mgr.messages['messages']}")
        assert result == True
        assert mgr.total_tokens == 8# 3 + 5

        # 测试2：裁剪部分消息
        print("\n【测试2】裁剪部分消息")
        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="sys",  # 3 tokens
            token_callback=simple_token_counter,
            maxtoken=20
        )
        await mgr.write("user", "msg1_")  # 5 tokens, total=8
        await mgr.write("user", "msg2_")  # 5 tokens, total=13
        await mgr.write("user", "msg3_")  # 5 tokens, total=18
        print(f"  裁剪前total_tokens: {mgr.total_tokens}")
        print(f"  裁剪前 token_counts: {mgr.token_counts}")
        # 写入新消息，需要裁剪 (18+ 5 = 23 > 20)
        result = await mgr.write("user", "msg4_")
        print(f"  写入结果: {result}")
        print(f"  裁剪后 total_tokens: {mgr.total_tokens}")
        print(f"  裁剪后 token_counts: {mgr.token_counts}")
        print(f"裁剪后 messages: {mgr.messages['messages']}")
        assert result == True

        # 测试3：裁剪所有消息还不够（新消息太大）
        print("\n【测试3】裁剪所有消息还不够")
        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="sys",  # 3 tokens
            token_callback=simple_token_counter,
            maxtoken=20
        )
        await mgr.write("user", "msg1_")  # 5 tokens
        print(f"  裁剪前 total_tokens: {mgr.total_tokens}")
        # 写入超大消息 (8 + 20 = 28 > 20，裁剪msg1后3 + 20 = 23 > 20)
        result = await mgr.write("user", "a" * 20)
        print(f"  写入结果: {result}")
        print(f"  total_tokens: {mgr.total_tokens}")
        assert result == False

        # 测试4：没有可裁剪的消息
        print("\n【测试4】没有可裁剪的消息")
        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="sys",  # 3 tokens
            token_callback=simple_token_counter,
            maxtoken=10
        )
        # 直接写入超大消息 (3 + 10 = 13 > 10)
        result = await mgr.write("user", "a" * 10)
        print(f"  写入结果: {result}")
        assert result == False

        # 测试5：压力测试 - 单实例大量写入，频繁裁剪
        print("\n【测试5】压力测试 - 单实例大量写入（随机数据）")
        import random
        import string
        import time

        def random_message(min_len: int = 50, max_len: int = 500) -> str:
            """生成随机长度的消息"""
            length = random.randint(min_len, max_len)
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="s" * 1000,  # 1000 tokens 的系统提示
            token_callback=simple_token_counter,
            maxtoken=150000  # 150k tokens
        )
        success_count = 0
        total_writes = 10000
        start_time = time.time()
        for i in range(total_writes):
            msg = random_message(100, 1000)  # 每条消息100-1000 tokens
            result = await mgr.write("user", msg)
            if result:
                success_count += 1
            # 验证数据一致性
            assert len(mgr.token_counts) == len(mgr.messages["messages"]) + 1
            assert mgr.total_tokens == sum(mgr.token_counts)
            assert mgr.total_tokens <= mgr.maxtoken
        elapsed = time.time() - start_time
        print(f"  {total_writes}次写入，成功{success_count}次")
        print(f"  耗时: {elapsed:.2f}秒")
        print(f"  最终 total_tokens: {mgr.total_tokens}")
        print(f"  最终 messages数量: {len(mgr.messages['messages'])}")

        # 测试6：边界测试 - 刚好等于maxtoken
        print("\n【测试6】边界测试 - 刚好等于maxtoken")
        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="sys",  # 3 tokens
            token_callback=simple_token_counter,
            maxtoken=8
        )
        result = await mgr.write("user", "hello")  # 5 tokens, total=8，刚好等于maxtoken
        print(f"  写入结果: {result}")
        print(f"  total_tokens: {mgr.total_tokens}")
        assert result == True
        assert mgr.total_tokens == 8

        # 测试7：连续裁剪多轮
        print("\n【测试7】连续裁剪多轮")
        mgr = HistHistoryManager(
            messages={"messages": []},
            system_prompt="s",  # 1 token
            token_callback=simple_token_counter,
            maxtoken=10
        )
        # 写入多条小消息
        for i in range(5):
            await mgr.write("user", f"{i}")  # 每条1 token
        print(f"  5条消息后 total_tokens: {mgr.total_tokens}")  # 1+5=6
        # 写入一条较大消息，触发裁剪
        result = await mgr.write("user", "abcd")  # 4 tokens, 6+4=10，刚好
        print(f"  写入4token消息结果: {result}, total: {mgr.total_tokens}")
        assert result == True
        # 再写一条，继续裁剪
        result = await mgr.write("user", "xyz")  # 3 tokens
        print(f"  写入3token消息结果: {result}, total: {mgr.total_tokens}")
        assert result == True
        assert len(mgr.token_counts) == len(mgr.messages["messages"]) + 1

        # 测试8：多实例并发压力测试 - 模拟多用户
        print("\n【测试8】多实例并发压力测试 - 纯CPU（无I/O）")

        async def user_session(user_id: int, write_count: int):
            """模拟单个用户会话（无I/O延迟）"""
            user_mgr = HistHistoryManager(
                messages={"messages": []},
                system_prompt="s" * 500,
                token_callback=simple_token_counter,
                maxtoken=100000
            )
            success = 0
            for i in range(write_count):
                msg = random_message(50, 500)
                if await user_mgr.write("user", msg):
                    success += 1
            assert len(user_mgr.token_counts) == len(user_mgr.messages["messages"]) + 1
            assert user_mgr.total_tokens == sum(user_mgr.token_counts)
            return user_id, success, user_mgr.total_tokens

        user_count = 500
        writes_per_user = 200
        start_time = time.time()
        tasks = [user_session(uid, writes_per_user) for uid in range(user_count)]
        results = await asyncio.gather(*tasks)
        elapsed_cpu = time.time() - start_time

        total_success = sum(r[1] for r in results)
        print(f"  {user_count}个用户并发，每人写入{writes_per_user}条")
        print(f"  总操作数: {user_count * writes_per_user}次")
        print(f"  总成功写入: {total_success}条")
        print(f"  耗时: {elapsed_cpu:.2f}秒")

        # 测试9：带I/O延迟的异步并发 vs 顺序执行对比
        print("\n【测试9】带I/O延迟对比（模拟真实网络场景）")

        async def user_session_with_io(user_id: int, write_count: int, io_delay: float = 0.001):
            """模拟单个用户会话（带I/O延迟）"""
            user_mgr = HistHistoryManager(
                messages={"messages": []},
                system_prompt="s" * 500,
                token_callback=simple_token_counter,
                maxtoken=100000
            )
            success = 0
            for i in range(write_count):
                msg = random_message(50, 500)
                await asyncio.sleep(io_delay)  # 模拟1ms的I/O延迟（如网络请求）
                if await user_mgr.write("user", msg):
                    success += 1
            assert len(user_mgr.token_counts) == len(user_mgr.messages["messages"]) + 1
            assert user_mgr.total_tokens == sum(user_mgr.token_counts)
            return user_id, success, user_mgr.total_tokens

        # 异步并发（带I/O延迟）
        # io_user_count = 100
        # io_writes_per_user = 50
        # io_delay = 0.001  # 1ms延迟

        # print(f"  模拟I/O延迟: {io_delay * 1000:.1f}ms/次")
        # print(f"  理论顺序执行时间: {io_user_count * io_writes_per_user * io_delay:.1f}秒")

        # start_time = time.time()
        # tasks = [user_session_with_io(uid, io_writes_per_user, io_delay) for uid in range(io_user_count)]
        # results = await asyncio.gather(*tasks)
        # elapsed_async_io = time.time() - start_time

        # async_io_success = sum(r[1] for r in results)
        # print(f"\n  [异步并发] {io_user_count}用户×{io_writes_per_user}条 = {io_user_count * io_writes_per_user}次")
        # print(f"  成功: {async_io_success}条, 耗时: {elapsed_async_io:.2f}秒")

        # # 顺序执行（带I/O延迟）
        # start_time = time.time()
        # sync_results = []
        # for uid in range(io_user_count):
        #     result = await user_session_with_io(uid, io_writes_per_user, io_delay)
        #     sync_results.append(result)
        # elapsed_sync_io = time.time() - start_time

        # sync_io_success = sum(r[1] for r in sync_results)
        # print(f"\n  [顺序执行] {io_user_count}用户×{io_writes_per_user}条 = {io_user_count * io_writes_per_user}次")
        # print(f"  成功: {sync_io_success}条, 耗时: {elapsed_sync_io:.2f}秒")

        # # 对比分析
        # print("\n【性能对比】")
        # async_io_ops = (io_user_count * io_writes_per_user) / elapsed_async_io
        # sync_io_ops = (io_user_count * io_writes_per_user) / elapsed_sync_io
        # speedup = elapsed_sync_io / elapsed_async_io
        # print(f"  异步并发: {async_io_ops:.0f} ops/sec")
        # print(f"  顺序执行: {sync_io_ops:.0f} ops/sec")
        # print(f"  并发加速比: {speedup:.1f}x")

        # 测试10：并发上限压力测试
        print("\n【测试10】并发上限压力测试（逐步拉高）")
        io_delay = 0.001  # 1ms延迟
        writes_per_user = 20  # 每用户写入次数固定

        # 逐步增加并发用户数
        user_levels = [100, 500, 1000, 2000, 5000, 10000, 20000,40000,80000]
        results_table = []

        for user_count in user_levels:
            print(f"\n  测试 {user_count} 用户并发...", end="", flush=True)
            try:
                start_time = time.time()
                tasks = [user_session_with_io(uid, writes_per_user, io_delay) for uid in range(user_count)]
                results = await asyncio.gather(*tasks)
                elapsed = time.time() - start_time

                total_ops = user_count * writes_per_user
                ops_per_sec = total_ops / elapsed
                success_count = sum(r[1] for r in results)

                results_table.append({
                    "users": user_count,
                    "total_ops": total_ops,
                    "elapsed": elapsed,
                    "ops_sec": ops_per_sec,
                    "success": success_count
                })
                print(f" 完成! {elapsed:.2f}秒, {ops_per_sec:.0f} ops/sec")

            except Exception as e:
                print(f" 失败! {type(e).__name__}: {e}")
                break

        # 输出结果表格
        print("\n" + "=" * 60)
        print("【并发上限测试结果】")
        print("=" * 60)
        print(f"{'用户数':>10} | {'总操作数':>10} | {'耗时(秒)':>10} | {'ops/sec':>12}")
        print("-" * 60)
        for r in results_table:
            print(f"{r['users']:>10} | {r['total_ops']:>10} | {r['elapsed']:>10.2f} | {r['ops_sec']:>12.0f}")
        print("-" * 60)

        # 找出最佳性能点
        if results_table:
            best = max(results_table, key=lambda x: x["ops_sec"])
            print(f"最佳性能: {best['users']}用户, {best['ops_sec']:.0f} ops/sec")

        print("\n" + "=" * 50)
        print("所有测试通过!")
        print("=" * 50)

    asyncio.run(test_trim())
