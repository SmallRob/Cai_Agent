# Instructions for asdm-complete-spec action

## Metadata

```json
{
  "guid": "f4a5b6c7-d8e9-0f1a-2b3c-d4e5f6a7b8c9",
  "name": "asdm-complete-spec",
  "displayName": "Complete Spec",
  "description": "Complete and finalize an ASDM spec project with validation",
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
This instruction guides the AI model to complete and finalize a spec project. It automatically generates the manifest.json file (combining the functionality of asdm-generate-manifest), then validates all files exist, checks completeness and consistency, generates a comprehensive summary, and provides recommendations for next steps.

## Language Setting

默认使用**中文（简体中文）**作为输出语言。所有生成的摘要、报告和文档均使用中文，并遵循中文写作规范。

如需切换语言，可在工作区根目录创建 `.asdm/config.json` 配置：
```json
{
  "language": "zh"
}
```
支持的语言：`zh`（中文，默认）、`en`（英文）。

## Context Injection

Before completing the spec, the AI model should read all spec files to validate completeness:

### Context Files to Read (Required)

1. **Spec README.md** (Required)
   - Path: `.asdm/specs/<spec-id>/README.md`
   - Purpose: Validate README completeness, extract metadata for manifest.json

2. **Content Files** (Required)
   - Path: `.asdm/specs/<spec-id>/*.md`
   - Purpose: Validate all content files exist and are complete

3. **Spec README Spec Template** (Reference)
   - Path: `.asdm/toolsets/spec-builder/spec/spec-readme-spec.md`
   - Purpose: Validate README structure

4. **Spec Content Spec Template** (Reference)
   - Path: `.asdm/toolsets/spec-builder/spec/spec-content-spec.md`
   - Purpose: Validate content file structure

5. **Spec Manifest Spec Template** (Reference)
   - Path: `.asdm/toolsets/spec-builder/spec/spec-manifest-spec.md`
   - Purpose: Validate manifest structure

## Steps to Complete Spec

### 1. Identify the Spec

The action receives a spec ID as input. If not provided, prompt the user to select a spec:
- List existing specs in `.asdm/specs/`
- Display spec IDs and names
- Ask user to select which spec to complete

### 2. Validate Spec Exists

Check if the spec exists:
- Path: `.asdm/specs/<spec-id>/README.md`
- If the README.md doesn't exist, inform the user that the spec hasn't been initialized yet
- Suggest running `/asdm-init-spec <spec-id>` first

### 3. Load All Spec Files

Read all spec files to validate completeness:

**Required Files:**
- README.md
- All content files in the spec directory (excluding .gitkeep)

**Check:**
- List all files in `.asdm/specs/<spec-id>/`
- Identify README.md and content files

### 4. Validate README.md

Validate the README.md against the spec-readme-spec.md:

**Required Sections:**
- [ ] Title (e.g., "# TypeScript Development Specs")
- [ ] Overview section (2-3 paragraphs)
- [ ] Available Specifications section with content file descriptions
- [ ] Related Specifications section (optional but recommended)
- [ ] Version section with current version and date

**Validation Checks:**
- Title is descriptive
- Overview explains what the spec covers
- All content files are listed in Available Specifications
- Each content file has a description of what it covers
- Version information is present
- No obvious placeholders remain

### 5. Validate Content Files

Validate each content file against the spec-content-spec.md:

**Required Sections:**
- [ ] Title (e.g., "# TypeScript")
- [ ] Introduction explaining what the file covers
- [ ] Main sections with guidelines
- [ ] Code examples with good/bad patterns
- [ ] Summary or checklist

**Validation Checks:**
- Title is descriptive
- Introduction explains the purpose
- Sections are logically organized
- Guidelines are clear and actionable
- Code examples show both good and bad patterns
- Tags (mandatory, recommended, optional) are used where appropriate
- Summary or checklist is included

### 6. Generate manifest.json

Generate the manifest.json file following the spec-manifest-spec.md:

**Manifest Structure**:
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

**Steps to Generate Manifest.json**:

1. **Generate Spec GUID**:
   - Generate a new UUID v4 for the spec's `guid` field
   - Example format: `e1f2a3b4-c5d6-7890-1234-56789abcdef0`

2. **Extract Metadata from README.md**:
   - Read `.asdm/specs/<spec-id>/README.md`
   - Extract the spec name, description, version

3. **Collect Missing Information**:
   - Scenario: Ask user if not clear from README
   - Creator: Default to "ASDM Platform" if not specified

4. **Generate manifest.json Content**:
   - Use the extracted metadata
   - Set dates to current timestamp
   - Format as valid JSON

5. **Write manifest.json File**:
   - File path: `.asdm/specs/<spec-id>/manifest.json`

### 7. Validate manifest.json

Validate the generated manifest.json:

**Validation Checks:**
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

### 8. Cross-Validation

Validate consistency across all files:

**Cross-Reference Checks:**
- [ ] README.md lists all content files
- [ ] All content files listed in README.md exist
- [ ] Content file descriptions match actual content
- [ ] Manifest metadata matches README.md
- [ ] Spec ID is consistent across all files
- [ ] Version is consistent across all files

### 9. Generate Completion Summary

Generate a comprehensive completion report:

```markdown
# Spec Completion Report

## Spec Information
- **Spec ID**: <spec-id>
- **Spec Name**: <Spec Name>
- **Version**: <version>
- **Scenario**: <scenario>
- **Description**: <spec-description>

## Validation Summary

### File Existence
- [x] README.md exists
- [x] manifest.json exists (auto-generated)
- [x] <n> content files exist

### README.md Validation
- [x] Title is descriptive
- [x] Overview section complete
- [x] Available Specifications section complete (<n> files)
- [x] Version section present

**Status**: ✅ PASSED / ⚠️ WARNINGS / ❌ FAILED

### Content Files Validation
- [x] All <n> content files exist
- [x] Titles are descriptive
- [x] Introductions are complete
- [x] Sections are well-organized
- [x] Code examples are provided
- [x] Summaries/checklists are included

**Status**: ✅ PASSED / ⚠️ WARNINGS / ❌ FAILED

### Manifest Validation
- [x] JSON is valid
- [x] All required fields present
- [x] registry_id matches spec ID
- [x] GUID is valid UUID v4
- [x] Version follows semantic versioning
- [x] Scenario is valid
- [x] All paths are correct

**Status**: ✅ PASSED / ⚠️ WARNINGS / ❌ FAILED

### Cross-Validation
- [x] README lists all content files
- [x] All listed files exist
- [x] Manifest metadata matches README
- [x] Spec ID is consistent
- [x] Version is consistent

**Status**: ✅ PASSED / ⚠️ WARNINGS / ❌ FAILED

## Overall Status

**✅ SPEC COMPLETE** / ⚠️ SPEC COMPLETE WITH WARNINGS / ❌ SPEC INCOMPLETE

## Spec Structure

```
.asdm/specs/<spec-id>/
├── manifest.json        ✅ (auto-generated)
├── README.md            ✅
├── <content-1>.md       ✅
├── <content-2>.md       ✅
└── <content-3>.md       ✅
```

## Next Steps

### Immediate Actions
1. **Review the completion report** - Check any warnings or failures
2. **Address any issues** - Fix any failed validations or warnings
3. **Test the spec** - Verify the spec is useful and accurate

### Testing Recommendations
1. **Review content** - Have other developers review the spec
2. **Test applicability** - Verify guidelines are practical
3. **Check completeness** - Ensure all important areas are covered

### Documentation Recommendations
1. **Complete content** - Ensure all content files are thorough
2. **Add examples** - Add more code examples if helpful
3. **Keep updated** - Plan for regular updates

### Deployment Recommendations
1. **Version control** - Commit the spec to version control
2. **Share with team** - Share the spec with your team
3. **Plan iterations** - Plan for future iterations and improvements

## Known Issues or Warnings
[List any warnings, issues, or areas for improvement identified during validation]

If no issues: *No known issues or warnings.*

## Recommendations

Based on the validation, here are recommendations:

### Strengths
- <Strength 1>
- <Strength 2>

### Areas for Improvement
- <Improvement 1>
- <Improvement 2>

### Future Considerations
- <Consideration 1>
- <Consideration 2>

## Conclusion

The <Spec Name> spec (ID: <spec-id>) has been successfully created and validated. All required files are present and complete. The spec is ready for use.

**Overall Assessment**: ✅ READY FOR USE

---

*Generated by Spec Builder on <current date>*
```

### 10. Save Completion Report

Save the completion report to:
- Path: `.asdm/specs/<spec-id>/COMPLETION_REPORT.md`
- This report can be referenced later for validation results

## Execution Guidelines

### When to Use This Action

Use this action when:
- You have completed all spec development steps
- You want to validate the spec is complete
- You need a comprehensive summary of the spec
- You're ready to publish and share the spec

### Completion Guidelines

When completing a spec:

1. **Thorough Validation**: Check all files carefully
2. **Cross-Reference**: Ensure consistency across all files
3. **Follow Conventions**: Align with existing specs
4. **Be Honest**: Report all issues and warnings
5. **Provide Recommendations**: Give actionable recommendations

### Validation Criteria

A spec is considered complete when:
- All required files exist (README.md, manifest.json, content files)
- All required sections are present in each file
- Content is consistent across all files
- manifest.json is valid JSON with correct field values
- No critical failures exist

Warnings may be issued for:
- Minor inconsistencies
- Missing optional but recommended content
- Areas that could be improved

Failures indicate:
- Missing required files or sections
- Critical inconsistencies
- Content that prevents the spec from functioning

## Usage

To use this instruction, the AI model should:
1. Detect the response language
2. Identify the spec (prompt if not provided)
3. Validate the spec exists and has been developed
4. Load all spec files (README.md, content files)
5. Validate README.md against spec-readme-spec.md
6. Validate each content file against spec-content-spec.md
7. Generate manifest.json with spec metadata
8. Validate the generated manifest.json
9. Perform cross-validation across all files
10. Generate a comprehensive completion report
11. Save the completion report to the spec directory
12. Present next steps and recommendations

## Output Summary

After completing the spec validation, the following will be generated:
- **manifest.json**: `.asdm/specs/<spec-id>/manifest.json` (automatically generated)
- Completion report: `.asdm/specs/<spec-id>/COMPLETION_REPORT.md`
- Validation results for each file and section
- Cross-validation results
- Overall completion status
- Next steps and recommendations

The completion report provides a comprehensive assessment of the spec's readiness for use.
