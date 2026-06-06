# Instructions for asdm-init-spec action

## Metadata

```json
{
  "guid": "c1d2e3f4-a5b6-7c8d-9e0f-a1b2c3d4e5f6",
  "name": "asdm-init-spec",
  "displayName": "Initialize New Spec",
  "description": "Initialize a new ASDM spec project with basic directory structure and README.md template",
  "toolset": {
    "guid": "spec-builder-guid-placeholder",
    "id": "spec-builder",
    "name": "Spec Builder",
    "version": "0.0.1"
  },
  "scenario": "规范开发"
}
```

## Purpose
This instruction guides the AI model to initialize a new spec project. It collects essential information from the developer, creates the basic directory structure, and generates a README.md template with placeholders for the developer to complete.

## Language Setting

默认使用**中文（简体中文）**作为输出语言。所有生成的文件、注释和文档均使用中文，并遵循中文写作规范。

如需切换语言，可在工作区根目录创建 `.asdm/config.json` 配置：
```json
{
  "language": "zh"
}
```
支持的语言：`zh`（中文，默认）、`en`（英文）。

## Context Injection

Before initializing a spec, the AI model should read and understand existing specs for reference:

### Context Files to Read (Optional)

1. **Existing Spec Examples** (Recommended)
   - Path: `.asdm/specs/*/README.md`
   - Purpose: Understand common patterns and conventions

2. **Spec README Spec Template** (Reference)
   - Path: `.asdm/toolsets/spec-builder/spec/spec-readme-spec.md`
   - Purpose: Follow the README template structure

## Steps to Initialize New Spec

### 1. Receive Spec Information

Collect the following information from the developer:

#### Required Information:
- **Spec ID**: Unique identifier for the spec
  - Format: lowercase letters, numbers, and hyphens only
  - Examples: `typescript`, `api-response`, `reactjs`, `vue3-composition-api`
  - Must be unique among existing specs

- **Spec Name**: Display name for the spec
  - Can include spaces and mixed case
  - Examples: "TypeScript Development Specs", "API Response Standard"
  - Should be descriptive of the technology or domain

- **Spec Description**: Brief description of what the spec covers
  - One or two sentences
  - Should explain the spec's purpose and scope

- **Spec Scenario**: Usage scenario for the spec
  - Options: `frontend`, `backend`, `backend-api`
  - Describes what type of technology the spec covers

#### Optional Information (use defaults if not provided):
- **Spec Version**: Default: `1.0.0`
- **Created Date**: Default: today's date (ISO-8601 format)
- **Creator**: Default: "ASDM Platform"

**Prompt Template**:
```
Please provide the following information for your new spec:

1. Spec ID (required): [e.g., typescript, api-response]
2. Spec Name (required): [e.g., TypeScript Development Specs]
3. Spec Description (required): [Brief description of what the spec covers]
4. Spec Scenario (required): [frontend/backend/backend-api]
5. Spec Version (optional, default: 1.0.0):
6. Creator (optional, default: ASDM Platform):
```

### 2. Validate Spec ID

Check if the spec ID is unique:
- List existing specs in `.asdm/specs/`
- If spec ID already exists, ask the developer to choose a different ID
- Spec ID should not conflict with existing specs

**Validation Rules**:
- Must be lowercase letters, numbers, and hyphens only
- Must not be empty
- Must be unique among existing specs
- Should be descriptive of the technology

### 3. Create Spec Directory Structure

Create the following directory structure:

```bash
mkdir -p .asdm/specs/<spec-id>
```

### 4. Generate README.md Template

Create a README.md file following the template from `.asdm/toolsets/spec-builder/spec/spec-readme-spec.md`:

The README.md should include:

```markdown
# <Spec Name> Specs

This directory contains coding standards, guidelines, and best practices for <technology> development within the ASDM ecosystem.

## Overview

<Spec Name> specs provide comprehensive guidance for:
- [Developer completes this section with main areas covered]
- [Point 2]
- [Point 3]

## Available Specifications

### 1. <Content File Name>
**File**: [filename.md](filename.md)

Covers:
- [Developer completes this section with what this file covers]
- [Point 2]
- [Point 3]

[Developer adds more content files as needed]

## Related Specifications

- [Developer adds related specs if any]

## Version

Current version: <version>
Last updated: <created-date>
```

**IMPORTANT**: The README.md is written by the developer. This is a template with placeholders that the developer should complete.

### 5. Create Placeholder Files

Create empty placeholder files for future use:

- `.gitkeep` - Keeps the directory in version control

### 6. Generate Initialization Summary

Create a summary for the developer:

```markdown
# Spec Initialization Summary

## Spec Information
- **Spec ID**: <spec-id>
- **Spec Name**: <Spec Name>
- **Spec Version**: <version>
- **Spec Scenario**: <scenario>
- **Description**: <spec-description>
- **Creator**: <creator>

## Created Files
- `.asdm/specs/<spec-id>/README.md` (Template - needs completion)

## Directory Structure
```
.asdm/specs/<spec-id>/
└── README.md
```

## Next Steps
1. Complete the README.md file by filling in all placeholders
2. Use `/asdm-define-spec-content <spec-id>` to define content files
3. Use `/asdm-generate-manifest <spec-id>` to generate manifest.json
4. Use `/asdm-complete-spec <spec-id>` to finalize the spec

## Important Notes
- The README.md is your primary documentation - complete it thoroughly
- Reference existing specs for patterns (e.g., typescript, reactjs, api-response)
- Follow the spec README template from `.asdm/toolsets/spec-builder/spec/spec-readme-spec.md`
- Consider what content files you'll need (coding standards, best practices, etc.)
```

Save this summary to a temporary location or display it to the developer.

## Execution Guidelines

### When to Use This Action

Use this action when:
- You want to start developing a new spec
- You need a structured starting point for spec development
- You want to ensure your spec follows ASDM conventions

### Initialization Guidelines

When initializing a new spec:

1. **Choose a Good ID**: Use descriptive, lowercase IDs with hyphens
2. **Write a Clear Description**: The description should be concise but informative
3. **Start with README**: Focus on completing the README.md first
4. **Think About Structure**: Consider what content files you'll need
5. **Follow Conventions**: Align with existing specs and ASDM principles

### Spec ID Guidelines

When choosing a spec ID:
- Use lowercase letters only
- Use hyphens to separate words
- Avoid special characters and spaces
- Keep it short but descriptive
- Ensure it's unique

**Good Examples**:
- `typescript`
- `api-response`
- `reactjs`
- `vue3-composition-api`
- `java-springboot-jpa`

**Bad Examples**:
- `MySpec` (uppercase)
- `my spec` (spaces)
- `my_spec` (underscores)
- `spec-001` (not descriptive)

### Scenario Guidelines

When choosing a scenario:
- `frontend` - For UI frameworks, CSS, client-side technologies
- `backend` - For server-side frameworks, databases, services
- `backend-api` - For API standards, response formats, error codes

## Usage

To use this instruction, the AI model should:
1. Detect the response language
2. Read existing specs for reference (optional but recommended)
3. Collect spec information from the developer (ID, name, description, scenario, version, creator)
4. Validate the spec ID is unique
5. Create the directory structure
6. Generate a README.md template with placeholders
7. Create placeholder files
8. Present an initialization summary with next steps

## Output Summary

After completing the initialization, the following will be generated:
- Spec directory: `.asdm/specs/<spec-id>/`
- README.md template: `.asdm/specs/<spec-id>/README.md` (developer completes)

The README.md is a template that the developer needs to complete. It contains placeholders and guidance for filling in the spec's content files and coverage areas.
