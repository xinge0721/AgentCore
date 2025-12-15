# API密钥配置管理系统

这是一个用于管理AI模型API密钥和提示词的Web应用程序。

## 功能特性

- 🔐 统一管理多个AI模型的API密钥
- 📝 **提示词在线编辑** - 直接在网页中编辑AI的System Prompt
- 🎨 美观的现代化界面设计
- 💾 自动保存配置到JSON文件
- ✅ 实时配置状态指示
- 🔄 支持的AI模型：
  - DeepSeek
  - 通义千问 (Qwen)
  - Kimi (月之暗面)
  - 豆包 (Doubao)
  - 讯飞星火

## 安装步骤

1. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 启动服务器：
```bash
python app.py
```

2. 在浏览器中访问：
```
http://localhost:5000
```

3. 在网页界面中：
   - 输入各个AI模型的API密钥
   - 编辑AI提示词（System Prompt）
   - 点击"保存配置"按钮

4. 修改提示词后，需要**重启AI程序**才能生效

## 配置文件

- `../role/secret_key.Json` - 存储所有AI模型的配置
- `../role/Char.JSON` - 存储AI的System Prompt提示词

## 提示词编辑说明

提示词编辑界面位于页面最下方，支持：
- ✏️ 多行文本编辑，等宽字体显示
- 🔄 实时保存到 `Char.JSON` 文件
- ✅ 配置状态实时指示
- 📏 可调整编辑器高度

**注意**：修改提示词后，必须重启AI程序（`main.py`）才会加载新的提示词配置！

## 注意事项

- 请妥善保管您的API密钥，不要泄露给他人
- 配置文件会被自动更新，请确保有写入权限
- 建议在局域网内使用，不要将服务暴露到公网

### 豆包模型特别说明

豆包（Doubao）使用火山方舟平台，需要特别注意：
- **Model** 字段需要填写 **endpoint ID**（格式：`ep-xxxxxxxxxxxxxx`），而不是模型名称
- 获取 endpoint ID 的步骤：
  1. 登录火山方舟控制台：https://console.volcengine.com/ark
  2. 进入"推理接入点"页面
  3. 创建或找到您的豆包模型接入点
  4. 复制对应的 endpoint ID

## 技术栈

- 后端：Flask (Python)
- 前端：HTML + CSS + JavaScript
- 数据存储：JSON文件

