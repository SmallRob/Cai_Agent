# Instructions for asdm-generate-manifest action

## Metadata

```json
{
  "guid": "e3f4a5b6-c7d8-9e0f-1a2b-c3d4e5f6a7b8",
  "name": "asdm-generate-manifest",
  "displayName": "Generate Spec Manifest",
  "description": "Generate manifest.json for an existing ASDM spec",
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
This instruction guides the AI model to generate manifest.json for an existing spec. It extracts metadata from the README.md, generates a UUID, and creates a valid manifest.json file.

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

Before generating manifest.json, the AI model should read the spec's README.md:

### Context Files to Read (Required)

1. **Spec README.md** (Required)
   - Path: `.asdm/specs/<spec-id>/README.md`
   - Purpose: Extract metadata for manifest.json

2. **Spec Manifest Spec Template** (Reference)
   - Path: `.asdm/toolsets/spec-builder/spec/spec-manifest-spec.md`
   - Purpose: Follow the manifest structure

## Steps to Generate Manifest

### 1. Identify the Spec

The action receives a spec ID as input. If not provided, prompt the user to select a spec:
- List existing specs in `.asdm/specs/`
- Display spec IDs and names
- Ask user to select which spec to generate manifest for

### 2. Validate Spec Exists

Check if the spec exists:
- Path: `.asdm/specs/<spec-id>/README.md`
- If the README.md doesn't exist, inform the user that the spec hasn't been initialized yet
- Suggest running `/asdm-init-spec <spec-id>` first

### 3. Extract Metadata from README.md

Read the spec's README.md and extract:
- Spec name (from title)
- Spec description (from overview)
- Spec scenario (from context or user input)
- Spec version (from version section)
- Content files list (from Available Specifications section)

### 4. Collect Missing Information

If any required information is missing, prompt the user:

**Required Information**:
- **Spec Scenario**: If not clear from README, ask:
  - `frontend` - For UI frameworks, CSS, client-side technologies
  - `backend` - For server-side frameworks, databases, services
  - `backend-api` - For API standards, response formats, error codes

- **Creator**: If not specified, default to "ASDM Platform"

**Prompt Template**:
```
I've extracted the following information from the README:
- Spec Name: <extracted-name>
- Description: <extracted-description>
- Version: <extracted-version>

Please provide the following missing information:
1. Spec Scenario (frontend/backend/backend-api): [e.g., frontend]
2. Creator (optional, default: ASDM Platform): [e.g., ASDM Platform]
```

### 5. Generate UUID

Generate a new UUID v4 for the manifest's `guid` field:
- Format: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`
- Example: `e1f2a3b4-c5d6-7890-1234-56789abcdef0`

### 6. Generate manifest.json

Create the manifest.json file with the following structure:

```json
{
  "registry_id": "<spec-id>",
  "guid": "<generated-uuid>",
  "name": "<Spec Name>",
  "description": "<Spec Description>",
  "scenario": "<frontend|backend|backend-api>",
  "version": "<version>",
  "downloadUrl": "<spec-id>.zip",
  "path": "<spec-id>",
  "entryPoint": "<spec-id>/README.md",
  "dateCreated": "<current-date-iso8601>",
  "dateUpdated": "<current-date-iso8601>",
  "createdBy": "<creator>",
  "updatedBy": "<creator>"
}
```

**Field Mapping**:
| Field | Source |
|-------|--------|
| `registry_id` | Spec ID |
| `guid` | Generated UUID v4 |
| `name` | README.md title |
| `description` | README.md overview |
| `scenario` | User input or README context |
| `version` | README.md version section |
| `downloadUrl` | `<spec-id>.zip` |
| `path` | `<spec-id>` |
| `entryPoint` | `<spec-id>/README.md` |
| `dateCreated` | Current timestamp |
| `dateUpdated` | Current timestamp |
| `createdBy` | User input or default |
| `updatedBy` | User input or default |

### 7. Validate manifest.json

Validate the generated manifest.json:

**Validation Checks**:
- JSON is valid and parseable
- All required fields are present
- `registry_id` matches spec ID
- `guid` is valid UUID v4 format
- `version` follows semantic versioning
- `scenario` is one of: `frontend`, `backend`, `backend-api`
- `downloadUrl` matches `<spec-id>.zip` pattern
- `path` matches `<spec-id>` pattern
- `entryPoint` matches `<spec-id>/README.md` pattern
- `dateCreated` and `dateUpdated` are valid ISO-8601 dates

### 8. Save manifest.json

Save the manifest.json to:
- Path: `.asdm/specs/<spec-id>/manifest.json`

### 9. Generate Manifest Summary

Create a summary for the developer:

```markdown
# Manifest Generation Summary

## Spec Information
- **Spec ID**: <spec-id>
- **Spec Name**: <Spec Name>
- **Version**: <version>
- **Scenario**: <scenario>

## Generated Manifest
- **Path**: `.asdm/specs/<spec-id>/manifest.json`
- **GUID**: <generated-uuid>

## Manifest Content
```json
<manifest-content>
```

## Validation Results
- [x] JSON is valid
- [x] All required fields present
- [x] registry_id matches spec ID
- [x] GUID is valid UUID v4
- [x] Version follows semantic versioning
- [x] Scenario is valid
- [x] All paths are correct

## Next Steps
1. Review the generated manifest.json
2. Use `/asdm-complete-spec <spec-id>` to finalize the spec and validate all files
```

Save this summary to a temporary location or display it to the developer.

## Execution Guidelines

### When to Use This Action

Use this action when:
- You have completed the spec content and need to generate manifest.json
- You want to quickly generate manifest.json for a spec
- You need to update the manifest with current spec information

### Manifest Guidelines

When generating manifest.json:

1. **Extract Accurately**: Get information from README.md accurately
2. **Validate UUID**: Ensure GUID is valid UUID v4 format
3. **Use Correct Paths**: Follow the path patterns exactly
4. **Set Correct Dates**: Use current timestamp in ISO-8601 format
5. **Validate Everything**: Check all fields before saving

### Scenario Guidelines

When determining scenario:
- `frontend` - React, Vue, Angular, CSS, HTML, JavaScript frameworks
- `backend` - Java, Spring Boot, Node.js, Python, database technologies
- `backend-api` - API response formats, error codes, REST standards

## Usage

To use this instruction, the AI model should:
1. Detect the response language
2. Identify the spec (prompt if not provided)
3. Validate the spec exists
4. Read the spec's README.md
5. Extract metadata from README.md
6. Collect missing information (scenario, creator)
7. Generate UUID v4
8. Generate manifest.json
9. Validate the manifest
10. Save manifest.json
11. Present a summary with validation results

## Output Summary

After completing the manifest generation, the following will be generated:
- Manifest file: `.asdm/specs/<spec-id>/manifest.json`
- Validation results for the manifest

The manifest.json contains all metadata about the spec and is used by the ASDM system to register and manage the spec.
