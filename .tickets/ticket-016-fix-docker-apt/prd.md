# Fix Docker Build - Debian Bullseye Repository Issue

## 1. Problem Statement

The Docker build fails with GPG signature errors because `python:3.10-slim-bullseye` is based on Debian 11 (Bullseye), which reached end-of-life. The Debian repositories for Bullseye are no longer signed at the standard mirrors (`deb.debian.org`), causing apt-get update failures.

## 2. Proposed Solution

Upgrade the base image from `python:3.10-slim-bullseye` to `python:3.10-slim-bookworm` (Debian 12, current stable).

## 3. Acceptance Criteria

- Docker build completes successfully
- `make test` passes without apt errors
- No regressions in functionality

## 4. Dependencies

None - standalone fix

## 6. Subtask Checklist

- [x] Task 1: Update Dockerfile base image
  - **Problem**: Debian Bullseye repositories are EOL
  - **Test**: Dockerfile builds without apt errors
  - **Subtasks**:
    - [x] Subtask 1.1: Change FROM python:3.10-slim-bullseye to python:3.10-slim-bookworm
    - [x] Subtask 1.2: Verify build succeeds

- [x] Task 2: Test the fix
  - **Problem**: Ensure the change resolves the issue
  - **Test**: make test passes
  - **Subtasks**:
    - [x] Subtask 2.1: Run docker compose build
    - [x] Subtask 2.2: Run make test

- [x] Task 3: Fix test import paths
  - **Problem**: test_signal_handlers.py has incorrect import path
  - **Test**: All tests pass including signal handler test
  - **Subtasks**:
    - [x] Subtask 3.1: Fix sys.path to point to correct src directory
    - [x] Subtask 3.2: Fix import statement for new module location
