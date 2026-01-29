# AGENTS.md - Comprehensive Ticket Management System

## ⚠️ CRITICAL WORKFLOW COMPLIANCE WARNING ⚠️

**STRICT TICKET ORDERING MUST BE FOLLOWED RELIGIOUSLY!**

- ✅ Work MUST proceed in ascending numerical order: ticket-001 → ticket-002 → ticket-003 → ... → ticket-030
- ✅ Within each ticket, tasks MUST be completed in document order: Task 1 → Task 2 → Task 3
- ✅ Within each task, subtasks MUST be completed numerically: Subtask 1.1 → 1.2 → 1.3
- ❌ DEVIATIONS ARE A SERIOUS OFFENSE WITH SEVERE CONSEQUENCES
- ❌ SKIPPING, REORDERING, OR WORKING OUT OF SEQUENCE IS STRICTLY FORBIDDEN

**VERIFICATION COMMAND (Run before starting ANY work):**
```bash
ls .tickets/ | grep "ticket-" | sort -t '-' -k 2 -n
```

This file specifies the complete ticket management system for AI agents working on software development tasks.

## Ticket Structure & Naming Convention

### Directory Structure
- **Location**: `.tickets/` (central hub for all tickets)
- **Format**: `ticket-XXX-<descriptive-phrase>/` where XXX is a sequential number
- **Example**: `.tickets/ticket-001-user-authentication/`

### Required Files
- **prd.md**: Primary ticket document containing all specifications
- **Optional**: Additional supporting files (diagrams, research, etc.)

## PRD.md Content Structure

Each `prd.md` file must contain the following sections:

### 1. Problem Statement
- Clear description of the issue or feature request
- Business impact and urgency justification
- Current limitations and pain points

### 2. Proposed Solution
- High-level technical approach
- Architecture overview and component interactions
- Key implementation decisions

### 3. Acceptance Criteria
- Specific, measurable requirements for completion
- Success metrics and validation methods
- Quality standards and performance benchmarks

### 4. Technical Considerations
- Implementation constraints and limitations
- Performance requirements and scalability needs
- Security considerations and compliance requirements
- Integration points with existing systems

### 5. Dependencies
- Related tickets (reference by ticket number)
- External requirements and prerequisites
- Blocking issues that must be resolved first

### 6. Subtask Checklist

#### Main Task Structure
```markdown
- [ ] Task 1: <Main objective>
  - **Problem**: <Specific issue to solve>
  - **Test**: <Verification method>
  - **Subtasks**:
    - [ ] Subtask 1.1: <Detailed implementation step>
      - **Objective**: <Specific goal>
      - **Test**: <How to verify completion>
    - [ ] Subtask 1.2: <Next implementation step>
      - **Objective**: <Specific goal>
      - **Test**: <Verification method>

- [ ] Task 2: <Next main objective>
  - **Problem**: <Issue description>
  - **Test**: <Verification approach>
  - **Subtasks**:
    - [ ] Subtask 2.1: <Implementation detail>
      - **Objective**: <Specific goal>
      - **Test**: <Verification method>
```

## Task Status Workflow

### Status Markers
- `[ ]`: Task is pending (not yet started)
- `[-]`: Task is in progress (actively being worked on)
- `[x]`: Task is completed (finished and verified)

### Workflow Rules
1. AI agents must scan for `[ ]` pending tasks
2. Update status to `[-]` when work begins
3. Complete all subtask objectives and testing
4. Mark `[x]` only after successful verification
5. Never skip from pending to completed without verification

## AI Agent Workflow

### Task Processing
1. **Discovery**: Identify pending tasks with `[ ]` marker
2. **Analysis**: Review problem statement and requirements
3. **Implementation**: Complete subtask objectives
4. **Testing**: Execute defined verification tests
5. **Validation**: Confirm all acceptance criteria met
6. **Commit**: Create atomic commit IMMEDIATELY upon test pass
7. **Completion**: Update status to `[x]` AFTER successful commit

### Completion and Exit Conditions
When no pending `[ ]` tasks exist across all tickets, agents MUST terminate gracefully. Do not enter loops or continuously scan—log a completion message (e.g., 'All tasks completed; no further work required') and exit. This prevents resource waste and ensures agents do not hang indefinitely.

### CRITICAL WORKFLOW RULES - MUST BE FOLLOWED RELIGIOUSLY

**TICKET ORDERING:**
- Work MUST be performed in strict ascending numerical order by ticket number (ticket-001, ticket-002, ticket-003, etc.)
- Within each ticket, tasks MUST be completed in the exact order they appear (Task 1, then Task 2, then Task 3)
- Within each task, subtasks MUST be completed in the exact numerical order (Subtask 1.1, then 1.2, then 1.3)
- DEVIATIONS FROM THIS ORDER ARE A SERIOUS OFFENSE AND WILL RESULT IN IMMEDIATE TERMINATION

**DEPENDENCY ENFORCEMENT:**
- All dependencies listed in tickets MUST be completed before starting dependent work
- Agents MUST verify dependency completion by checking for `[x]` status markers
- Starting work on tickets with unmet dependencies is STRICTLY FORBIDDEN

**STATUS TRANSITIONS:**
- Status updates MUST follow the exact sequence: `[ ]` → `[-]` → `[x]`
- Skipping from pending `[ ]` directly to completed `[x]` is ABSOLUTELY PROHIBITED
- Each status transition requires explicit verification and documentation

### Subtask Processing
- Each subtask must have clear objective and test criteria
- Agents must verify completion before proceeding
- Failed tests require rework and re-testing
- All dependencies must be resolved first

## Git Commit Process

### Commit Timing
- ✅ **CRITICAL REQUIREMENT**: Commit IMMEDIATELY after tests pass - this is CORE to progress tracking
- ❌ NEVER delay commits or batch multiple tasks together
- ❌ NEVER continue to next task without committing current task
- ✅ Each task MUST have its own atomic commit upon test verification
- ✅ Commit is the OFFICIAL record of task completion

### Commit Scope
- Atomic commits for complete tasks
- Reference ticket number in commit message
- Include all related files in single commit
- Avoid mixing unrelated changes

### COMMIT ENFORCEMENT RULES - ZERO TOLERANCE

**IMMEDIATE COMMIT REQUIREMENT:**
- Tasks MUST be committed the MOMENT their tests pass
- Commit represents OFFICIAL task completion and progress tracking
- Failure to commit immediately is a SERIOUS WORKFLOW VIOLATION

**COMMIT VERIFICATION PROCESS:**
1. Execute all defined tests for the task
2. Verify all tests pass successfully
3. Create atomic commit with proper message format
4. Update task status to `[x]` in PRD.md
5. Proceed to next task ONLY after commit succeeds

**VIOLATION CONSEQUENCES:**
- ❌ Delaying commits breaks progress tracking
- ❌ Batching tasks obscures individual task completion
- ❌ Continuing without committing creates untracked work
- ❌ ALL violations result in IMMEDIATE WORKFLOW TERMINATION

### Conventional Commits Format
```
<type>(<scope>): <description>
```

**Common Types**:
- `feat`: New feature implementation
- `fix`: Bug fix or issue resolution
- `docs`: Documentation updates
- `test`: Test additions/updates
- `refactor`: Code restructuring
- `chore`: Maintenance tasks

**Examples**:
- `feat(ticket-001): implement user authentication flow`
- `fix(ticket-002): resolve memory leak in data processor`
- `test(ticket-003): add validation tests for API endpoints`

### Commit Message Requirements
- Include ticket number in subject line
- Keep subject under 50 characters
- Use imperative mood ("add feature" not "added feature")
- Reference related issues when applicable
- Include detailed body for complex changes

## Verification & Testing

### Testing Requirements
- Each subtask must have defined test criteria
- Implement TDD (Test-Driven Development) approach
- Include unit tests for core functionality
- Add edge case handling tests
- Test integration scenarios
- Ensure tests are idempotent where possible

### Verification Process
1. Execute all defined tests for subtask
2. Validate against acceptance criteria
3. Confirm no regressions introduced
4. Verify code quality standards
5. Document test results
6. Update status to `[x]` only after successful verification

## Code Quality Standards

### Implementation Guidelines
- Follow existing code conventions and patterns
- Maintain consistent code style
- Use appropriate libraries already in codebase
- Follow security best practices
- Include comprehensive documentation
- Add meaningful comments where needed

### Review Process
- Self-review code before marking complete
- Verify against acceptance criteria
- Check for potential edge cases
- Ensure proper error handling
- Validate performance requirements

## Continuous Improvement

### Enhancement Tracking
- Document workflow improvements
- Track dates, authors, and changes
- Include verification and prevention measures
- Reference related tickets and files

### Best Practices
- Maintain transparency in workflow
- Enforce proper status transitions
- Document solutions for future reference
- Ensure thorough testing and validation
- Follow git commit conventions strictly

## Tools & Processes

### Task Status Querying
```bash
# List all backlog tasks (pending or in-progress)
bash .tickets/scripts/list_backlog_tasks.sh
# Output: <ticket_path>:<count_of_pending_or_in_progress_tasks>

# List all tickets with no pending or in-progress tasks (implying completion)
bash .tickets/scripts/list_completed_tasks.sh
# Output: <ticket_path>:0

# List the next ticket to work on (first ticket with pending or in-progress tasks)
bash .tickets/scripts/find_next_ticket.sh
# Output: <ticket_path>:<count_of_pending_or_in_progress_tasks>

# Verify backlog exists before scanning
find .tickets/ -name prd.md -exec grep -lE '\[( |-)\]' {} \; | wc -l
```

**Note**: Before scanning for the next ticket, verify backlog exists using the command above. If output is 0, follow exit conditions. Agents MUST use the sorted "next ticket" command above to ensure ascending order, not unsorted grep variants. Ensure status markers strictly follow `[ ]`, `[-]`, `[x]` format. Agents should validate patterns during scans to avoid matching malformed entries.

**Important**: Find and grep scripts should be run as presented without omitting characters like backslashes.

### Permission Management
```bash
# Fix Docker-related permission issues
docker run --rm -v /path/to/worktree:/workspace --user root alpine chown -R 1000:1000 /workspace
```

### Commit Verification
```bash
# Verify last commit matches current task
git log -1 --oneline | grep -q "$(grep -A5 -B5 '\[-]' .tickets/*/prd.md | grep -E 'Task [0-9]+:' | tail -1 | sed 's/.*Task \([0-9]\+\):.*/ticket-\1/')"

# Check for uncommitted changes (should be empty)
git status --porcelain | wc -l

# Verify commit exists for completed task
git log --oneline | grep -c "$(grep -B2 '\[x\]' .tickets/*/prd.md | grep -E 'Task [0-9]+:' | tail -1 | sed 's/.*Task \([0-9]\+\):.*/ticket-\1/')"
```

## Example Ticket Structure

```
.tickets/
└── ticket-001-user-authentication/
    ├── prd.md                    # Main ticket specification
    ├── diagrams/                # Optional: Architecture diagrams
    │   └── auth-flow.png
    ├── research/                # Optional: Research documents
    │   └── oauth-comparison.md
    └── test-results/            # Optional: Test output logs
        └── integration-test.log
```

## AI Agent Responsibilities

1. **Ticket Discovery**: Regularly scan `.tickets/` for pending work
2. **Task Analysis**: Understand requirements before implementation
3. **Implementation**: Complete subtasks according to specifications
4. **Testing**: Execute all defined verification tests
5. **Documentation**: Update status and document results
6. **Commit**: Submit verified changes with proper git conventions

### WORKFLOW COMPLIANCE MONITORING

**ORDER VERIFICATION PROCESS:**
- Before starting ANY work, agents MUST run: `ls .tickets/ | grep "ticket-" | sort -t '-' -k 2 -n`
- Agents MUST confirm they are working on the lowest-numbered ticket with pending tasks
- Agents MUST verify all previous tickets are either completed `[x]` or have no pending tasks

**TASK ORDER VERIFICATION:**
- Within each ticket's prd.md, agents MUST process tasks in exact document order
- Agents MUST NOT skip or reorder tasks based on perceived difficulty or preference
- Task order is SACROSANCT and represents critical dependency chains

**SUBTASK ORDER VERIFICATION:**
- Subtasks MUST be completed in strict numerical order (1.1, 1.2, 1.3, etc.)
- Completion of higher-numbered subtasks before lower-numbered ones is GROUNDS FOR IMMEDIATE TERMINATION
- Each subtask builds upon the previous one - order is NOT arbitrary

This comprehensive ticket management system ensures structured, testable, and traceable development workflow where AI agents can systematically work through subtasks and commit verified changes to the codebase.
