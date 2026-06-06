# asdm-req-context-init: 初始化需求分析上下文

## 目的

初始化需求分析上下文，建立系统能力概览的全局索引。

**前置条件**：项目已存在，具备基本代码结构。

**兼容范围**：同时支持后端代码库（Java/Go/Node.js）和前端代码库（Vue/React）

## 初始化步骤

### 步骤 1: 识别项目类型

首先判断项目类型：

```bash
# 检查前端特征
ls -la src/ | grep -E "(views|pages|components)"
if [ -d "src/views" ] || [ -d "src/pages" ] || [ -f "package.json" ]; then
    echo "FRONTEND"
fi

# 检查后端特征
if [ -d "src/main/java" ] || [ -f "pom.xml" ] || [ -f "go.mod" ]; then
    echo "BACKEND"
fi
```

### 步骤 2: 分析项目结构

根据项目类型，采用不同的分析策略：

#### 后端项目分析

1. **扫描项目基本信息**
   - 项目名称和描述（从 pom.xml / go.mod / package.json 获取）
   - 技术栈（Spring Boot / Go / Node.js 等）
   - 项目规模

2. **扫描代码结构**
   - 识别主要的业务包/模块
   - 识别核心的 Controller/Service/Repository

3. **识别业务域**
   - 基于代码结构归纳业务域
   - 确定每个业务域的核心职责

#### 前端项目分析

1. **扫描项目基本信息**
   - 项目名称和描述（从 package.json 获取）
   - 技术栈（Vue 3 / React 18 / Taro 等）
   - 项目规模

2. **扫描代码结构**
   - 识别主要的页面目录（views/ 或 pages/）
   - 识别核心组件、路由、状态管理

3. **识别功能模块**
   - 基于 views/pages 目录结构归纳模块
   - 确定每个模块的核心职责

### 步骤 3: 创建目录结构

```
.asdm/contexts/requirements/
├── index.md                           # 全局索引
│
└── domains/                           # 领域上下文目录
```

### 步骤 4: 生成全局索引

使用 `specs/index.md` 模板生成 `index.md`：

**核心要求**：
- **大小限制**：< 2KB
- 一句话描述系统
- 业务域/模块列表及简要描述
- 导航链接

**特殊处理**：

| 项目类型 | 索引内容差异 |
|----------|-------------|
| 后端 | 强调业务域、API 接口 |
| 前端 | 强调功能模块、页面路由 |

### 步骤 5: 生成系统概览（可选）

根据项目类型，生成补充说明：

**后端项目**：
- 核心 API 分组
- 微服务架构说明（如适用）

**前端项目**：
- 路由结构概览
- 状态管理概览

---

## 输出摘要

| 文件 | 说明 |
|------|------|
| `.asdm/contexts/requirements/index.md` | 全局索引 |

## 使用方法

```bash
# 初始化需求分析上下文
/asdm-req-context-init
```

## 注意事项

1. **内容来源**：从代码、配置文件、README 中抽取
2. **内容形式**：概要描述，不是代码片段
3. **项目类型识别**：
   - 后端：关注 .java / Controller / Service 结构
   - 前端：关注 .vue / .tsx / views / router 结构
4. **保持精简**：每个文件都要控制大小，便于 AI 加载

## 下一步

初始化完成后，执行：
- `/asdm-req-domain-context-build <领域名>` - 为每个领域构建上下文

**推荐流程**：
1. `/asdm-req-domain-discovery` - 先发现领域（可选但推荐）
2. `/asdm-req-context-init` - 初始化
3. `/asdm-req-domain-context-build <领域1>` - 构建领域上下文
4. `/asdm-req-domain-context-build <领域2>` - 构建领域上下文
5. ...
