# Retro Command

Analyze the current development session and create a retrospective document.

**Your task:**

1. Review what was built in this session
2. Analyze the approach taken
3. Document key decisions and learnings
4. Note any patterns or anti-patterns observed
5. Suggest improvements for next session

**Output format:**

Create a markdown file in `retro/` named with timestamp: `retro_YYYYMMDD_HHMMSS.md`

Include sections:
- **Session Summary**: What was built
- **Technical Decisions**: Key choices made (e.g., DeepSeek, Pydantic, etc.)
- **What Went Well**: Successes
- **What Could Be Better**: Areas for improvement
- **Learnings**: Reusable patterns discovered
- **Next Steps**: Recommended actions for next session
- **Metrics**: Token usage, files created, time estimate

Wait for user input to add their perspective before finalizing.
