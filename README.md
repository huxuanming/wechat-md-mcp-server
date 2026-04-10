# 微信 Markdown 转换 MCP

把 Markdown 转成适合微信公众号的内联样式 HTML。服务只负责渲染输出，复制富文本交给用户现有工作流（浏览器、Doocs/md、WeMD、mdnice 等）。

## 工具

| 工具 | 说明 |
|------|------|
| `convert_markdown_to_wechat_html` | Markdown → 内联样式 HTML 字符串 |
| `open_wechat_html_in_browser` | 将 HTML 存入缓存并在浏览器中打开，全选复制后可直接粘贴到公众号编辑器 |
| `list_wechat_themes` | 返回可用主题列表 |

转换成功后自动缓存 HTML 到 `./.cache/wechat-mcp/`，可通过 `WECHAT_MCP_CACHE_DIR` 环境变量覆盖。

## 运行

```bash
uvx --from "git+https://github.com/huxuanming/wechat-md-mcp-server.git" wechat-md-mcp-server
```

本地开发：

```bash
uvx --from . wechat-md-mcp-server
```

查看可用工具：

```bash
uvx --from . wechat-md-mcp-server --list-tools
```

## MCP 配置示例

**远程（GitHub）：**

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

**本地开发（推荐用 `uv run`，自动感知代码变化）：**

```json
{
  "mcpServers": {
    "wechat-md-mcp-server": {
      "command": "uv",
      "args": ["--directory", "/path/to/wechat-md-mcp-server", "run", "wechat-md-mcp-server"]
    }
  }
}
```

> 本地开发不要用 `uvx --from /path`，uvx 会缓存构建产物，代码修改后不会自动重建。

## 工具参数

### `convert_markdown_to_wechat_html`

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `markdown` | string | 是 | 源 Markdown 文本 |
| `theme` | string | 否 | 主题，见下方列表，默认 `default` |
| `title` | string | 否 | 文章标题，渲染为 h1 |

输出：HTML 字符串（`<article>...</article>`）。

### `list_wechat_themes`

无参数，返回主题名称和描述列表。

## 主题

| 名称 | 风格 |
|------|------|
| `default` | 通用企业风 |
| `tech` | 简洁技术风 |
| `warm` | 暖色品牌风 |
| `apple` | Apple 极简风 |
| `wechat-native` | 微信绿原生风 |

## 命令行工具

`wechat-md-convert` 可直接转换本地 Markdown 文件：

```bash
uvx --from . wechat-md-convert input.md --theme tech --out output.html
```

| 参数 | 说明 |
|------|------|
| `input` | 输入 Markdown 文件路径 |
| `--theme` | 主题（默认 `default`） |
| `--title` | 标题覆盖 |
| `--out` | 输出 HTML 路径，省略则写入缓存目录 |
| `--cache-dir` | 覆盖缓存目录 |
| `--open` | 转换完成后自动在浏览器中打开，全选复制即可粘贴到公众号编辑器 |

## 支持的 Markdown 语法

- 标题：`#` 到 `######`
- 段落、换行
- 无序列表（`-` / `*` / `+`）、有序列表
- 引用：`>`
- 分割线：`---` 或 `***`
- 粗体：`**bold**`，斜体：`*italic*`，嵌套：`**bold *italic* bold**`
- 行内代码：`` `code` ``
- 代码块：` ```lang ... ``` `
- 链接：`[text](https://...)` / `[text](#anchor)` / `[text](mailto:...)`

## 快速验证

```bash
uvx --from . python3 - <<'PY'
import server as s
md = "# 标题\n\n这是**测试**，带[链接](https://example.com)和`代码`。"
print(s.parse_markdown(md, theme_name="default")[:300])
PY
```

## 缓存目录优先级

1. `WECHAT_MCP_CACHE_DIR` 环境变量
2. `<输入文件目录>/.cache/wechat-mcp/`
3. `~/.cache/wechat-mcp/`（macOS：`~/Library/Caches/wechat-mcp/`）
4. 系统临时目录
