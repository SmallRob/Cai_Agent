# asdm-req-domain-context-build: 构建领域全维度上下文

## 目的

为指定业务域一次性构建包含所有维度的上下文文档，让 AI 能够完整理解该业务域的系统情况。

**前置条件**：已执行 `/asdm-req-context-init` 生成了全局索引

**兼容范围**：同时支持后端代码库（Java/Go/Node.js）和前端代码库（Vue/React）

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| 领域名 | String | 是 | 要构建上下文的目标领域名称 |

## 上下文维度

本 action 一次性生成以下五个维度的内容：

| 维度 | 内容 | 目的 |
|------|------|------|
| 业务能力 | 核心业务能力列表 | 让 AI 知道该域能做什么 |
| 业务流程 | 核心业务流程 | 让 AI 知道业务如何运转 |
| 数据模型 | 核心实体和关系 | 让 AI 知道管理哪些数据 |
| 业务规则 | 约束和限制条件 | 让 AI 知道有哪些限制 |
| 用户角色 | 角色和权限 | 让 AI 知道有哪些用户类型 |

## 构建步骤

### 步骤 1: 识别项目类型

```bash
# 判断项目类型
if [ -d "src/views" ] || [ -d "src/pages" ] || [ -f "package.json" ]; then
    PROJECT_TYPE="FRONTEND"
elif [ -d "src/main/java" ] || [ -f "pom.xml" ] || [ -f "go.mod" ]; then
    PROJECT_TYPE="BACKEND"
fi
```

### 步骤 2: 定位领域代码

1. 读取 `.asdm/contexts/requirements/index.md` 了解项目业务域划分
2. 在代码中定位该业务域的代码结构
3. 识别核心代码文件

#### 后端项目识别策略

| 代码类型 | 识别特征 | 示例 |
|----------|----------|------|
| Controller | `@RestController` / `@Controller` | `UserController.java` |
| Service | `@Service` | `UserService.java` |
| Repository | `@Repository` / `extends JpaRepository` | `UserRepository.java` |
| Entity | `@Entity` | `User.java` |

#### 前端项目识别策略

| 代码类型 | 识别特征 | 示例 |
|----------|----------|------|
| 页面组件 | `views/` 或 `pages/` 下的组件 | `views/user/Login.vue` |
| 业务组件 | `components/` 下的业务组件 | `components/user/UserCard.vue` |
| 路由配置 | `router/` 下的配置 | `router/index.ts` |
| 状态管理 | `stores/` 或 `store/` 下的配置 | `stores/user.ts` |
| API 服务 | `api/` 或 `services/` 下的请求 | `api/user.ts` |

### 步骤 3: 扫描并分析代码

#### 后端项目分析

**扫描范围**：
- 核心 Service 类：识别业务能力
- Controller 类：识别对外接口
- Entity 类：识别数据模型
- 验证逻辑：识别业务规则
- 认证模块：识别用户角色

**分析方法**：
1. 分析方法名获取能力意图
2. 阅读关键方法的注释和业务逻辑
3. 从参数和返回值理解数据流向
4. 从异常处理理解业务约束

#### 前端项目分析

**扫描范围**：
- 页面组件（.vue / .tsx）：识别页面功能
- 路由配置：识别页面关系和权限
- Store/Pinia：识别状态管理能力
- API 调用：识别数据操作

**分析方法**：
1. 分析路由定义理解页面关系
2. 阅读页面组件的模板和逻辑
3. 分析 API 接口理解数据操作
4. 分析 Store 状态理解业务状态

### 步骤 4: 抽取并转化内容

**核心原则**：从代码抽取概要信息，用业务语言描述

#### 后端抽取示例

```
❌ 不好的抽取（代码片段）
"public Order createOrder(OrderDTO dto) {
    if (dto.getAmount() <= 0) throw new IllegalArgumentException();
    Order order = new Order();
    order.setAmount(dto.getAmount());
    // ... 100行代码
}"

✓ 好的抽取（业务描述）
"## 订单创建能力

**能力描述**：客户可以创建新订单

**输入**：商品列表、客户信息、收货地址、支付方式

**业务流程**：
1. 验证商品可售
2. 计算订单金额
3. 扣减库存
4. 创建订单记录

**业务规则**：
- 订单金额必须 > 0
- 每个订单最多 99 个商品

**输出**：订单编号、订单状态"
```

#### 前端抽取示例

```
❌ 不好的抽取（代码片段）
"const UserList: React.FC = () => {
  const [users, setUsers] = useState([]);
  useEffect(() => { fetchUsers(); }, []);
  return <Table dataSource={users}>...</Table>;
}"

✓ 好的抽取（业务描述）
"## 用户列表页面

**页面功能**：展示系统中所有用户的信息列表

**页面元素**：
- 搜索框：支持按用户名、手机号搜索
- 表格：展示用户信息（ID、用户名、手机号、状态、注册时间）
- 操作列：编辑、禁用/启用、删除

**交互流程**：
1. 页面加载 → 自动请求用户列表
2. 点击搜索 → 按条件过滤列表
3. 点击编辑 → 跳转用户编辑页
4. 点击删除 → 弹出确认框 → 删除用户

**关联数据**：
- 用户信息（用户名、手机号、邮箱）
- 用户状态（启用/禁用）

**权限要求**：
- 仅管理员可访问此页面
- 仅管理员可执行编辑、删除操作"
```

### 步骤 5: 生成领域索引

使用 `specs/domain/index.md` 模板生成域索引：

**文件**：`.asdm/contexts/requirements/domains/{领域名}/index.md`

**内容**：
- 领域一句话描述
- 核心能力列表（3-5 条）
- 关联领域链接
- context.md 的入口说明

**前端/后端差异**：

| 维度 | 后端描述重点 | 前端描述重点 |
|------|-------------|-------------|
| 能力 | Service 方法 | 页面功能 |
| 流程 | 后端处理流程 | 页面交互流程 |
| 数据 | 数据库实体 | 页面数据来源 |

### 步骤 6: 生成领域全维度上下文

使用 `specs/domain/context.md` 模板生成完整上下文：

**文件**：`.asdm/contexts/requirements/domains/{领域名}/context.md`

**大小限制**：< 10KB

**内容结构**：
1. 业务能力（3-5 个核心能力）
2. 业务流程（2-3 个核心流程）
3. 数据模型（3-5 个核心实体/数据结构）
4. 业务规则（3-5 条核心规则）
5. 用户角色（2-4 个角色）

### 步骤 7: 更新全局索引

在 `index.md` 的领域列表中，添加该领域的入口链接。

## 输出摘要

| 文件 | 位置 | 大小 |
|------|------|------|
| 领域索引 | `domains/{领域名}/index.md` | < 3KB |
| 全维度上下文 | `domains/{领域名}/context.md` | < 10KB |
| 全局索引 | `index.md` | 已更新 |

## 使用方法

```bash
# 构建单个领域上下文
/asdm-req-domain-context-build 用户域

# 构建多个领域上下文
/asdm-req-domain-context-build 用户域,订单域,支付域
```

## 注意事项

1. **内容要业务化**：用业务语言描述，不要直接复制代码
2. **控制粒度**：每个维度聚焦核心内容，不要追求完整
3. **前端/后端适配**：
   - 后端：强调 API 能力、数据实体、后端规则
   - 前端：强调页面功能、交互流程、前端验证
4. **标注来源**：可以标注关键代码位置，便于后续追溯
5. **留有扩展**：context.md 控制在 10KB 内，细节按需深入

## 抽取质量标准

| 标准 | 说明 |
|------|------|
| 完整性 | 覆盖该领域的主要能力、流程、数据 |
| 准确性 | 描述与代码实现一致 |
| 可读性 | 用业务语言，AI 能理解 |
| 简洁性 | 聚焦核心，细节按需补充 |

---

*本文件由 Context Builder Requirements 生成*
