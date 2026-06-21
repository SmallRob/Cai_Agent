## 技能：AI 文档编写（Doc Writing）

> 适用场景：利用 AI Agent 自动生成、更新和审查项目文档，提高文档编写效率和质量。

### 一、目标

- 自动化文档编写流程，减少人工工作量
- 保持文档与代码的一致性
- 提供标准化的文档结构和风格
- 支持多种文档类型（README、API 文档、架构文档等）

### 二、核心能力

#### 2.1 文档生成

根据代码库自动生成文档，支持以下类型：

| 类型 | 说明 | 默认输出 |
|------|------|----------|
| readme | 项目说明文档 | README.md |
| api | API 接口文档 | docs/API.md |
| architecture | 架构文档 | docs/ARCHITECTURE.md |
| changelog | 变更日志 | CHANGELOG.md |
| contributing | 贡献指南 | CONTRIBUTING.md |

#### 2.2 文档更新

基于代码变更自动更新文档：

- 分析 Git diff 识别变更范围
- 评估变更对文档的影响
- 增量更新受影响的章节
- 保留文档整体结构

#### 2.3 文档审查

检查文档质量和一致性：

- 完整性检查：是否包含必要章节
- 准确性检查：内容是否与代码一致
- 可读性检查：结构是否清晰
- 规范性检查：是否遵循 Markdown 规范

### 三、使用方式

#### 3.1 CLI 命令

```bash
# 生成 README
cai-agent doc generate --type readme

# 生成 API 文档
cai-agent doc generate --type api --source src/ --output docs/API.md

# 更新文档
cai-agent doc update --file README.md --diff HEAD~3

# 审查文档
cai-agent doc review --file README.md --json

# 列出支持的文档类型
cai-agent doc types --json
```

#### 3.2 对话提示

可以在对话中使用以下提示：

> 「请帮我生成项目 README 文档，包含项目介绍、安装说明、使用方法和配置说明。」

> 「请审查 docs/API.md 文档，检查是否有遗漏的接口或过时的内容。」

> 「请基于最近的代码变更更新 CHANGELOG.md。」

### 四、文档编写最佳实践

#### 4.1 结构清晰

- 使用适当的标题层级（H1 > H2 > H3）
- 每个章节聚焦一个主题
- 使用列表和表格组织信息

#### 4.2 内容准确

- 确保代码示例可运行
- 保持参数说明与实际一致
- 及时更新过时内容

#### 4.3 语言简洁

- 使用简洁明了的句子
- 避免冗余和重复
- 使用主动语态

#### 4.4 示例丰富

- 提供实际的代码示例
- 包含常见使用场景
- 说明错误处理方式

### 五、工作流集成

#### 5.1 文档生成工作流

```json
{
  "description": "三阶段文档生成：探索代码 → 分析结构 → 生成文档",
  "steps": [
    {"name": "explore", "role": "explorer", "goal": "探索代码库结构"},
    {"name": "analyze", "role": "default", "goal": "分析代码细节"},
    {"name": "write", "role": "default", "goal": "生成文档内容"}
  ]
}
```

#### 5.2 文档更新工作流

```json
{
  "description": "文档更新：分析变更 → 识别影响 → 更新文档",
  "steps": [
    {"name": "diff", "role": "explorer", "goal": "分析代码变更"},
    {"name": "impact", "role": "default", "goal": "评估文档影响"},
    {"name": "update", "role": "default", "goal": "更新文档内容"}
  ]
}
```

### 六、注意事项

1. **安全性**：文档生成不应修改源代码文件
2. **可逆性**：所有文档更新应可回滚（使用 Git）
3. **一致性**：生成的文档应与项目风格保持一致
4. **国际化**：根据项目语言选择文档语言
5. **性能**：大型代码库应限制分析深度

### 七、与其他技能的配合

- **docs-sync**：文档同步更新
- **plan-then-execute**：先规划再执行文档编写
- **code-review**：代码审查时同步审查文档
- **release-prep**：发布前更新文档
