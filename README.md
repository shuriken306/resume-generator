# Resume Generator

A developer resume as PDF -- generated from a JSON file with a Python script. Dark terminal-style header, two-column layout, color-coded skill bars.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (dependencies are resolved automatically)

## Quick Start

```bash
# Generate default example (Max Mustermann)
uv run --with reportlab python3 resume.py

# Use your own data
uv run --with reportlab python3 resume.py my_data.json

# Fixed output name (overwrites)
uv run --with reportlab python3 resume.py my_data.json --output application.pdf
```

Without `--output`, files are versioned automatically: `resume_v1.pdf`, `resume_v2.pdf`, ...

## Project Structure

```
resume.py                  # PDF generator (reportlab)
resume_data_default.json   # Example data (Max Mustermann)
resume_data.json           # Your own data (not in repo)
generate.sh                # Shell wrapper
.claude/skills/resume/     # Claude Code skill for interactive creation
```

## JSON Structure

The JSON file has the following sections:

```jsonc
{
  "personal": { ... },        // Name, contact, title, stack line
  "terminal_text": "...",     // Text in the terminal bar in the header
  "jobs": [                   // Work experience (most recent first)
    {
      "title": "...",
      "company": "Company, City",
      "period": "since ...",
      "tasks": ["...", "..."]
    }
  ],
  "education": [ ... ],       // Education with optional tags
  "skills": [                 // Tech stack with progress bars
    {
      "name": "Python",
      "level": 0.9,           // 0.0 - 1.0
      "color": "sky",         // sky | orange | green | indigo
      "hint": "optional"      // Subtitle (can be empty)
    }
  ],
  "further_education": [ ... ], // Conferences, certifications
  "languages": [ ... ],         // Languages with proficiency level
  "profile": "..."              // Free-text profile (3-4 sentences)
}
```

See `resume_data_default.json` for a complete example.

### Skill Colors

| Color    | Category           | Examples                     |
|----------|--------------------|------------------------------|
| `sky`    | Main stack         | C#/.NET, Python, Blazor      |
| `orange` | Frontend           | Angular, React, TypeScript   |
| `green`  | Data / DevOps      | PostgreSQL, Docker, Git      |
| `indigo` | API / Architecture | REST APIs, Clean Architecture|

## Creating a Resume with AI

### With Claude Code (recommended)

The project includes an interactive skill that guides you step by step:

```
/resume
```

Or directly with a job description:

```
/resume We are looking for a full-stack developer with Python experience...
```

The skill will:
1. Ask if there is a job description and analyze the requirements
2. Collect your data block by block (contact, work experience, education, skills, ...)
3. Follow up on gaps or vague information
4. Suggest phrasings and a profile text
5. Generate the JSON and create the PDF
6. Ask if adjustments are needed

### With another AI agent

You can also create the JSON with any other LLM. Give the agent this prompt:

```
I want to create a resume. The target structure is a JSON file
with this layout: [paste contents of resume_data_default.json]

Ask me step by step for my data:
1. Personal details and contact information
2. Work experience (each position individually, with specific tasks and technologies)
3. Education (all stations, including those without a degree)
4. Technical skills (with self-assessment 1-10)
5. Further education and conferences
6. Languages
7. Profile text (2-3 sentences)

If a job description is provided, adapt the order and phrasing
to match the requirements.

Follow up if information is vague or there are gaps in the resume.
Suggest concrete phrasings but do not invent data.
```

Save the generated JSON as `resume_data.json` and generate the PDF:

```bash
uv run --with reportlab python3 resume.py resume_data.json
```

## Customization

### Changing the Layout

The script (`resume.py`) is organized into clearly named functions:

- `draw_header()` -- Dark header with terminal bar and contact info
- `draw_left_column()` -- Work experience + education
- `draw_right_column()` -- Tech stack, further education, languages, profile
- `draw_footer()` -- Footer with location and date

Colors, spacing, and font sizes are defined as constants at the top of the file.
