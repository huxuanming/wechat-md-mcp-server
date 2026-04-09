# 微信 Markdown 转换 MCP

这个 MCP 服务提供两个工具：
- `convert_markdown_to_wechat_html`: 把 Markdown 转成可用于公众号排版流程的内联样式 HTML。
- `list_wechat_themes`: 返回可用主题。
- `convert_markdown_to_wechat_clipboard`: 把 Markdown 转换后直接写入 macOS 剪切板（HTML 富文本）。

转换成功后会自动缓存一份 HTML 到：
- `./.cache/wechat-mcp/`

> 说明：公众号后台会过滤部分 HTML。实践上建议把输出先粘到 Doocs/md、WeMD 或 mdnice 再复制到公众号后台，兼容性更稳。

## 文件
- `wechat_mcp_server.py`

## 运行
```bash
python3 wechat_mcp_server.py
```

## 无网络环境使用（推荐）
如果你的 MCP 容器/沙盒禁网，避免用 `uvx --from git+https://...` 拉取源码，直接用本地路径启动：

```bash
python3 -u /path/to/wechat_mcp_server.py
```

## 用 uvx 封装并调用
推荐通过 GitHub 直接调用：

```bash
uvx --from "git+https://github.com/huxuanming/wechat-md-mcp-server.git" wechat-md-mcp-server
```

如果你是本地开发，也可以用相对路径：

```bash
uvx --from ./wechat-md-mcp-server wechat-md-mcp-server
```

## MCP 配置示例
把下面配置到你的 MCP 客户端（按客户端格式调整）：

```json
{
  "mcpServers": {
    "wechat-md-mcp-server": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/huxuanming/wechat-md-mcp-server.git", "wechat-md-mcp-server"]
    }
  }
}
```

> 说明：`mcpServers` 里的 key 只是客户端侧的别名，可随意命名。

## 工具参数

### 1) `convert_markdown_to_wechat_html`
输入：
- `markdown` (string, required)
- `theme` (string, optional): `default | tech | warm | apple | wechat-native`
- `title` (string, optional)

输出：
- `text` 内容为 HTML 字符串（`<article>...</article>`）
- `meta.cacheHtmlPath` 返回缓存文件路径

### 2) `list_wechat_themes`
输入：空对象
输出：主题列表

### 3) `convert_markdown_to_wechat_clipboard`
输入：
- `markdown` (string, required)
- `theme` (string, optional): `default | tech | warm | apple | wechat-native`
- `title` (string, optional)

输出：
- JSON 文本，包含 `ok / htmlLength / theme`
- 包含 `cacheHtmlPath`
- 剪切板会被设置为 `HTML` 富文本类型，可直接粘贴公众号编辑器。

> 说明：剪切板写入依赖 macOS 的 `osascript`，非 macOS 环境会失败并返回错误。

## 支持的 Markdown 语法
- 标题：`#` 到 `######`
- 段落
- 无序/有序列表
- 引用：`>`
- 分割线：`---` 或 `***`
- 行内强调：`**bold**`、`*italic*`
- 行内代码：`` `code` ``
- 代码块：```lang ... ```
- 链接：`[text](https://...)`

## 快速验证（本地）
```bash
PYTHONPYCACHEPREFIX=/tmp python3 - <<'PY'
import wechat_mcp_server as s
md = "# 标题\n\n这是**测试**，带[链接](https://example.com)和`代码`。"
print(s.parse_markdown(md, theme_name="default")[:300])
PY
```

## 缓存目录
默认会尝试写入用户缓存目录；如果权限受限，可设置：
- `WECHAT_MCP_CACHE_DIR=/tmp/wechat-mcp`

## 后续可扩展
- 增加“公众号兼容过滤器”（自动降级不兼容标签）。
- 增加封面导语卡片、参数对比卡片等业务组件。
- 增加“一键输出纯文本 + 富文本双版本”。
