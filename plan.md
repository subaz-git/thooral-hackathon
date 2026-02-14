# GSuite CLI Development Plan (Optimized)

## 0. Implementation Status (2026-02-13)

### Completed in Code
- `auth logout` implemented with token revocation attempt + local credential deletion.
- `docs edit` improved:
  - Added `--set` to replace full document content.
  - Updated append index handling to work reliably on empty and non-empty docs.
- Phase 2 Docs features implemented:
  - `docs copy <document_id> <new_title>`
  - `docs share <document_id> --email <email> --role <reader|writer|commenter>`
  - `docs get --format <plain_text|markdown>`
  - `docs get --output <file>`
  - `docs delete --yes` with confirmation prompt when `--yes` is not provided.
- Phase 3 Sheets MVP implemented:
  - `sheets create <title>`
  - `sheets list`
  - `sheets read <spreadsheet_id> <range>`
  - `sheets write <spreadsheet_id> <range> <data>`
  - `sheets clear <spreadsheet_id> <range>`
  - Sheets OAuth scope added (`https://www.googleapis.com/auth/spreadsheets`)
- Phase 4 Forms MVP implemented:
  - `forms create <title>`
  - `forms list`
  - `forms add-question <form_id> --type <text|paragraph|choice> --title <question_text> [--options ...]`
  - `forms get-responses <form_id>`
  - Forms scope upgraded to write-capable (`https://www.googleapis.com/auth/forms.body`)
- Service-layer refactor completed:
  - `services/config.py`
  - `services/credentials.py`
  - `services/auth_service.py`
  - `services/docs_service.py`
  - `services/forms_service.py`
  - `services/sheets_service.py`
  - `services/errors.py`
- Standardized CLI error output via shared helpers.
- Added CLI smoke tests in `tests/test_cli.py`.

### Remaining from Roadmap
- Quality hardening and advanced docs improvements.

## 1. Goal

Build a reliable CLI for Google Workspace automation (Docs, Sheets, Forms) with a focus on practical scripting use, clear errors, and predictable behavior.

## 2. Reality Check Against Current Repo

Based on `gsuite_cli.py`, the current implementation is:

### Implemented
- `auth login`
- `auth logout`
- `docs create <title>`
- `docs list`
- `docs get <document_id>`
- `docs get <document_id> --format <plain_text|markdown>`
- `docs get <document_id> --output <file>`
- `docs delete <document_id>` (with confirmation prompt)
- `docs delete <document_id> --yes`
- `docs edit <document_id> --append <text>`
- `docs edit <document_id> --set <text>`
- `docs copy <document_id> <new_title>`
- `docs share <document_id> --email <email> --role <reader|writer|commenter>`
- `sheets create <title>`
- `sheets list`
- `sheets read <spreadsheet_id> <range>`
- `sheets write <spreadsheet_id> <range> <data>`
- `sheets clear <spreadsheet_id> <range>`
- `forms create <title>`
- `forms list`
- `forms add-question <form_id> --type <text|paragraph|choice> --title <question_text> [--options ...]`
- `forms get-responses <form_id>`
- Shared services for config/credentials/auth/docs/sheets/forms/errors
- Basic CLI smoke tests (`tests/test_cli.py`)

### Not Implemented Yet
- Integration tests with real Google APIs
- Optional docs replace command (`docs edit --replace ...`)

## 3. Key Gaps and Risks

- Integration tests for real Google APIs are still missing.
- Existing users may need to re-authenticate to grant newly added Sheets/Forms scopes.
- Current tests are smoke-level and do not yet validate end-to-end API responses.

## 4. Optimized Roadmap

## Phase 1: Stability and Structure (High Priority)

### Deliverables
- Implement `auth logout`:
  - Revoke refresh token (when available).
  - Remove local credential file.
  - Return clear success/failure status.
- Make `docs edit` robust:
  - Add `--set` to replace document content safely.
  - Keep `--append` and route empty-doc first-write to a reliable flow.
- Refactor into modules (minimum):
  - `auth_service.py`, `docs_service.py`, shared credential/util layer.
- Standardize error format (single helper for API and auth errors).

### Exit Criteria
- `auth login` + `auth logout` tested manually end-to-end.
- `docs edit --append` works on empty and non-empty docs.
- Command behavior remains backward compatible for existing docs commands.

## Phase 2: Docs Feature Completion

### Deliverables
- `docs copy <document_id> <new_title>` (Drive `files.copy`)
- `docs share <document_id> --email <email> --role <reader|writer|commenter>`
- `docs get` enhancements:
  - `--output <file>`
  - `--format <plain_text|markdown>`
- `docs delete` safety option:
  - confirmation prompt by default
  - `--yes` flag for automation/non-interactive scripts
- Optional: simple `--replace <old> --with <new>` string replace

### Exit Criteria
- All docs commands return actionable errors.
- `docs get --output` creates valid files for common content.

## Phase 3: Sheets MVP

### Deliverables
- Add Sheets scopes required for read/write.
- Implement:
  - `sheets create <title>`
  - `sheets list` (Drive query by Sheets MIME type)
  - `sheets read <spreadsheet_id> <range>`
  - `sheets write <spreadsheet_id> <range> <data>`
  - `sheets clear <spreadsheet_id> <range>`

### Exit Criteria
- Round-trip test: write values then read back expected values.
- Command options are documented in README.

## Phase 4: Forms MVP

### Deliverables
- Implement:
  - `forms create <title>`
  - `forms list` (use Drive listing for form files)
  - `forms add-question ...` (Forms `batchUpdate`)
  - `forms get-responses <form_id>`

### Exit Criteria
- A form can be created, updated with at least one question type, and responses can be fetched.

## Phase 5: Quality Hardening

### Deliverables
- Unit tests for parsing, auth utilities, and command helpers.
- Integration test harness using a dedicated test Google account.
- Confirmation prompts for destructive commands (`docs delete`, future clear/delete commands).
- Optional config file support at `~/.gsuite_cli/config.yaml`.

### Exit Criteria
- Core happy-path commands covered by tests.
- Release checklist includes dependency and scope validation.

## 5. Technical Notes (Important)

- Forms listing should be done via Drive file listing by Forms MIME type; Forms API does not provide a broad "list all my forms" endpoint equivalent to Drive listing.
- Prefer least-privilege scopes and expand only when new commands require them.
- Keep command I/O script-friendly: stable plain-text output now, optional JSON output later.

## 6. Immediate Next Sprint (Recommended)

1. Implement optional `docs edit --replace <old> --with <new>`.
2. Add response formatting/export options for `forms get-responses`.
3. Add integration tests against a dedicated Google test account.
4. Add machine-readable output mode (`--json`) for scripting workflows.
