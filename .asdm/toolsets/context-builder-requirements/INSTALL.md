# 安装指南

## 安装步骤

### 步骤 1: 复制工具集

将 `context-builder-requirements-v0.1.0` 目录复制到项目的 `.asdm/toolsets/` 目录：

```bash
cp -r context-builder-requirements-v0.1.0 <your-project>/.asdm/toolsets/
```

### 步骤 2: 注册工具集

在 CodeBuddy 的工具集注册界面中注册此工具集。

### 步骤 3: 验证安装

在项目中执行以下命令验证安装：

```bash
# 应该看到以下命令
/asdm-req-context-init
/asdm-req-domain-context-build
/asdm-req-process-context-build
/asdm-req-data-context-build
/asdm-req-rules-context-build
/asdm-req-context-update
```

## 卸载

删除工具集目录即可：

```bash
rm -rf <your-project>/.asdm/toolsets/context-builder-requirements-v0.1.0
```

## 版本更新

1. 备份现有上下文文件
2. 删除旧版本
3. 安装新版本
4. 重新执行上下文构建
