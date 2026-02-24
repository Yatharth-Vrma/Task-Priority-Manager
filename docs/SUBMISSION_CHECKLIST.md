# Submission Checklist

## Required Components

- [x] **Working Repository**
  - Complete source code
  - All dependencies listed
  - Setup instructions clear

- [x] **README**
  - Project overview
  - Architecture explanation
  - Key technical decisions
  - Setup instructions
  - API documentation
  - Known limitations
  - Extension approach

- [x] **Walkthrough Video (10-15 min)**
  - Architecture overview
  - Code structure walkthrough
  - Technical decisions explained
  - AI usage demonstrated
  - Risks identified
  - Extension approach described

- [x] **AI Guidance Files**
  - `docs/claude-guidance.md` - Constraints and rules for AI
  - Clear coding standards
  - Error handling requirements
  - Architecture patterns

## Evaluation Criteria Coverage

### Structure ✓
- Clear layer boundaries (routes → services → models)
- Logical organization
- Single responsibility per module

### Simplicity ✓
- Readable code over clever code
- Predictable behavior
- Minimal abstractions

### Correctness ✓
- Invalid states impossible (state machine)
- Pydantic validation prevents bad data
- Database constraints enforced
- Type hints throughout

### Interface Safety ✓
- Pydantic schemas validate all inputs
- Type hints on all functions
- Explicit error messages
- REST conventions followed

### Change Resilience ✓
- New fields don't break existing code
- Services isolated from HTTP concerns
- Business logic separated from validation
- Easy to add new endpoints

### Verification ✓
- Unit tests for business logic
- Integration tests for API
- All tests passing
- Error cases covered

### Observability ✓
- Structured error responses
- HTTP status codes meaningful
- Clear error messages
- Can enable query logging

### AI Guidance ✓
- Documented constraints in `claude-guidance.md`
- Coding standards defined
- Common mistakes prevented
- Review checklist provided

### AI Usage ✓
- All code reviewed
- Tests verify behavior
- Type safety maintained
- Documentation accurate

### Communication ✓
- Trade-offs explained in README
- Weaknesses acknowledged
- Extension approach described
- Clear documentation

## Final Checks

- [x] All tests pass: `pytest tests/ -v` → 56 passed, 0 warnings
- [x] Backend runs: `python backend/run.py`
- [x] Frontend builds: `cd frontend && npm install && npm start` → 0 errors, 0 warnings
- [x] README is complete — architecture, decisions, AI usage, risks, extensions, video embed
- [ ] Walkthrough video recorded (10-15 min) → place in `video/walkthrough.mp4`
- [x] AI guidance files included — `docs/claude-guidance.md`
- [x] Video folder created — `video/` with instructions
- [ ] Email subject correct: "Associate Software Engineer - Yatharth - Assessment"
- [ ] Email sent to: assessments@bettrsw.com

## What NOT to Include

- [x] No confidential code
- [x] No employer-owned code
- [x] No proprietary prompts
- [x] All code created specifically for this assessment

## Submission Content

1. **Repository Link** (GitHub recommended)
2. **Video Link** (Loom, YouTube, Google Drive, etc.)
3. **Brief Email**:
   - Introduction
   - Repository link
   - Video link
   - Time invested (~22 hours)
   - Any notes or context

## Email Template

```
Subject: Associate Software Engineer - Yatharth - Assessment

Dear Better Software Hiring Team,

I'm pleased to submit my Associate Software Engineer assessment.

Project: Task Priority Manager
Repository: [GitHub URL]
Walkthrough Video: [Video URL]

Key highlights:
- Clean layered architecture (routes → services → models)
- Type-safe end-to-end (Pydantic + TypeScript)
- Comprehensive test coverage
- Invalid states prevented by design
- AI-assisted development with human verification

Time invested: ~22 hours over 48-hour window

The system demonstrates correctness over features, with clear extension points and well-documented trade-offs.

Looking forward to discussing the implementation.

Best regards,
Yatharth Verma
```

## Repository Checklist

- [x] README.md in root
- [x] Backend code complete
- [x] Frontend code complete
- [x] Tests included
- [x] Documentation in docs/
- [x] .gitignore configured
- [x] requirements.txt
- [x] package.json
- [x] Clear commit history (if using Git)

## Video Recording Tips

1. **Test recording setup first**
   - Check audio quality
   - Check screen sharing clarity
   - Test code visibility

2. **Structure**
   - Start with overview
   - Walk through code systematically
   - Show tests running
   - Demo the application
   - Discuss trade-offs
   - Explain extension approach

3. **Timing**
   - Introduction: 1 min
   - Architecture: 4 min
   - Technical decisions: 3 min
   - AI usage: 2 min
   - Testing: 2 min
   - Risks/Extensions: 2 min
   - Demo: 1 min

4. **Don't forget to**
   - Explain WHY, not just WHAT
   - Show trade-offs
   - Acknowledge limitations
   - Demonstrate change resilience
