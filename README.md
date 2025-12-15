# AI 编辑器模块业务逻辑说明文档

## 1. 模块目标与整体设计思路

本 AI 模块是一个「AI 编辑器内核」，负责：

1. 管理用户登录 / 权限（待实现）
2. 管理与多个大模型（对话模型、知识模型）的交互
3. 通过 MCP 调用文件系统 / 数据库 / 网络等工具
4. 在权限约束下完成读写文件、搜索信息等操作（权限系统待实现）
5. 将复杂的内部操作抽象成自然语言对话对用户呈现

### 核心原则

* **解耦**：业务层不直接拿 AI 实例，只通过回调调用
* **权限优先**：所有外部资源访问统一经 MCP + 权限系统（权限系统待实现）
* **双 AI 分工**：对话 AI 负责对话和规划，知识 AI 负责数据收集和简单处理
* **有结构的数据流**：所有数据在模块间流动路径清晰可追踪

---

## 2. 模块与子模块总览

主要涉及以下子模块：

* **Main（主文件）**：`ai_assistant.py` - 入口，负责系统启动与模块协调
* **AuthCore**：登录 / 注册 / 权限等级查询（**未实现**）
* **Agent 模块**
  * **ConversationHandler**：会话控制器，负责整体对话流程与任务调度
  * **_Search**：知识检索处理，负责 TODO 生成与执行
  * **_Dialogue**：对话生成处理，负责最终回答生成
* **AICore 模块**
  * **AIManager**：AI 工厂，创建/管理模型调用回调
  * **OPEN_AI**：OpenAI 封装类，处理实际 API 请求、异常与历史记录
  * **HistoryManager**：历史记录管理器，支持 token 裁剪
* **MCP 服务器**：
  * 工具调用统一入口（文件、DB、网络等）
  * **权限管理**（**未实现**）
  * **FileWatcher（AllEventsHandler）**：文件监听器
  * **WorkspaceIndex**：工作区文件索引（**未独立实现**，功能在 _Search 中）
* **对话 AI（Dialog AI）**：面向用户的主模型，负责理解问题与生成计划、给用户最终回答
* **知识 AI（Knowledge AI）**：便宜快速模型，只负责「收集数据 + 简单处理」
* **TaskScheduler**：任务调度器（**未独立实现**，逻辑内嵌在 ConversationHandler 中）

---

## 3. 启动阶段的数据流与时序

### 3.1 启动阶段的流程（当前实现）

**入口：Main（ai_assistant.py）**

Main 启动后，执行以下流程：

1. **Agent 启动流程**
   * Main → AICore 模块
   * AICore 内部：
     1. 启动 **AIManager**：
        * 读取配置/密钥（`module/AICore/role/secret_key.json`）
        * 准备不同模型的调用参数（base URL、模型名等）
     2. 使用 AIManager 创建两个回调：
        * `dialogue_callback(...)`：对话模型调用接口
        * `knowledge_callback(...)`：知识模型调用接口
        * 注意：**外部只拿到"函数"，不拿到真实模型实例**，模型切换由 AIManager 内部处理
     3. 把上述两个回调传给 **ConversationHandler** 完成初始化

2. **文件监控启动**
   * Main → AllEventsHandler（文件监控器）
   * AllEventsHandler 内部启动：
     * 监听工作区目录文件变化
     * 事件队列管理

3. **MCP 启动流程**（可选）
   * Main → MCP 服务器
   * MCP 内部启动：
     * MCP 核心服务（基于 FastMCP）
     * 加载工具插件（文件工具、DB 工具、网络工具等）

### 3.2 用户会话上下文绑定（待实现）

当 AuthCore 完成用户验证后（**当前未实现**）：

1. Main 将 `userInfo + permissionLevel` 传入 MCP
2. MCP 创建用户会话上下文
3. 权限系统基于该用户加载相关权限规则

---

## 4. 单轮对话的数据流（重点）

这一段是后续开发者最需要看的核心逻辑。

### 4.1 从用户到对话 AI：规划阶段

1. 用户在编辑器中输入问题（或指令）

2. Main 将用户输入交给 **ConversationHandler**

3. **ConversationHandler 三阶段流程**：

   **阶段 1：生成 TODO 搜索规划**
   * ConversationHandler 调用 `_Search.generate_todo_plan()`
   * _Search 调用知识 AI（通过 `knowledge_callback`）
   * 知识 AI 输出：一份 **TODO 任务列表**（JSON 格式），例如：
     * Task1：列出当前项目相关的所有文档
     * Task2：读取与某关键词相关的几份文档
     * Task3：整理文档内容，生成对用户友好的总结

   **阶段 2：执行 TODO 列表**
   * ConversationHandler 调用 `_Search.execute_todo_list()`
   * _Search 根据 TODO 列表：
     * 扫描文件结构（`_scan_files()`）
     * 调用 MCP 工具（通过 JSON 指令）
     * 监控文件变化（AllEventsHandler）
     * 收集所有查询结果

   **阶段 3：生成最终回答**
   * ConversationHandler 调用 `_Dialogue.generate_response()`
   * _Dialogue 调用对话 AI（通过 `dialogue_callback`）
   * 对话 AI 基于查询结果生成最终回答
   * 返回给用户

### 4.2 知识 AI + MCP：执行阶段（实际实现）

在阶段 2 中，_Search 执行 TODO 列表：

1. **文件扫描**：
   * _Search 调用 `_scan_files()` 扫描工作区文件结构
   * 将文件列表注入到知识 AI 的上下文中

2. **MCP 工具调用**（通过 JSON 指令）：
   * 知识 AI 生成 JSON 格式的工具调用指令
   * _Search 解析 JSON 指令并调用 MCP 工具
   * MCP 工具执行操作（文件读取、数据库查询等）
   * 返回执行结果给 _Search

3. **文件监控**：
   * AllEventsHandler 实时监控文件变化
   * _Search 读取文件变化事件
   * 更新文件上下文并注入到知识 AI

4. **权限控制**（**当前未实现**）：
   * MCP 接收到工具调用请求后：
     1. **权限系统**：根据当前用户会话上下文判断该操作是否允许
     2. 若允许：调用对应工具并返回结果
     3. 若不允许：返回 `permission_denied` 错误

### 4.3 高风险操作：对话 AI + 用户确认（待实现）

对于删除文件等高风险任务（**当前未实现**）：

1. 在 TODO 列表里会标记：
   * `executor = dialog-ai`
   * `requireUserConfirm = true`

2. 当执行到该任务时：
   * 调用对话 AI 生成确认提示语
   * 对话 AI 把确认问题发给用户
   * 用户明确确认后才执行操作

---

## 5. 文件监听与 WorkspaceIndex 的数据流

为了让 AI 知道当前软件中有哪些文件、是否变更，系统引入了：

* **AllEventsHandler（FileWatcher）**：监听工作区目录
* **WorkspaceIndex**：维护文件索引和元数据（**当前未独立实现**，功能在 _Search 中）

数据流如下：

1. **系统启动 / 工作区加载时**
   * AllEventsHandler 开始监听文件系统
   * _Search 在需要时扫描文件结构（`_scan_files()`）

2. **运行中用户对文件做任何修改**
   * AllEventsHandler 捕捉 OS 文件事件
   * 事件存储在队列中

3. **AI 查询工作区结构时**
   * _Search 调用 `_scan_files()` 获取文件列表
   * 读取 AllEventsHandler 的事件队列
   * 更新文件上下文并注入到知识 AI

---

## 6. 双 AI 的分工与数据流向

可以简单概括为：

* **对话 AI（贵）**：
  * 输入：用户问题 + 部分上下文 + 知识 AI 整理后的信息
  * 主要职责：
    * 理解用户需求
    * 规划 TODO 列表（在知识 AI 协助下）
    * 生成与用户对话内容
    * 决定是否进行高风险操作（待实现）

* **知识 AI（便宜）**：
  * 输入：对话 AI 给出的任务 + 当前已有数据 + 工具调用结果
  * 主要职责：
    * 生成 TODO 计划
    * 利用 MCP 工具（在权限内）做搜索、读文件、查 DB、简单写入/创建
    * 对结果做初步整理、筛选、结构化
    * 将整理后的中间结果交回对话 AI

**数据流总结**：

```
用户 → ConversationHandler
  → 阶段1：知识AI生成TODO规划（_Search.generate_todo_plan）
  → 阶段2：知识AI执行TODO（_Search.execute_todo_list）
    ├─ 扫描文件结构
    ├─ 调用MCP工具
    └─ 监控文件变化
  → 阶段3：对话AI生成最终回答（_Dialogue.generate_response）
  → 用户
```

---

## 7. 权限控制的关键要点（待实现）

* 权限实体：用户 / 角色（role）
* 资源范围：**仅限导入到本软件的文件/数据源**（非操作系统全盘）
* 权限操作：`read`, `write`, `delete`, `list`, `execute` 等
* 较高粒度：可以到文件/目录/数据源级
* 知识 AI 的权限**通常是用户权限的收紧版本**（例如禁用 delete、禁用访问 root-only 资源）
* 所有工具调用（包括 AI 发起的）都要先走 MCP → 权限验证 → 工具适配层

权限不足时的行为：
* MCP 返回 `permission_denied`
* 标记任务失败并提示知识 AI
* 知识 AI 尽力寻找替代方案
* 最终对话 AI 会告知用户：部分资源因权限限制未访问，答复可能不完整

---

## 8. 实现状态总结

### ✅ 已实现功能

1. **双 AI 协同架构**
   - 对话 AI（role_A）：负责理解用户需求、生成回答
   - 知识 AI（role_B）：负责数据收集、TODO 规划、文件搜索

2. **三阶段对话流程**
   - 阶段 1：知识 AI 生成 TODO 搜索规划
   - 阶段 2：知识 AI 执行 TODO 列表（调用 MCP 工具/扫描文件）
   - 阶段 3：对话 AI 生成最终回答

3. **MCP 工具调用系统**
   - 30+ 工具函数
   - 支持文件操作、数据库操作、数据查询
   - 异步任务队列管理

4. **文件监控系统**
   - 实时监控工作区文件变化（AllEventsHandler）
   - 事件队列存储
   - 集成到对话流程中

5. **多模型支持**
   - 已支持：DeepSeek、Qwen、Kimi、Doubao
   - 待支持：Claude、Gemini、ChatGPT、Xinhuo

6. **历史管理系统**
   - Token 自动裁剪
   - 保留 system 消息
   - 支持多角色历史分离

### ⏳ 待实现功能

1. **AuthCore 模块**（登录/注册/权限系统）
2. **独立的权限管理系统**
3. **独立的 TaskScheduler**（当前逻辑内嵌在 ConversationHandler 中）
4. **独立的 WorkspaceIndex**（当前功能在 _Search 中）
5. **高风险操作的用户确认机制**
6. **更多 AI 模型支持**（Claude、Gemini 等）

### ⚠️ 已知问题

1. **导入路径错误**
   - 文件：`ai_assistant.py:16`
   - 错误：`from module.Agent.AIManager import AIFactory`
   - 应为：`from module.AICore.AIManager import AIFactory`

2. **缺失模块**
   - JSONProcessor（被多处引用但未找到实现文件）

3. **部分模型未实现**
   - Claude、Gemini、ChatGPT、Xinhuo 模型文件存在但未实现

---

## 9. 快速开始

### 配置 API 密钥

#### 方式一：使用 Web 配置界面（推荐）

```bash
cd window
python app.py
# 或直接双击：启动配置管理.bat
```

在浏览器中打开 `http://localhost:5000`，配置您的 API 密钥。

#### 方式二：手动编辑配置文件

编辑 `module/AICore/role/secret_key.json`：

```json
{
  "deepseek": {
    "api_key": "your_deepseek_api_key_here",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-chat"
  },
  "qwen": {
    "api_key": "your_qwen_api_key_here",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo"
  }
}
```

### 运行主程序

```bash
python ai_assistant.py
```

---

## 10. 文档索引

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 详细的项目目录结构和模块说明
- [README_USAGE.md](README_USAGE.md) - OPEN_AI 类使用指南
- [window/README.md](window/README.md) - Web 配置管理界面说明

---

## 11. 依赖安装

```bash
# 核心依赖
pip install openai watchdog

# Web 配置界面
pip install flask flask-cors

# MCP 支持
pip install fastmcp

# 可选：Qwen 模型 token 计算
pip install transformers
```

---

## 12. 注意事项

1. **API 密钥安全**
   - 不要将 `secret_key.json` 提交到版本控制
   - 使用 Web 配置系统时注意网络安全

2. **Token 管理**
   - 合理设置 `max_tokens` 控制成本
   - 不同模型的 token 计算方式可能不同

3. **文件监控**
   - 文件监控基于 watchdog 库
   - 需要在工作区目录下运行

4. **MCP 工具调用**
   - MCP 工具调用通过 JSON 指令格式进行
   - 支持异步任务队列管理
