# Spec Builder Installation

**Toolset ID:** `spec-builder`

## Overview
This document provides instructions for installing and setting up the Spec Builder toolset. Spec Builder helps developers create and manage ASDM specs (coding standards, best practices, and guidelines) efficiently by providing guided development steps and automatic file generation.

## AI Guided Installation
To install this toolset using AI Guided Installation, copy and paste the following prompt into your AI Coding tool's chat window:

```shell
Follow instructions in .asdm/toolsets/spec-builder/INSTALL.md
```

## Installation Steps

### 1. Create `.asdm/specs` directory for specs

Create the directory for storing specs:

```bash
mkdir -p .asdm/specs
```

### 2. Detect the current `Agentic Engine` provider

Detect the current AI coding assistant provider (e.g., Claude Code, GitHub Copilot, Tencent CodeBuddy). Using the following guidelines to detect the provider:

- If `.claude` directory exists, use `Claude Code`
- If `.github` directory exists, use `GitHub Copilot`
- If `.codebuddy` directory exists, use `Tencent CodeBuddy`
- If no such folder is found in the current workspace, give user a prompt to select a provider manually

### 3. Create shortcuts commands for Spec Builder (toolset ID: `spec-builder`) in provider's entry point

Create shortcut commands in the appropriate location based on the detected provider. The installation process is consistent across all providers - we use `cat` to concatenate provider-specific frontmatter with the actual instruction content:

#### For Claude Code (`.claude/commands/`):
Claude Code uses Markdown files with Frontmatter metadata for slash commands. Create commands by concatenating Claude-specific frontmatter with instruction content:

```bash
mkdir -p .claude/commands/

# Initialize spec command
cat > .claude/commands/asdm-init-spec.md << 'EOF'
---
description: "Initialize a new spec project"
argument-hint: "[spec-id]"
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-init-spec.md >> .claude/commands/asdm-init-spec.md

# Define spec content command
cat > .claude/commands/asdm-define-spec-content.md << 'EOF'
---
description: "Define content files for spec"
argument-hint: "[spec-id]"
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-define-spec-content.md >> .claude/commands/asdm-define-spec-content.md

# Generate manifest command
cat > .claude/commands/asdm-generate-manifest.md << 'EOF'
---
description: "Generate manifest.json for spec"
argument-hint: "[spec-id]"
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-generate-manifest.md >> .claude/commands/asdm-generate-manifest.md

# Complete spec command
cat > .claude/commands/asdm-complete-spec.md << 'EOF'
---
description: "Complete and finalize the spec"
argument-hint: "[spec-id]"
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-complete-spec.md >> .claude/commands/asdm-complete-spec.md
```

#### For GitHub Copilot (`.github/prompts/`):
GitHub Copilot uses `.prompt.md` files with YAML frontmatter. Create prompt files by concatenating GitHub-specific frontmatter with instruction content:

```bash
mkdir -p .github/prompts/

# Initialize spec prompt
cat > .github/prompts/asdm-init-spec.prompt.md << 'EOF'
---
agent: 'agent'
description: 'Initialize a new spec project'
argument-hint: 'Enter spec ID'
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-init-spec.md >> .github/prompts/asdm-init-spec.prompt.md

# Define spec content prompt
cat > .github/prompts/asdm-define-spec-content.prompt.md << 'EOF'
---
agent: 'agent'
description: 'Define content files for spec'
argument-hint: 'Enter spec ID'
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-define-spec-content.md >> .github/prompts/asdm-define-spec-content.prompt.md

# Generate manifest prompt
cat > .github/prompts/asdm-generate-manifest.prompt.md << 'EOF'
---
agent: 'agent'
description: 'Generate manifest.json for spec'
argument-hint: 'Enter spec ID'
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-generate-manifest.md >> .github/prompts/asdm-generate-manifest.prompt.md

# Complete spec prompt
cat > .github/prompts/asdm-complete-spec.prompt.md << 'EOF'
---
agent: 'agent'
description: 'Complete and finalize the spec'
argument-hint: 'Enter spec ID'
---

EOF
cat .asdm/toolsets/spec-builder/actions/asdm-complete-spec.md >> .github/prompts/asdm-complete-spec.prompt.md
```

#### For Tencent CodeBuddy (`.codebuddy/commands/`):
Tencent CodeBuddy uses plain Markdown files. Copy the instruction files directly:

```bash
mkdir -p .codebuddy/commands/

# Copy all action files
cp .asdm/toolsets/spec-builder/actions/asdm-init-spec.md .codebuddy/commands/
cp .asdm/toolsets/spec-builder/actions/asdm-define-spec-content.md .codebuddy/commands/
cp .asdm/toolsets/spec-builder/actions/asdm-generate-manifest.md .codebuddy/commands/
cp .asdm/toolsets/spec-builder/actions/asdm-complete-spec.md .codebuddy/commands/
```

#### For Manual Usage (Other Providers):
For other AI coding assistants that don't have a standard command format, you can manually reference the action files:

1. Navigate to `.asdm/toolsets/spec-builder/actions/`
2. Open the desired action file (e.g., `asdm-init-spec.md`)
3. Copy the content and paste it into your AI coding tool's chat window
4. Follow the instructions in the action file

### 4. Verify Installation

Verify that the installation was successful:

```bash
# Check if directories exist
ls -la .asdm/specs
ls -la .asdm/toolsets/spec-builder

# Check if commands were created (for Claude Code)
ls -la .claude/commands/asdm-*.md

# Check if prompts were created (for GitHub Copilot)
ls -la .github/prompts/asdm-*.prompt.md

# Check if commands were created (for Tencent CodeBuddy)
ls -la .codebuddy/commands/asdm-*.md
```

## Initializing Spec Builder

Once Spec Builder is installed, you can use the following commands to create new specs:

### Using Claude Code
```shell
/asdm-init-spec [spec-id]
/asdm-define-spec-content [spec-id]
/asdm-generate-manifest [spec-id]
/asdm-complete-spec [spec-id]
```

### Using GitHub Copilot
```shell
/asdm-init-spec [spec-id]
/asdm-define-spec-content [spec-id]
/asdm-generate-manifest [spec-id]
/asdm-complete-spec [spec-id]
```

### Using Tencent CodeBuddy
```shell
/asdm-init-spec [spec-id]
/asdm-define-spec-content [spec-id]
/asdm-generate-manifest [spec-id]
/asdm-complete-spec [spec-id]
```

## Available Commands

| Command | Description |
|---------|-------------|
| `/asdm-init-spec` | Initialize a new spec project with directory structure and README.md template |
| `/asdm-define-spec-content` | Define and create content files for the spec |
| `/asdm-generate-manifest` | Generate manifest.json for the spec |
| `/asdm-complete-spec` | Complete and finalize the spec with validation |

## Toolset Structure

```
.asdm/toolsets/spec-builder/
├── INSTALL.md                         ## This file
├── README.md                          ## Toolset description
├── manifest.json                      ## Toolset manifest
├── actions/                           ## Action instructions
│   ├── asdm-init-spec.md             ## Initialize new spec
│   ├── asdm-define-spec-content.md   ## Define spec content files
│   ├── asdm-generate-manifest.md     ## Generate manifest.json
│   └── asdm-complete-spec.md         ## Complete, generate manifest.json
└── spec/                              ## Spec templates
    ├── spec-readme-spec.md           ## README template
    ├── spec-content-spec.md          ## Content file template
    └── spec-manifest-spec.md         ## Manifest template
```

## Spec Structure

When creating a new spec using Spec Builder, the following structure will be generated:

```
.asdm/specs/<spec-id>/
├── manifest.json              ## Spec metadata
├── README.md                  ## Entry point document
├── <content-file-1>.md       ## Coding standards/guidelines
├── <content-file-2>.md       ## Additional content
└── ...
```

## Verification

To verify the installation is complete:

1. Check that the Spec Builder toolset exists:
   ```bash
   ls -la .asdm/toolsets/spec-builder/
   ```

2. Check that the commands were created:
   - Claude Code: `ls -la .claude/commands/asdm-*.md`
   - GitHub Copilot: `ls -la .github/prompts/asdm-*.prompt.md`
   - Tencent CodeBuddy: `ls -la .codebuddy/commands/asdm-*.md`

3. Test a command:
   ```
   /asdm-init-spec test-spec
   ```

## Usage Examples

### Example 1: Create a new TypeScript spec
```
/asdm-init-spec typescript
/asdm-define-spec-content typescript
/asdm-generate-manifest typescript
/asdm-complete-spec typescript
```

### Example 2: Create an API response spec
```
/asdm-init-spec api-response
/asdm-define-spec-content api-response
/asdm-complete-spec api-response
```

## Usage

### For Claude Code
After installation, use the slash commands in Claude Code:
```
/asdm-init-spec [spec-id]
/asdm-define-spec-content [spec-id]
/asdm-generate-manifest [spec-id]
/asdm-complete-spec [spec-id]
```

### For GitHub Copilot
After installation, use the prompts in GitHub Copilot:
```
/asdm-init-spec [spec-id]
/asdm-define-spec-content [spec-id]
/asdm-generate-manifest [spec-id]
/asdm-complete-spec [spec-id]
```

### For Tencent CodeBuddy
After installation, use the commands in Tencent CodeBuddy:
```
/asdm-init-spec [spec-id]
/asdm-define-spec-content [spec-id]
/asdm-generate-manifest [spec-id]
/asdm-complete-spec [spec-id]
```

### For Other Providers
For other AI coding assistants, manually reference the action files:
1. Open the action file from `.asdm/toolsets/spec-builder/actions/`
2. Copy the content into your AI tool's chat window
3. Follow the instructions

## Notes

- All commands accept an optional `[spec-id]` argument
- If no spec-id is provided, you will be prompted to select one
- The toolset generates files in `.asdm/specs/` directory
- All generated files follow ASDM conventions

## Integration with Other Toolsets

Spec Builder works well with:
- **Toolset Builder** - For creating ASDM toolsets that use specs
- **Existing Specs** - Reference existing specs for patterns and conventions

## Getting Help

If you encounter issues:
1. Check the README.md in `.asdm/toolsets/spec-builder/`
2. Review the action files in `.asdm/toolsets/spec-builder/actions/`
3. Reference existing specs in `.asdm/specs/` for examples

## License

Copyright (c) 2026 LeansoftX.com & iSoftStone. All rights reserved.

Licensed under the PROPRIETARY SOFTWARE LICENSE. See [LICENSE](LICENSE) in the project root for license information.
