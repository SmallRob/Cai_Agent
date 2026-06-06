# Instructions for asdm-define-spec-content action

## Metadata

```json
{
  "guid": "d2e3f4a5-b6c7-8d9e-0f1a-b2c3d4e5f6a7",
  "name": "asdm-define-spec-content",
  "displayName": "Define Spec Content",
  "description": "Define content files for an existing ASDM spec",
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
This instruction guides the AI model to define content files for an existing spec. It collects detailed information about each content file, generates content file templates, and updates the README.md with the file information.

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

Before defining content files, the AI model should read the spec's README.md and understand the spec context:

### Context Files to Read (Required)

1. **Spec README.md** (Required)
   - Path: `.asdm/specs/<spec-id>/README.md`
   - Purpose: Understand the spec's purpose and existing structure

2. **Spec Content Spec Template** (Reference)
   - Path: `.asdm/toolsets/spec-builder/spec/spec-content-spec.md`
   - Purpose: Follow the content file structure

3. **Existing Spec Examples** (Optional)
   - Path: `.asdm/specs/*/README.md`
   - Purpose: Understand common patterns and conventions

## Steps to Define Spec Content Files

### 1. Identify the Spec

The action receives a spec ID as input. If not provided, prompt the user to select a spec:
- List existing specs in `.asdm/specs/`
- Display spec IDs and names
- Ask user to select which spec to define content for

### 2. Validate Spec Exists

Check if the spec exists:
- Path: `.asdm/specs/<spec-id>/README.md`
- If the README.md doesn't exist, inform the user that the spec hasn't been initialized yet
- Suggest running `/asdm-init-spec <spec-id>` first

### 3. Load Spec README

Read the spec's README.md to understand:
- Spec purpose and overview
- Existing content file descriptions (if any)
- Spec scenario and scope

### 4. Collect Content File Information

Ask the developer to describe each content file for the spec:

**For each content file, collect:**

1. **File Name**: Name of the content file
   - Format: lowercase with hyphens, ending with `.md`
   - Examples: `typescript.md`, `coding-standards.md`, `performance-guidelines.md`

2. **File Purpose**: What does this file cover?
   - Brief description of the content
   - What area of the technology it addresses

3. **Main Sections**: What are the main sections of the file?
   - List the major topics covered
   - Brief description of each topic

4. **Key Guidelines**: What are the key guidelines?
   - List important rules or recommendations
   - Specify if they are mandatory, recommended, or optional

**Prompt Template for Each Content File**:
```
Please describe content file #{n}:

1. File Name: [e.g., typescript.md, coding-standards.md]
2. File Purpose: [What area does this file cover?]
3. Main Sections: [List major topics with brief descriptions]
4. Key Guidelines: [List important rules/recommendations]

(Enter 'done' when finished adding content files)
```

### 5. Generate Content Files

For each content file, generate a file following the template from `.asdm/toolsets/spec-builder/spec/spec-content-spec.md`:

The content file should include:

```markdown
# <Topic Name>

[Introduction explaining what this file covers]

## 1. <Section Name>

### 1.1 <Subsection>

<Guidelines and rules>

```code
// bad — Example of what not to do
// good — Example of what to do
```

## 2. <Section Name>

[Continue for all sections]

## Summary

- Guideline 1
- Guideline 2
- Guideline 3
```

**Important**:
- Follow the content file specification structure
- Include code examples with "bad" and "good" annotations
- Use `mandatory`, `recommended`, `optional` tags where appropriate
- Provide clear, actionable guidelines
- Include realistic code examples

**Content File Path**: `.asdm/specs/<spec-id>/<filename>`

### 6. Update README.md

Update the spec's README.md to include the content files in the Available Specifications section:

```markdown
## Available Specifications

### 1. <Content File 1 Name>
**File**: [filename.md](filename.md)

Covers:
- <Point 1 from content file>
- <Point 2 from content file>
- <Point 3 from content file>

### 2. <Content File 2 Name>
**File**: [filename.md](filename.md)

Covers:
- <Point 1 from content file>
- <Point 2 from content file>

[Continue for all content files]
```

### 7. Remove Placeholder Files

Remove the `.gitkeep` file from the directory if it exists:
- Delete `.asdm/specs/<spec-id>/.gitkeep`

This is no longer needed since the directory now contains actual files.

### 8. Generate Content Definition Summary

Create a summary for the developer:

```markdown
# Spec Content Definition Summary

## Spec
- **Spec ID**: <spec-id>
- **Spec Name**: <Spec Name>

## Defined Content Files

| File Name | Purpose | Main Sections |
|-----------|---------|---------------|
| <file-1>.md | <Purpose> | <Sections> |
| <file-2>.md | <Purpose> | <Sections> |
| ... | ... | ... |

## Generated Files
- Content files in `.asdm/specs/<spec-id>/`
- Updated README.md with content file descriptions

## Next Steps
1. Review the generated content files
2. Complete the content files with detailed guidelines
3. Use `/asdm-generate-manifest <spec-id>` to generate manifest.json
4. Use `/asdm-complete-spec <spec-id>` to finalize the spec

## Important Notes
- Content files contain the actual coding standards and guidelines
- Each content file should have clear, actionable guidelines
- Include code examples with good and bad patterns
- Use tags (mandatory, recommended, optional) for guidelines
```

Save this summary to a temporary location or display it to the developer.

## Execution Guidelines

### When to Use This Action

Use this action when:
- You have initialized a spec and need to define its content files
- You want to create coding standards and guidelines files
- You need to update the README.md with content file information

### Content File Guidelines

When defining content files:

1. **Be Descriptive**: Provide clear descriptions of what each file covers
2. **Consider Scope**: Each file should cover a specific area or topic
3. **Define Clear Sections**: Organize content into logical sections
4. **Think About Users**: Consider who will use these guidelines
5. **Follow ASDM Principles**: Align with ASDM conventions

### File Name Guidelines

When choosing file names:
- Use lowercase letters only
- Use hyphens to separate words
- Keep them short but descriptive
- End with `.md` extension

**Good Examples**:
- `typescript.md`
- `coding-standards.md`
- `performance-guidelines.md`
- `testing-best-practices.md`

**Bad Examples**:
- `TypeScript.md` (uppercase)
- `coding standards.md` (spaces)
- `my_file.md` (underscores)

### Content Guidelines

When writing content:
- Make each guideline clear and actionable
- Include code examples where appropriate
- Use tags (mandatory, recommended, optional) to indicate importance
- Consider edge cases and common pitfalls
- Provide rationale for guidelines

## Usage

To use this instruction, the AI model should:
1. Detect the response language
2. Identify the spec (prompt if not provided)
3. Validate the spec exists and has been initialized
4. Load the spec's README.md
5. Collect content file information from the developer for each file
6. Generate content files following the content spec template
7. Update the README.md with content file descriptions
8. Remove placeholder `.gitkeep` files
9. Present a content definition summary with next steps

## Output Summary

After completing the content definition, the following will be generated:
- Content files: `.asdm/specs/<spec-id>/<filename>.md` (one for each content area)
- Updated README.md with content file descriptions
- Removed placeholder `.gitkeep` files

All content files follow the structure defined in `.asdm/toolsets/spec-builder/spec/spec-content-spec.md` and provide detailed coding standards and guidelines.
