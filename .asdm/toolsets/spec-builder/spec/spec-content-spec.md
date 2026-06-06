# Spec Content File Template Specification

## Overview

This specification defines the template structure for creating spec content files. Content files (e.g., `typescript.md`, `css.md`) contain the actual coding standards, guidelines, and best practices for a specific technology or domain.

**Note**: Content files are the core of a spec. They provide detailed guidance that developers and AI models should follow when working with the technology.

---

## Content File Types

Common types of spec content files include:

1. **Coding Standards**: Define coding conventions, naming rules, and style guidelines
2. **Best Practices**: Provide recommended patterns and approaches
3. **Performance Guidelines**: Offer optimization techniques and recommendations
4. **Testing Guidelines**: Define testing strategies and patterns
5. **Architecture Guidelines**: Describe structural patterns and organization

---

## Content File Structure

A spec content file should include the following sections:

```markdown
# <Topic Name>

[Introduction and overview]

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

[Key takeaways and checklist]
```

---

## Section Guidelines

### 1. Title

Format: `# <Topic Name>`

The title should:
- Be descriptive of the technology or domain
- Use clear, recognizable terms
- Match the spec ID (e.g., "TypeScript" for typescript spec)

### 2. Introduction Section

Briefly introduce the topic:

```markdown
# <Topic Name>

[Introduction paragraph explaining what this spec covers and why it's important]
```

Keep it concise (1-2 paragraphs).

### 3. Main Sections

Organize content into logical sections:

```markdown
## 1. <Section Name>

### 1.1 <Subsection>

<Guidelines and rules>

```code
// bad — Example of what not to do
// good — Example of what to do
```
```

**Guidelines**:
- Use numbered sections (1, 2, 3...)
- Use subsections (1.1, 1.2, 2.1, 2.2...)
- Include code examples with "bad" and "good" annotations
- Provide clear, actionable guidelines
- Use `mandatory`, `recommended`, `optional` tags where appropriate

### 4. Code Examples

Include code examples to illustrate guidelines:

```markdown
```code
// bad — Direct mutation
const arr = [1, 2, 3];
arr.push(4);

// good — Immutable approach
const arr = [1, 2, 3];
const newArr = [...arr, 4];
```
```

**Guidelines**:
- Always show both "bad" and "good" examples
- Use comments to explain why something is bad or good
- Keep examples concise and focused
- Use realistic examples from actual use cases

### 5. Summary Section

Provide a summary or checklist:

```markdown
## Summary

- Guideline 1
- Guideline 2
- Guideline 3

## Checklist

- [ ] Check 1
- [ ] Check 2
- [ ] Check 3
```

---

## Writing Guidelines

### Clarity

- Be clear about what each guideline means
- Provide concrete examples
- Avoid ambiguous language
- Use specific terms, not vague ones

### Completeness

- Cover all important aspects of the technology
- Include both common and edge cases
- Provide guidance for different scenarios
- Include error handling where relevant

### Consistency

- Use consistent terminology throughout
- Follow the same formatting patterns
- Maintain similar level of detail across sections
- Use consistent code style in examples

### Practicality

- Focus on real-world use cases
- Provide actionable guidance
- Consider developer workflow
- Include common pitfalls to avoid

---

## Common Patterns

### Pattern 1: Rule with Example

```markdown
### 1.1 Use TypeScript Interfaces

Define data structures using interfaces:

```code
// bad — Using any type
function process(data: any) { ... }

// good — Using interface
interface UserData {
  id: number;
  name: string;
}
function process(data: UserData) { ... }
```
```

### Pattern 2: Rule with Tags

```markdown
### 2.1 Error Handling

- `mandatory` All API calls must include error handling
- `recommended` Use try-catch for async operations
- `optional` Add logging for debugging
```

### Pattern 3: Checklist

```markdown
## Performance Checklist

- [ ] Use React.memo for expensive components
- [ ] Memoize computed values with useMemo
- [ ] Memoize callbacks with useCallback
- [ ] Use virtualization for long lists
```

### Pattern 4: Table for Reference

```markdown
## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | Success | All successful responses |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing authentication |
| 500 | Server Error | Internal errors |
```

---

## Best Practices

### 1. Start with Why

Explain why each guideline is important:
- What problem does it solve?
- What happens if not followed?
- What are the benefits?

### 2. Provide Examples

Always include examples:
- Show both good and bad patterns
- Use realistic code snippets
- Explain the reasoning

### 3. Be Specific

Avoid vague guidelines:
- Use specific numbers when possible
- Define exact formats
- Provide concrete thresholds

### 4. Consider Edge Cases

Address common edge cases:
- What happens in error scenarios?
- How to handle exceptions?
- What are the limitations?

### 5. Keep It Updated

Regularly review and update:
- Add new patterns as they emerge
- Remove outdated practices
- Update examples to current versions

---

## Common Mistakes to Avoid

1. **Too theoretical**: Focus on practical, actionable guidance
2. **Missing examples**: Always include code examples
3. **Inconsistent style**: Use consistent formatting throughout
4. **Outdated content**: Keep guidelines current with latest versions
5. **Vague rules**: Be specific about what to do and why
6. **No rationale**: Explain why each guideline matters

---

## Example: TypeScript Content File Structure

```markdown
# TypeScript

This document defines coding standards and best practices for TypeScript development.

## 1. Type Safety

### 1.1 Use Explicit Types

Always specify types explicitly for function parameters and return values:

```code
// bad — Implicit any
function add(a, b) {
  return a + b;
}

// good — Explicit types
function add(a: number, b: number): number {
  return a + b;
}
```

### 1.2 Avoid Any Type

Never use `any` type unless absolutely necessary:

```code
// bad — Using any
let data: any;

// good — Using unknown for type safety
let data: unknown;
```

## 2. Naming Conventions

### 2.1 Use PascalCase for Types

```code
// bad — camelCase
type userProfile = { ... }

// good — PascalCase
type UserProfile = { ... }
```

## Summary

- Always use explicit types
- Avoid `any` type
- Follow naming conventions
- Use interfaces for object shapes
```

---

## Checklist for Writing Content Files

Before finalizing your content file, check:

- [ ] Title is descriptive
- [ ] Introduction explains the purpose
- [ ] Sections are logically organized
- [ ] Code examples show both good and bad patterns
- [ ] Guidelines are specific and actionable
- [ ] Tags (mandatory, recommended, optional) are used where appropriate
- [ ] Summary or checklist is included
- [ ] Language is clear and consistent
- [ ] No typos or formatting errors

---

## Related Documents

This specification is used by:
- **Spec Builder**: `/asdm-define-spec-content` action generates content files based on this spec
- **Developers**: Follow this spec when writing content files
- **AI Models**: Reference this spec for coding standards
