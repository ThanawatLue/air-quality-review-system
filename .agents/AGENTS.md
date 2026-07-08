# Custom Agent Rules for AirQualityReview Project

## Default Workflow Override: Strict Discipline Always On
1. **No Trivial Exemptions (Disable Fast Path):** Do not use the "Active Fast Path". Treat EVERY user request—whether it is writing a script, modifying a document, or making a code change—as a "non-trivial task".
2. **Always Plan & Verify:** For every task, you MUST automatically apply the strict Checklist Execution Discipline and Evidence-Based Completion standard.
3. **Implicit Fable Discipline:** Act as if the user appended `@fable-discipline` to every single prompt. Never skip creating an implementation plan, maintaining a checklist, and explicitly verifying the output before reporting completion.

## Markdown Parsing and Manipulation
When reading, searching, or performing regex/string replacements on Markdown files (especially those generated from document converters like Word-to-Markdown tools), ALWAYS account for Markdown escape characters. Converters often escape characters like `_`, `-`, `(`, `)`, `[`, and `]` with backslashes (e.g., `\_`, `\-`, `\(`). 
- Before running string replacements, view the raw text of the file to inspect how special characters are escaped.
- When writing regex patterns or exact string matches, explicitly handle potential backslashes to ensure successful matches.
