# AgentCore - 智能AI服务器

## 1. 项目定位与设计目标

**AgentCore** 是一个基于双AI协同架构的智能服务器系统，类似于MySQL等数据库服务器，提供：

1. **多用户并发支持**：支持多个客户端同时连接和会话管理
2. **跨语言客户端**：不限于Python，支持任何语言通过网络协议接入
3. **双AI协同处理**：对话AI（决策层）+ 知识AI（执行层）智能分工
4. **统一工具调用**：通过MCP协议调用文件系统、数据库、网络等工具
5. **完善的权限系统**：多用户场景下的认证、授权、资源隔离（规划中）
6. **状态机驱动**：基于状态机的灵活对话流程控制

### 核心设计原则

* **服务器架构**：客户端-服务器模型，支持网络通信和会话管理
* **并发隔离**：每个用户会话独立，资源隔离，互不干扰
* **解耦设计**：业务层不直接持有AI实例，通过回调函数调用
* **权限优先**：所有资源访问必须经过权限验证（规划中）
* **双AI分工**：对话AI负责理解和决策，知识AI负责执行和数据处理
* **状态机控制**：灵活的状态转换，适应复杂对话场景

---

## 2. 系统架构总览

### 2.1 服务器架构（规划中）

```
┌─────────────────────────────────────────────────────────┐
│                    客户端层                              │
│  Python客户端 | JavaScript客户端 | Go客户端 | ...       │
└────────────────────┬────────────────────────────────────┘
                     │ (HTTP/WebSocket/gRPC)
┌────────────────────┴────────────────────────────────────┐
│                  网络通信层（规划中）                     │
│  - 连接管理  - 会话管理  - 负载均衡  - 协议适配            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  认证与权限层（规划中）                   │
│  - 用户认证  - 权限验证  - 资源隔离  - 会话上下文          │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                   AI核心层（已实现）                      │
│  - Agent状态机  - 双AI协同  - 对话流程控制                 │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│                  工具调用层（已实现）                     │
│  - MCP服务器  - 文件操作  - 数据库  - 任务管理             │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心模块说明

#### ✅ 已实现模块

* **Main（主入口）**：[main.py](main.py) - 系统启动入口
* **Agent 模块**：[module/Agent/Agent.py](module/Agent/Agent.py)
  * 基于**状态机模式**的对话流程控制
  * 9个状态：IDLE、MODEL_A_DECIDING、DIRECT_ANSWER、CALL_MCP_TOOL、COMPLEX_TASK_PLANNING、MODEL_B_JUDGING、MODEL_B_EXECUTING、MODEL_A_SUMMARIZING、ENDING
  * 动态状态转换，根据AI决策自动切换

* **AICore 模块**：
  * **AIManager**：[module/AICore/AIManager.py](module/AICore/AIManager.py) - AI工厂，管理双AI实例
  * **OPEN_AI**：[module/AICore/Tool/OPEN_AI.py](module/AICore/Tool/OPEN_AI.py) - OpenAI标准接口封装
  * **HistoryManager**：[module/AICore/Tool/HistoryManager.py](module/AICore/Tool/HistoryManager.py) - 历史记录管理，支持token裁剪
  * **ConfigValidator**：[module/AICore/Tool/ConfigValidator.py](module/AICore/Tool/ConfigValidator.py) - 配置验证器

* **MCP 工具系统**：
  * **MCPServer**：[module/MCP/server/MCPServer.py](module/MCP/server/MCPServer.py) - MCP服务器（基于FastMCP）
  * **MCPClient**：[module/MCP/client/MCPClient.py](module/MCP/client/MCPClient.py) - 异步MCP客户端，支持任务队列
  * **TaskManager**：[module/MCP/server/Tools/TaskManager.py](module/MCP/server/Tools/TaskManager.py) - 任务管理工具（已启用）
  * **Mathematics**：[module/MCP/server/Tools/mathematics.py](module/MCP/server/Tools/mathematics.py) - 数学计算工具（已启用）
  * **DatabaseEditor**：[module/MCP/server/Tools/DatabaseEditor.py](module/MCP/server/Tools/DatabaseEditor.py) - 数据库工具（已实现但被注释）
  * **FileEditor**：[module/MCP/server/Tools/FileEditor.py](module/MCP/server/Tools/FileEditor.py) - 文件编辑工具（已实现但被注释）
  * **WorkspaceManager**：[module/MCP/server/Tools/WorkspaceManager.py](module/MCP/server/Tools/WorkspaceManager.py) - 工作空间管理（已实现但被注释）

* **文件监控系统**：
  * **AllEventsHandler**：[tools/AllEventsHandler.py](tools/AllEventsHandler.py) - 基于watchdog的文件监控器（已实现但未集成）


#### ⏳ 规划中模块

* **网络通信层**：支持HTTP/WebSocket/gRPC协议（未实现）
* **AuthCore**：用户认证、注册、权限管理（未实现）
* **会话管理器**：多用户会话隔离、连接池管理（未实现）
* **权限系统**：资源级权限控制、用户角色管理（未实现）

#### 🤖 双AI协同

* **对话AI（role_A）**：
  * 模型：deepseek-reasoner（可配置）
  * 职责：理解用户需求、判断是否需要工具、生成最终回答
  * 配置：[module/AICore/role/role_A/assistant.json](module/AICore/role/role_A/assistant.json)

* **知识AI（role_B）**：
  * 模型：deepseek-reasoner（可配置）
  * 职责：数据收集、TODO规划、执行MCP工具调用
  * 配置：[module/AICore/role/role_B/assistant.json](module/AICore/role/role_B/assistant.json)

---

## 3. 系统启动流程

### 3.1 当前启动流程（单用户模式）

**入口：[main.py](main.py)**

系统启动时执行以下流程：

```
1. 加载配置
   ├─ 读取 secret_key.json（API密钥）
   ├─ 读取 config.json（模型配置）
   └─ 读取 role_A/assistant.json 和 role_B/assistant.json（系统提示词）

2. 初始化 AIManager
   ├─ 创建对话AI实例（role_A）
   ├─ 创建知识AI实例（role_B）
   └─ 生成回调函数：dialogue_callback() 和 knowledge_callback()

3. 启动 MCP 服务器
   ├─ 加载 TaskManager 工具（3个）
   ├─ 加载 Mathematics 工具（6个）
   └─ 启动 MCPClient（异步任务队列）

4. 初始化 Agent 状态机
   ├─ 注入 dialogue_callback 和 knowledge_callback
   ├─ 注入 MCP 客户端
   └─ 设置初始状态为 IDLE

5. 进入对话循环
   └─ 等待用户输入，触发状态机流转
```

**注意**：
- 文件监控系统（AllEventsHandler）已实现但当前未启动
- 当前为单用户模式，无会话隔离

### 3.2 未来服务器模式启动流程（规划中）

```
1. 加载配置（同上）

2. 启动网络通信层
   ├─ 监听端口（HTTP/WebSocket/gRPC）
   ├─ 初始化连接池
   └─ 启动负载均衡器

3. 启动认证与权限层
   ├─ 加载用户数据库
   ├─ 初始化权限规则引擎
   └─ 启动会话管理器

4. 初始化 AI 核心层（共享资源池）
   ├─ 创建 AI 实例池（支持并发）
   ├─ 启动 MCP 服务器集群
   └─ 初始化文件监控系统

5. 等待客户端连接
   └─ 每个连接创建独立的 Agent 实例和会话上下文
```

---

## 4. 对话流程详解（核心机制）

### 4.1 状态机驱动的对话流程

AgentCore 使用**状态机模式**控制对话流程，根据AI的决策动态切换状态。

#### 状态机的9个状态

```
┌─────────────────────────────────────────────────────────┐
│  IDLE（空闲）                                            │
│  ↓ 用户输入                                              │
│  MODEL_A_DECIDING（对话AI决策）                          │
│  ├─→ DIRECT_ANSWER（直接回答）→ ENDING                  │
│  ├─→ CALL_MCP_TOOL（调用工具）→ MODEL_A_DECIDING        │
│  └─→ COMPLEX_TASK_PLANNING（复杂任务规划）               │
│      ↓                                                   │
│      MODEL_B_JUDGING（知识AI判断是否介入）               │
│      ├─→ 不介入 → MODEL_A_SUMMARIZING                    │
│      └─→ 介入 → MODEL_B_EXECUTING（执行TODO）            │
│                 ↓                                        │
│                 MODEL_A_SUMMARIZING（对话AI汇总）         │
│                 ↓                                        │
│                 IDLE（返回空闲，对话AI决定是否结束）      │
│                 ↓                                        │
│                 ENDING（结束）                           │
└─────────────────────────────────────────────────────────┘
```

### 4.2 典型对话流程示例

#### 场景1：简单问答（无需工具）

```
用户："你好，今天天气怎么样？"
  ↓
IDLE → MODEL_A_DECIDING
  ↓ 对话AI判断：无需工具，直接回答
DIRECT_ANSWER
  ↓ 对话AI生成回答
ENDING
  ↓
返回用户："你好！我无法获取实时天气信息..."
```

#### 场景2：简单工具调用

```
用户："计算 123 + 456"
  ↓
IDLE → MODEL_A_DECIDING
  ↓ 对话AI判断：需要调用数学工具
CALL_MCP_TOOL
  ↓ 调用 Mathematics.add(123, 456)
  ↓ 返回结果：579
MODEL_A_DECIDING
  ↓ 对话AI判断：已获得结果，可以回答
DIRECT_ANSWER
  ↓
ENDING
  ↓
返回用户："123 + 456 = 579"
```

#### 场景3：复杂任务（需要知识AI介入）

```
用户："分析项目中所有Python文件的函数定义"
  ↓
IDLE → MODEL_A_DECIDING
  ↓ 对话AI判断：复杂任务，需要规划
COMPLEX_TASK_PLANNING
  ↓ 对话AI生成任务规划（PLAN类型）
MODEL_B_JUDGING
  ↓ 知识AI判断：需要介入
MODEL_B_EXECUTING
  ↓ 知识AI生成TODO列表：
  │ 1. 扫描工作区，找到所有.py文件
  │ 2. 读取每个文件内容
  │ 3. 提取函数定义（def关键字）
  │ 4. 整理成结构化数据
  ↓ 知识AI逐步执行TODO，调用MCP工具
  ↓ 收集所有结果
MODEL_A_SUMMARIZING
  ↓ 对话AI汇总知识AI的执行结果
IDLE
  ↓ 对话AI判断：任务完成
ENDING
  ↓
返回用户："我找到了15个Python文件，共包含42个函数定义..."
```

### 4.3 双AI协同机制

#### 对话AI（role_A）的职责

1. **理解用户意图**：分析用户输入，判断任务类型
2. **决策路由**：
   - 简单问答 → DIRECT_ANSWER
   - 简单工具调用 → CALL_MCP_TOOL
   - 复杂任务 → COMPLEX_TASK_PLANNING
3. **生成最终回答**：将执行结果转化为自然语言
4. **判断是否结束**：决定对话是否完成

#### 知识AI（role_B）的职责

1. **判断是否介入**：评估任务复杂度，决定是否需要自己执行
2. **生成TODO列表**：将复杂任务分解为可执行的步骤
3. **执行TODO**：
   - 调用MCP工具（文件操作、数据库查询等）
   - 收集和整理数据
   - 处理工具调用结果
4. **反馈执行结果**：将结构化数据返回给对话AI

### 4.4 MCP工具调用流程

```
知识AI生成工具调用请求（OpenAI格式）
  ↓
MCPClient.add(data) → 添加到任务队列
  ↓
异步线程处理任务
  ↓
OpenAI格式 → MCP格式转换
  ↓
调用MCP工具（TaskManager、Mathematics等）
  ↓
MCP格式 → OpenAI格式转换
  ↓
MCPClient.get_result(task_id) → 返回结果
  ↓
知识AI接收结果，继续执行下一步
```

### 4.5 权限控制机制（规划中）

在多用户服务器模式下，每个工具调用都需要经过权限验证：

```
用户A请求："删除文件 config.json"
  ↓
会话管理器：识别用户A的会话ID
  ↓
权限系统：检查用户A是否有删除权限
  ├─→ 有权限：执行删除操作
  └─→ 无权限：返回 permission_denied 错误
      ↓
      对话AI告知用户："抱歉，您没有删除该文件的权限"
```

**权限级别设计**（规划中）：
- **只读用户**：只能读取文件、查询数据
- **普通用户**：可以读写自己的文件
- **管理员**：可以访问所有资源
- **AI专用权限**：知识AI的权限通常低于用户权限（例如禁止删除操作）

---

## 5. 文件监控系统（已实现但未集成）

### 5.1 AllEventsHandler 文件监控器

**位置**：[tools/AllEventsHandler.py](tools/AllEventsHandler.py)

**功能**：
- 基于 watchdog 库实现
- 监控文件创建、删除、修改、移动事件
- 事件队列管理（内存存储）
- 支持递归监控子目录

**当前状态**：已完整实现但未在 main.py 中启动

**未来集成计划**：
1. 在系统启动时启动文件监控
2. 将文件变化事件注入到知识AI的上下文
3. 支持实时感知工作区文件变化

---

## 6. AI模型支持

### 6.1 已支持的模型

| 供应商 | 模型 | 实现状态 | 配置文件 |
|--------|------|---------|---------|
| **DeepSeek** | deepseek-chat, deepseek-reasoner | ✅ 已实现 | [module/AICore/Model/deepseek.py](module/AICore/Model/deepseek.py) |
| **Qwen** | qwen-turbo, qwen-plus, qwen-max 等 | ✅ 已实现 | [module/AICore/Model/qwen.py](module/AICore/Model/qwen.py) |
| **Kimi** | moonshot-v1-8k, moonshot-v1-32k 等 | ✅ 已实现 | [module/AICore/Model/Kiimi.py](module/AICore/Model/Kiimi.py) |
| **Doubao** | doubao-seed-1-6-lite 等 | ✅ 已实现 | [module/AICore/Model/doubao.py](module/AICore/Model/doubao.py) |

### 6.2 规划支持的模型

| 供应商 | 模型 | 实现状态 |
|--------|------|---------|
| **Claude** | claude-3-opus, claude-3-sonnet 等 | ⏳ 文件存在但未实现 |
| **Gemini** | gemini-pro, gemini-ultra 等 | ⏳ 文件存在但未实现 |
| **ChatGPT** | gpt-4, gpt-3.5-turbo 等 | ⏳ 文件存在但未实现 |
| **Xinhuo** | generalv3.5 等 | ⏳ 文件存在但未实现 |

### 6.3 模型配置

所有模型配置存储在：
- **API密钥**：[module/AICore/role/secret_key.json](module/AICore/role/secret_key.json)
- **模型参数**：[module/AICore/role/config.json](module/AICore/role/config.json)

---

## 7. MCP工具系统详解

### 7.1 当前启用的工具（9个）

#### TaskManager 工具（3个）
- `exit_task` - 退出任务
- `plan_task` - 规划任务
- `generate_todo_list` - 生成TODO列表

#### Mathematics 工具（6个）
- `add` - 加法
- `subtract` - 减法
- `multiply` - 乘法
- `divide` - 除法
- `power` - 幂运算
- `sqrt` - 平方根

### 7.2 已实现但被注释的工具（30+个）

#### DatabaseEditor 工具（12个）
文件：[module/MCP/server/Tools/DatabaseEditor.py](module/MCP/server/Tools/DatabaseEditor.py)
- connect, delete, insert_data, update_data, delete_data
- create_table, delete_table, write, read
- list_tables, list_all_data, count_records, data_exists

#### FileEditor 工具（10个）
文件：[module/MCP/server/Tools/FileEditor.py](module/MCP/server/Tools/FileEditor.py)
- read_line, read_all, update_line, delete_line, insert_line
- append_line, clear_file, read_JSON, write_JSON, append_JSON

#### WorkspaceManager 工具（4个）
文件：[module/MCP/server/Tools/WorkspaceManager.py](module/MCP/server/Tools/WorkspaceManager.py)
- scan_workspace - 扫描工作区
- search_files - 搜索文件
- get_file_metadata - 获取文件元数据
- list_files_simple - 简单列出文件

#### DataInquire 工具（10个）
文件：[module/MCP/server/Tools/DataInquire.py](module/MCP/server/Tools/DataInquire.py)
- file_directory, file_content, file_line_count
- file_content_fuzzy, database_all_table, database_table_content 等

**注意**：这些工具已完整实现，只是在 MCPServer.py 中被注释掉了。启用它们只需取消注释即可。

---

## 8. 多用户服务器架构规划

### 8.1 核心挑战

从当前的单用户模式升级到多用户服务器模式，需要解决：

1. **会话隔离**：每个用户的对话历史、上下文、状态机实例必须独立
2. **资源隔离**：文件访问、数据库连接、工作区必须按用户隔离
3. **并发控制**：多个用户同时请求时，AI调用需要排队或并发处理
4. **权限管理**：不同用户有不同的资源访问权限
5. **连接管理**：支持长连接（WebSocket）或短连接（HTTP）

### 8.2 技术方案建议

#### 方案A：Python + FastAPI（推荐）

**优势**：
- 保持现有Python生态
- FastAPI支持异步并发
- 开发速度快，改动最小
- 性能足够（每秒数千请求）

**架构**：
```python
# 伪代码示例
from fastapi import FastAPI, WebSocket
from module.Agent.Agent import Agent
from module.AICore.AIManager import AIFactory

app = FastAPI()

# 会话管理器
sessions = {}  # {session_id: Agent实例}

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()

    # 为每个用户创建独立的Agent实例
    agent = Agent(...)
    session_id = generate_session_id()
    sessions[session_id] = agent

    while True:
        data = await websocket.receive_text()
        response = agent.process(data)
        await websocket.send_text(response)
```

#### 方案B：Go/Rust网关 + Python AI核心

**优势**：
- 网关层性能极高
- Python专注AI逻辑
- 更好的资源控制

**架构**：
```
Go网关（处理连接、认证、会话）
  ↓ gRPC/HTTP
Python AI核心（处理AI逻辑）
```

### 8.3 实现路线图

**阶段1：网络通信层**（优先级：高）
- [ ] 实现 FastAPI 服务器
- [ ] 支持 WebSocket 长连接
- [ ] 实现会话管理器
- [ ] 实现连接池

**阶段2：认证与权限**（优先级：高）
- [ ] 实现 AuthCore 模块（用户注册、登录）
- [ ] 实现权限系统（资源级权限控制）
- [ ] 实现会话上下文绑定
- [ ] 实现用户资源隔离

**阶段3：并发优化**（优先级：中）
- [ ] AI实例池（避免每次创建）
- [ ] 请求队列管理
- [ ] 负载均衡
- [ ] 缓存机制

**阶段4：客户端SDK**（优先级：中）
- [ ] Python客户端
- [ ] JavaScript客户端
- [ ] Go客户端
- [ ] 统一的客户端协议文档

**阶段5：监控与运维**（优先级：低）
- [ ] 日志系统
- [ ] 性能监控
- [ ] 错误追踪
- [ ] 健康检查接口

---

## 9. 实现状态总结

### ✅ 已实现功能

#### 核心架构
- ✅ **状态机驱动的Agent**：9个状态，动态流程控制
- ✅ **双AI协同架构**：对话AI（决策层）+ 知识AI（执行层）
- ✅ **AI工厂模式**：统一的模型管理和切换机制
- ✅ **历史管理系统**：Token自动裁剪、多角色历史分离

#### AI模型支持
- ✅ **DeepSeek**：deepseek-chat, deepseek-reasoner
- ✅ **Qwen**：qwen-turbo, qwen-plus, qwen-max 等
- ✅ **Kimi**：moonshot-v1-8k, moonshot-v1-32k 等
- ✅ **Doubao**：doubao-seed-1-6-lite 等

#### MCP工具系统
- ✅ **MCP服务器**：基于FastMCP的异步服务器
- ✅ **MCP客户端**：线程化异步客户端，支持任务队列
- ✅ **TaskManager工具**：3个工具（已启用）
- ✅ **Mathematics工具**：6个工具（已启用）
- ✅ **DatabaseEditor工具**：12个工具（已实现但被注释）
- ✅ **FileEditor工具**：10个工具（已实现但被注释）
- ✅ **WorkspaceManager工具**：4个工具（已实现但被注释）
- ✅ **DataInquire工具**：10个工具（已实现但被注释）

#### 其他功能
- ✅ **文件监控系统**：基于watchdog（已实现但未集成）
- ✅ **Web配置界面**：Flask应用，API密钥管理
- ✅ **配置验证器**：ConfigValidator

### ⏳ 规划中功能

#### 服务器架构（高优先级）
- ⏳ **网络通信层**：FastAPI/WebSocket/gRPC支持
- ⏳ **会话管理器**：多用户会话隔离
- ⏳ **连接池管理**：高效的连接复用
- ⏳ **AuthCore模块**：用户认证、注册、登录
- ⏳ **权限系统**：资源级权限控制、用户角色管理

#### 功能增强（中优先级）
- ⏳ **文件监控集成**：将AllEventsHandler集成到主流程
- ⏳ **启用更多MCP工具**：取消注释已实现的30+工具
- ⏳ **AI实例池**：支持并发请求的实例池
- ⏳ **客户端SDK**：Python、JavaScript、Go客户端

#### 模型扩展（低优先级）
- ⏳ **Claude**：claude-3-opus, claude-3-sonnet 等
- ⏳ **Gemini**：gemini-pro, gemini-ultra 等
- ⏳ **ChatGPT**：gpt-4, gpt-3.5-turbo 等
- ⏳ **Xinhuo**：generalv3.5 等

### ⚠️ 已知问题

1. **文件监控未集成**
   - 状态：AllEventsHandler已实现但未在main.py中启动
   - 影响：无法实时感知文件变化

2. **大部分MCP工具被注释**
   - 状态：30+工具已实现但被注释
   - 影响：功能受限，仅能使用9个工具

3. **部分模型未实现**
   - 状态：Claude、Gemini、ChatGPT、Xinhuo文件存在但未实现
   - 影响：无法使用这些模型

4. **缺少多用户支持**
   - 状态：当前为单用户模式
   - 影响：无法支持并发访问，权限系统形同虚设

---

## 10. 快速开始

### 10.1 安装依赖

```bash
# 核心依赖
pip install openai watchdog

# MCP 支持
pip install fastmcp

# Web 配置界面（可选）
pip install flask flask-cors

# Qwen 模型 token 计算（可选）
pip install transformers
```

### 10.2 配置 API 密钥


#### 手动编辑配置文件

编辑 [module/AICore/role/secret_key.json](module/AICore/role/secret_key.json)：

```json
{
  "deepseek": {
    "api_key": "your_deepseek_api_key_here",
    "base_url": "https://api.deepseek.com",
    "model": "deepseek-reasoner"
  },
  "qwen": {
    "api_key": "your_qwen_api_key_here",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model": "qwen-turbo"
  }
}
```

### 10.3 运行主程序（单用户模式）

```bash
python main.py
```

### 10.4 未来：运行服务器模式（规划中）

```bash
# 启动服务器
python server.py --host 0.0.0.0 --port 8000

# 客户端连接
python client.py --server ws://localhost:8000
```

---

## 11. 使用示例

### 11.1 简单对话

```
用户：你好
AI：你好！我是AgentCore智能助手，有什么可以帮助你的吗？
```

### 11.2 数学计算

```
用户：计算 123 * 456
AI：[调用Mathematics.multiply工具]
AI：123 * 456 = 56088
```

### 11.3 复杂任务（规划中，需启用更多工具）

```
用户：分析项目中所有Python文件的函数定义
AI：[状态机流转：COMPLEX_TASK_PLANNING → MODEL_B_EXECUTING]
AI：[知识AI调用WorkspaceManager和FileEditor工具]
AI：我找到了15个Python文件，共包含42个函数定义...
```

---

## 12. 开发指南

### 12.1 添加新的AI模型

1. 在 [module/AICore/Model/](module/AICore/Model/) 创建新模型文件
2. 实现模型接口（参考 [deepseek.py](module/AICore/Model/deepseek.py)）
3. 在 [config.json](module/AICore/role/config.json) 添加模型配置
4. 在 [secret_key.json](module/AICore/role/secret_key.json) 添加API密钥

### 12.2 添加新的MCP工具

1. 在 [module/MCP/server/Tools/](module/MCP/server/Tools/) 创建工具文件
2. 使用 `@mcp.tool()` 装饰器定义工具函数
3. 在 [MCPServer.py](module/MCP/server/MCPServer.py) 中注册工具
4. 更新知识AI的系统提示词，告知新工具的用法

### 12.3 修改状态机流程

编辑 [module/Agent/Agent.py](module/Agent/Agent.py)：
- 添加新状态：在 `State` 枚举中添加
- 修改状态转换：在 `_transition()` 方法中添加转换逻辑
- 添加状态处理：实现对应的状态处理方法

---

## 13. 文档索引

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 详细的项目目录结构和模块说明
- [README_USAGE.md](README_USAGE.md) - OPEN_AI 类使用指南


---

## 14. 常见问题

### Q1: 为什么大部分MCP工具被注释了？
A: 项目处于早期开发阶段，为了简化测试，只启用了核心工具。可以在 [MCPServer.py](module/MCP/server/MCPServer.py) 中取消注释来启用更多工具。

### Q2: 如何支持多用户并发？
A: 当前为单用户模式。多用户支持需要实现网络通信层、会话管理器和权限系统，详见第8章的实现路线图。

### Q3: 文件监控系统为什么没有启动？
A: AllEventsHandler已实现但未集成到主流程。需要在 [main.py](main.py) 中启动文件监控器并将事件注入到AI上下文。

### Q4: 如何切换AI模型？
A: 编辑 [config.json](module/AICore/role/config.json)，修改 `dialogue_ai` 和 `knowledge_ai` 的模型配置。

### Q5: 权限系统什么时候实现？
A: 权限系统是多用户服务器架构的核心组件，计划在实现网络通信层后开发（高优先级）。

---

