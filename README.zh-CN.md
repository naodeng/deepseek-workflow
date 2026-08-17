# <img src='Workflow/icon.png' width='45' align='center' alt='icon'> DeepSeek Alfred Workflow

<p align="center">
  <a href="README.md">English</a> · <b>简体中文</b>
</p>

在 Alfred 中直接与 [DeepSeek](https://www.deepseek.com/) 对话——这是 [Alfred OpenAI Workflow](https://github.com/alfredapp/openai-workflow) 的一个分支，改为调用 [DeepSeek API](https://api-docs.deepseek.com/)（与 OpenAI 兼容）而非 OpenAI。

## 安装与配置

1. 注册 DeepSeek 账号并[登录](https://platform.deepseek.com/)。
2. 在 [API keys 页面](https://platform.deepseek.com/api_keys) 点击 `Create new API key` 创建密钥。
3. 复制密钥并填入 Workflow 的 [Configuration](https://www.alfredapp.com/help/workflows/user-configuration/)（配置项）中的 `DeepSeek API Key`。
4. 双击 `DeepSeek.alfredworkflow` 导入 Alfred。

## 使用方法

### DeepSeek 聊天

通过 `deepseek` 关键字、[Universal Action](https://www.alfredapp.com/help/features/universal-actions/)（通用操作）或 [Fallback Search](https://www.alfredapp.com/help/features/default-results/fallback-searches/)（回退搜索）查询 DeepSeek。

输入 `deepseek` 后跟你的问题：

* <kbd>↩&#xFE0E;</kbd> 提出新问题。
* <kbd>⌘</kbd><kbd>↩&#xFE0E;</kbd> 清空并开始新对话。
* <kbd>⌥</kbd><kbd>↩&#xFE0E;</kbd> 复制最后一条回答。
* <kbd>⌃</kbd><kbd>↩&#xFE0E;</kbd> 复制完整对话。
* <kbd>⇧</kbd><kbd>↩&#xFE0E;</kbd> 停止生成回答。

回答会以流式方式实时显示在 Alfred 文本视图中，每段对话保存在 workflow 数据目录下的 `chat.json` 中。

#### 聊天记录

在 `deepseek` 关键字下按 <kbd>⌥</kbd><kbd>↩&#xFE0E;</kbd> 查看聊天记录。每条记录以第一个问题为标题、最后一个问题为副标题显示。

按 <kbd>↩&#xFE0E;</kbd> 归档当前对话并加载所选记录。旧对话可通过 `Delete` [Universal Action](https://www.alfredapp.com/help/features/universal-actions/) 删除，也可用 [File Buffer](https://www.alfredapp.com/help/features/file-search/#file-buffer) 多选。

### 模型

支持 DeepSeek 两个公开模型：

| 配置项名称 | 模型 ID | 说明 |
| --- | --- | --- |
| DeepSeek Chat | `deepseek-chat` | 通用对话模型（DeepSeek-V3），默认。 |
| DeepSeek Reasoner | `deepseek-reasoner` | 推理模型（DeepSeek-R1），思考过程通过 `reasoning_content` 流式输出并显示在对话中。 |

也可设置 `deepseek_model_override` 在运行时覆盖模型（例如指向自定义的 `deepseek-*` 部署）。

## 配置项

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `deepseek_api_key` | — | 你的 DeepSeek API 密钥（必填）。 |
| `deepseek_keyword` | `deepseek` | 启动对话的关键字。 |
| `deepseek_history_save` | 开 | 开始新对话时保存当前对话。 |
| `deepseek_model` | `deepseek-chat` | 使用的模型。 |
| `max_context` | 24 | 发送的最近问答条数。 |
| `timeout_seconds` | 10 | 连接停滞多少秒后放弃。 |
| `system_prompt` | — | 引导 DeepSeek 回答风格的初始提示词。 |
| `deepseek_api_endpoint` | `https://api.deepseek.com/v1/chat/completions` | API 端点，可指向任意 OpenAI 兼容服务（如代理）。 |
| `deepseek_model_override` | — | 可选的运行时模型覆盖。 |

## 说明

* DeepSeek API 与 OpenAI 兼容，本 workflow 只调用 chat completions 接口。原 workflow 的 DALL·E 图片生成流程未包含，因为 DeepSeek 不提供图片生成 API。
* DeepSeek 不需要组织（Organization）请求头，已移除 `OpenAI-Organization`。

## 开发

`info.plist` 由上游 [alfredapp/openai-workflow](https://github.com/alfredapp/openai-workflow) 的 plist 通过 [`tools/build_info_plist.py`](tools/build_info_plist.py) 生成；图标由 [`tools/make_icon.py`](tools/make_icon.py) 生成。

重新生成：

```bash
python3 tools/build_info_plist.py /path/to/openai-workflow/Workflow/info.plist
python3 tools/make_icon.py
```

## 许可证

MIT——见 [LICENSE](LICENSE)。原 [Alfred OpenAI Workflow](https://github.com/alfredapp/openai-workflow) © Vítor Galvão，MIT 许可。
