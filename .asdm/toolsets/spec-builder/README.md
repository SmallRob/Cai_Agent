# ASDM Toolset - Spec Builder

toolset-id: spec-builder
toolset-name: Spec Builder
version: 0.0.1
updated-date: 2026-05-29
toolset-description: A toolset for helping developers create and manage ASDM specs (coding standards, best practices, and guidelines).

## Overview

Spec Builder (toolset-id: spec-builder) is an ASDM toolset designed to help developers create and manage specification documents efficiently. Specs define coding standards, best practices, and guidelines for specific technologies or domains (e.g., TypeScript, React, API Response standards).

This toolset provides a structured approach to spec development, guiding developers through the entire process from initial concept to complete implementation. The toolset generates all necessary files including README.md, manifest.json, and content files based on developer's requirements.

User can install this toolset into a workspace and run `INSTALL.md` document using `AI Guided Installation` to initialize the toolset for the workspace. Just simply copy and paste the following prompt into your `AI Coding` tool's chat window and hit enter:

```shell
Follow instructions in .asdm/toolsets/spec-builder/INSTALL.md
```

## Features

Main features of Spec Builder:

### Common features

- Provide user friendly shortcuts `actions` using provider's entry point to ease the spec development process
- Provide standard `spec` for creating new spec files
- Interactive development guidance with step-by-step instructions
- Automatic file generation based on developer input
- Support for multiple spec scenarios (frontend, backend, backend-api)

### Initialize New Spec (init-spec)

Initialize a new spec project by collecting essential information:
- Spec ID (unique identifier, e.g., `typescript`, `api-response`)
- Spec Name (display name, e.g., "TypeScript Development Specs")
- Spec Description (overview of purpose)
- Spec Scenario (frontend, backend, backend-api)
- Initial directory structure

Output: Basic spec directory with README.md template and directory structure

### Define Spec Content (define-spec-content)

Define the content files for the spec:
- Collect content file descriptions (e.g., coding standards, performance guidelines)
- Define file names and purposes
- Specify content structure and format
- Generate content file templates

Output: Content files in the spec directory (e.g., `typescript.md`, `coding-standards.md`)

### Generate Manifest (generate-manifest)

Generate manifest.json for a spec:
- Extract metadata from README.md
- Generate and validate manifest.json
- Ensure all required fields are present

Output: manifest.json with complete spec metadata

### Complete Spec (complete-spec)

Review and finalize the spec:
- Validate all files exist
- Generate manifest.json
- Check completeness and consistency
- Generate summary
- Provide next steps

Output: Complete, ready-to-use spec with manifest.json and validation report

## Toolset Installation Process

`INSTALL.md` will setup the toolset with the following steps:

- Create `.asdm/specs` directory if it doesn't exist
- Detect the current `Agentic Engine` provider, e.g. Claude Code, GitHub Copilot, Tencent CodeBuddy etc.
- Create shortcuts commands for Spec Builder in provider's entry point, e.g. `.claude/commands`, `.github/prompts`, `.codebuddy/commands` etc.

## Toolset Workflow

Once Spec Builder is installed, user can use the following commands to create new specs:

- `/asdm-init-spec`: Initialize a new spec project
- `/asdm-define-spec-content`: Define content files for the spec
- `/asdm-generate-manifest`: Generate manifest.json for a spec
- `/asdm-complete-spec`: Generate manifest.json and finalize the spec

## Toolset Structure

The Spec Builder toolset has the following structure:

```
.asdm/
└── toolsets/
    └── spec-builder/                          ## Spec Builder toolset
        ├── INSTALL.md                         ## Installation instructions
        ├── README.md                          ## Current document
        ├── manifest.json                      ## Toolset manifest
        ├── actions/                           ## Instructions for Spec Builder
        │   ├── asdm-init-spec.md             ## Initialize new spec
        │   ├── asdm-define-spec-content.md   ## Define spec content files
        │   ├── asdm-generate-manifest.md     ## Generate manifest.json
        │   └── asdm-complete-spec.md         ## Complete, generate manifest.json
        └── spec/                              ## Spec documents for Spec Builder
            ├── spec-readme-spec.md           ## README template
            ├── spec-content-spec.md          ## Content file template
            └── spec-manifest-spec.md         ## Manifest template
```

## Toolset Workspace

When creating a new spec using Spec Builder, the following structure will be generated:

```
.asdm/specs/<spec-id>/
├── manifest.json              ## Spec metadata
├── README.md                  ## Entry point document
├── <content-file-1>.md       ## Coding standards/guidelines
├── <content-file-2>.md       ## Additional content
└── ...
```

## Development Workflow

### Step 1: Initialize Spec
Use `/asdm-init-spec` to create a new spec project with basic structure and README.md template.

### Step 2: Define Content Files
Use `/asdm-define-spec-content` to define and create the content files for the spec.

### Step 3: Generate Manifest
Use `/asdm-generate-manifest` to generate manifest.json for the spec.

### Step 4: Complete and Review
Use `/asdm-complete-spec` to finalize the spec, validate all files, and get a summary.

## Benefits

Using Spec Builder provides:

1. **Faster Development**: Quickly create new specs with guided steps
2. **Consistent Structure**: All specs follow the same structure and conventions
3. **Best Practices**: Built-in guidelines based on existing ASDM specs
4. **Reduced Errors**: Automated generation reduces manual errors
5. **Documentation Ready**: Includes complete README and manifest documentation

## Related Toolsets

- [Toolset Builder](../toolset-builder/README.md) - For creating ASDM toolsets

## Copyright & License

Copyright (c) 2026 LeansoftX.com & iSoftStone. All rights reserved.

Licensed under the PROPRIETARY SOFTWARE LICENSE. See [LICENSE](LICENSE) in the project root for license information.
