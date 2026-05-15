# SECURITY-FINDINGS.md

OWASP Top 10 (2021) and financial-integrity security review of the LedgerBase
repository, plus GitHub Actions supply-chain hardening. Audit performed on the
state of branch `claude/security-audit-access-control-1jWov`.

## Scope and posture summary

LedgerBase is currently a Flask **scaffolding** repository. The ledger /
accounting *business logic* is not yet implemented:

- `src/ledgerbase/models.py` defines only an `ExampleModel`. There are **no
  ORM models** for ledger entries, accounts, transactions, users, or
  ownership relationships.
- `src/ledgerbase/__init__.py` exposes only `/`, `/login` (placeholder), and a
  `/debug-sentry` test route. There are **no routes that read or modify
  ledger entries**, no export endpoints (CSV/PDF), and no aggregation /
  reporting endpoints.
- `src/schema/init.sql` defines the eventual Postgres schema (institutions,
  accounts, vendors, vendor_patterns, transactions_normalized) but the schema
  has **no `user_id` / owner columns** and **no double-entry constraint**
  (debits-equal-credits).
- The only outbound integration is `src/services/plaid_service.py`, which
  posts to the Plaid REST API.

As a consequence, the OWASP A01/A02/A03 audit and the financial-integrity
checks are forward-looking: most findings are *preconditions to satisfy
before* user-owned ledger routes are written. The findings below distinguish
clearly between *issues fixed in this PR* and *requirements documented for
the not-yet-implemented features*.

---

## A01 — Broken Access Control

### A01-001 (status: forward-looking) — No ownership model exists yet

**Finding.** `src/schema/init.sql` defines `accounts`,
`transactions_normalized`, etc., with no `user_id` (or equivalent owner)
column. There is no `users` table. There are no Flask routes that read or
write ledger objects.

**Risk.** When the first ledger route is added without these prerequisites in
place, IDOR is almost guaranteed: a request like `GET
/transactions/<id>` would return any user's transaction.

**Requirement (must be satisfied before any ledger route ships).**

1. Add a `users` table and an `owner_user_id` foreign key (NOT NULL) to
   every user-scoped table: `institutions`, `accounts`,
   `transactions_normalized`, `vendor_patterns` if user-specific, and any
   future `ledger_entries` / `journals` table.
2. Add an index on `owner_user_id` for each of those tables.
3. Provide a single ownership-check helper (e.g.
   `get_owned_or_404(model, id)`) that every read/write route must use.
   Never query by primary key alone; always join with the owner.
4. Add tests that prove user A cannot read or modify user B's records,
   including via update/delete by ID and via aggregation endpoints.
5. Consider Postgres Row-Level Security as defence in depth, with a
   per-request `SET LOCAL app.current_user_id = ...`.

### A01-002 (status: forward-looking) — No authentication in place

**Finding.** The only `/login` handler (`src/ledgerbase/security.py:81`) is a
placeholder that returns the string `"Login attempt"`. There is no session
management, no CSRF protection wired up, and `SECRET_KEY` was previously
commented out (see A01-003).

**Requirement.** Before any ledger route ships:

- Use Flask-Login or an OAuth/OIDC stack with secure session cookies.
- Enable Flask-WTF (or equivalent) CSRF tokens on all state-changing routes.
- Enforce the existing rate limiter on auth endpoints (it is already
  configured at 5/min for `/login`; expand to `/register`, password reset,
  MFA, etc.).

### A01-003 (status: FIXED) — `SECRET_KEY` was unset / had unsafe default

**Finding (before fix).**
- `src/ledgerbase/__init__.py` had `app.config["SECRET_KEY"]` commented out,
  so Flask falls back to its own random key per process. Sessions and any
  signed tokens would silently invalidate across worker restarts.
- `src/ledgerbase/config.py` defaulted `SECRET_KEY` to the literal string
  `"unsafe-development-key"`. If `FLASK_ENV=production` was selected but
  `SECRET_KEY` was unset in the environment, production would silently come
  up with a known-public secret.

**Fix.**
- `src/ledgerbase/__init__.py`: requires `SECRET_KEY` (and `DATABASE_URL`)
  in production; generates a per-process random key only in
  non-production. Sets `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`,
  `SESSION_COOKIE_SAMESITE=Lax`, and `PREFERRED_URL_SCHEME=https` in
  production.
- `src/ledgerbase/config.py`: removed the `"unsafe-development-key"`
  default. `ProductionConfig.__init__` now fails fast if `SECRET_KEY` or
  `DATABASE_URL` is missing.

### A01-004 (status: FIXED) — `/debug-sentry` exposed in all environments

**Finding (before fix).** `src/ledgerbase/__init__.py` registered
`/debug-sentry` unconditionally. Anyone could trigger an
unhandled-exception path in production (denial of useful logs, alert
fatigue) by hitting it.

**Fix.** Route is now only registered when `FLASK_ENV != "production"`.

---

## A02 — Cryptographic Failures

### A02-001 (status: OK) — Encryption helper looks correct

**Finding.** `encryption.py` uses `cryptography.fernet.Fernet` (AES-128-CBC
with HMAC-SHA-256) with a list of keys loaded from
`current_app.config["LEDGERBASE_SECRET_KEYS"]`. The first key encrypts; all
keys are tried for decryption, which supports rotation. Errors are caught
without leaking key material.

**Recommendation (when adopted).** Document the rotation procedure (rotate
the list; keep at least one previous key until ciphertexts are re-encrypted
in batch). Confirm the keys themselves are stored in a KMS / secrets
manager — not in plaintext `.env` files committed alongside the app. The
existing SOPS configuration (`.sops.yaml`) is the right direction.

### A02-002 (status: forward-looking) — No fields are encrypted at rest

**Finding.** `src/schema/init.sql` stores `account_number_suffix`,
`raw_description`, `parsed_vendor`, and other potentially sensitive
financial data as plain `TEXT`. The Plaid integration handles
`access_token` values in `src/services/plaid_service.py` but there is no
storage layer for them yet.

**Requirement.** When Plaid `access_token`s, account numbers, or any PII are
persisted:

- Encrypt them using the `Encryptor` from `encryption.py` (column-level
  Fernet), or use a Postgres `pgcrypto` column.
- Never log decrypted values (see A09 logging note below).
- Use Postgres TDE / disk encryption at the storage layer as well.

### A02-003 (status: forward-looking) — No export endpoints exist

**Finding.** The task asked us to "verify any export functionality (CSV,
PDF) includes proper authorization." No such endpoints exist today.

**Requirement.** When CSV / PDF exports are added:

- They must apply the same `owner_user_id` filter as the underlying read
  endpoints. Never trust client-supplied filters such as `?user_id=…`.
- Stream rather than buffer (avoid memory-exhaustion DoS).
- Set `Content-Disposition: attachment; filename="…"` with a sanitised
  filename (no user-controlled path traversal).
- Set `X-Content-Type-Options: nosniff` (already globally applied).
- Rate-limit per user to prevent enumeration via export.

### A02-004 (status: improved) — Plaid responses no longer logged in full

**Finding (before fix).** `src/services/plaid_service.py` did
`print("Response:", response.text)` on every failed Plaid request. Plaid
responses can include `access_token`, `account_id`, account numbers, and
balances — none of which should appear in `stdout`/journald.

**Fix.** Replaced `print` with `logging.getLogger(__name__).warning` and
emit only `endpoint`, HTTP status, and the exception message — never the
response body. Also fail-fast if `BASE_URL`, `PLAID_CLIENT_ID`, or
`PLAID_SECRET` are missing rather than sending a request that would
otherwise echo the configuration error back.

---

## A03 — Injection

### A03-001 (status: OK) — All current DB access is parameterized

**Finding.** Searched the entire codebase for `execute(`, `text(`, and
f-string SQL construction:

```bash
$ grep -rn "execute\|raw\|text(" --include="*.py" src/ *.py
src/scripts/generate_review_request.py: read_text/write_text only (file I/O)
load_env.py:88: write_text (file I/O)
noxfile.py: read_text/write_text (file I/O)
```

No raw SQL is constructed anywhere in `src/`. The only data layer is
SQLAlchemy ORM in `src/ledgerbase/models.py`. Schema DDL in
`src/schema/init.sql` is static.

### A03-002 (status: forward-looking) — Reporting / aggregation not implemented

**Finding.** No reporting endpoints exist. The risk of dynamic query
construction is therefore latent.

**Requirement.** When reporting / aggregation endpoints are added:

- Build them with SQLAlchemy Core (`select`, `func.sum`, `group_by`) — not
  f-strings.
- For any user-controlled filter dimension (date range, account, category,
  vendor), pass values as bound parameters, validate them against an
  allow-list (e.g. for category enum), and reject sort/order arguments that
  are not in a server-side whitelist.

### A03-003 (status: OK with note) — Plaid request body construction

**Finding.** `src/services/plaid_service.py` builds JSON payloads
dictionary-style and passes them to `requests.post(..., json=...)`. There
is no string concatenation of user input into URLs or query parameters.
`endpoint` is the only string interpolated into the URL, but it is supplied
by trusted callers within the codebase (`/link/token/create`,
`/transactions/get`, etc.). Document this trust boundary if any caller
ever forwards user input as `endpoint`.

---

## Financial integrity

### FIN-001 (status: forward-looking) — No double-entry constraint exists

**Finding.** `transactions_normalized` is a single-sided ledger
(`amount NUMERIC(12,2)`, no paired debit/credit posting). There is no
`journals`/`postings` table and no enforcement that debits equal credits.

**Requirement.** When double-entry posting is introduced:

1. Add a `journal_entries` table (id, posted_at, description, owner_user_id)
   and a `postings` table (id, journal_entry_id, account_id, debit
   NUMERIC, credit NUMERIC, CHECK (debit >= 0 AND credit >= 0 AND (debit
   = 0) <> (credit = 0))).
2. Enforce per-journal balance:
   - Application-level: wrap insertions of all postings for a journal in a
     single transaction; raise if `SUM(debit) <> SUM(credit)`.
   - Database-level (defence in depth): use a deferred CHECK via trigger
     `AFTER INSERT/UPDATE/DELETE ON postings` that verifies the affected
     journal's debits equal its credits, or model as `CREATE CONSTRAINT
     TRIGGER … DEFERRABLE INITIALLY DEFERRED`.
3. Use `NUMERIC` everywhere (already correct in the schema). Never `FLOAT`.

### FIN-002 (status: forward-looking) — Race conditions on concurrent posts

**Finding.** With no posting code, this is latent. When implemented, two
concurrent transfers that touch the same account can interleave and produce
non-balanced or duplicate effects.

**Requirement.**

- Wrap each journal posting in an explicit DB transaction with `SET
  TRANSACTION ISOLATION LEVEL SERIALIZABLE` (or REPEATABLE READ with
  explicit `SELECT … FOR UPDATE` on affected `accounts` rows).
- Add a unique `external_id` (or idempotency key) on
  `transactions_normalized` / `journal_entries` so retries don't double-post.
- For Plaid sync (`sync_transactions`), persist and check the `cursor` so a
  retry on partial failure resumes rather than re-imports.
- Apply per-user / per-account rate limits to write endpoints to bound
  contention.

### FIN-003 (status: forward-looking) — Money handling guidance

**Requirement.** Continue using `NUMERIC(12, 2)` (or wider, e.g.
`NUMERIC(20, 4)` if multi-currency is on the roadmap). On the Python side,
use `decimal.Decimal` end-to-end — never `float`. Reject inputs that don't
round-trip to the schema scale. Store currency as a separate column
(ISO-4217) once a second currency is in scope.

---

## GitHub Actions hardening

### GHA-001 (status: FIXED) — Third-party actions pinned to immutable SHAs

A baseline pinning sweep was applied across every workflow under
`.github/workflows/` and `.github/workflows/templates/`. All third-party
`uses:` references now resolve to a 40-character commit SHA with a
trailing `# vX.Y.Z` comment for readability.

SHAs used (selected from already-pinned references in the repo or verified
on the upstream release page):

| Action | Version | SHA |
| --- | --- | --- |
| `actions/checkout` | v4.2.2 | `11bd71901bbe5b1630ceea73d27597364c9af683` |
| `actions/setup-python` | v5.3.0 | `0b93645e9fea7318ecaed2b359559ac225c90a2b` |
| `actions/setup-node` | v4.4.0 | `49933ea5288caeca8642d1e84afbd3f7d6820020` |
| `actions/upload-artifact` | v4.5.0 | `6f51ac03b9356f520e9adb1b1b7802705f340c2b` |
| `actions/download-artifact` | v4.3.0 | `d3f86a106a0bac45b974a628896c90dbdf5c8093` |
| `actions/cache` | v4.3.0 | `0057852bfaa89a56745cba8c7296529d2fc39830` |
| `actions/github-script` | v7.0.1 | `60a0d83039c74a4aee543508d2ffcb1c3799cdea` |
| `actions/stale` | v9.1.0 | `5bef64f19d7facfb25b37b414482c7164d639639` |
| `actions/dependency-review-action` | v4.5.0 | `67d4f4bd7a9b17a0db54d2a7519187c65e339de8` |
| `step-security/harden-runner` | v2.12.0 | `0634a2670c59f64b4a01f0f96f84700a4088b9f0` |
| `github/codeql-action/*` | v3.28.0 | `48ab28a6f5dbc2a99bf1e0131198dd8f1df78169` |
| `docker/setup-buildx-action` | v3.10.0 | `b5ca514318bd6ebac0fb2aedd5d36ec1b5c232a2` |
| `peaceiris/actions-gh-pages` | v4.0.0 | `4f9cc6602d3f66b9c108549d475ec49e8ef4d45e` |
| `codecov/codecov-action` | v5.5.0 | `fdcc8476540edceab3de004e990f80d881c6cc00` |
| `ossf/scorecard-action` | v2.4.0 | `62b2cac7ed8198b15735ed49ab1e5cf35480ba46` |
| `google-github-actions/auth` | v2.1.13 | `c200f3691d83b41bf9bbd8638997a462592937ed` |

Major-version upgrades performed during pinning:

- `actions/upload-artifact@v3` → v4 (cifuzzy.yml). v3 is end-of-life.
- `github/codeql-action/upload-sarif@v2` → v3 (cifuzzy.yml).
- `docker/setup-buildx-action@v2` → v3.10.0 (sbom.yml, security-trivy.yml).
- `google-github-actions/auth@v1` → v2.1.13 (prepare-poetry.yml,
  templates/assured-oss-auth.yml). v1 is end-of-life.

### GHA-002 (status: open, exceptions documented) — Remaining unpinned `uses:`

The following four references still target a moving ref and are documented
exceptions, not oversights:

| File | Reference | Why |
| --- | --- | --- |
| `.github/workflows/coverage.yml:26` | `ByronWilliamsCPA/.github/.github/workflows/python-qlty-coverage.yml@main` | Same-org reusable workflow. Same trust boundary as this repo. Pin to a tagged release once that org tags its workflows. |
| `.github/workflows/slsa-provenance.yml:103` | `ByronWilliamsCPA/.github/.github/workflows/python-slsa.yml@main` | As above. |
| `.github/workflows/cifuzzy.yml:52` | `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master` | Upstream `google/oss-fuzz` publishes CIFuzz actions only on `master` — no tags. Mitigation: the job runs `harden-runner` with `egress-policy: audit`; consider tightening to `block` once allow-listed endpoints are known. |
| `.github/workflows/cifuzzy.yml:57` | `google/oss-fuzz/infra/cifuzz/actions/run_fuzzers@master` | As above. |

### GHA-003 (status: FIXED) — `permissions:` blocks added where missing

Top-level `permissions:` blocks were added (default `contents: read`) to
workflows that had none:

- `.github/workflows/dev-checks.yml`
- `.github/workflows/gh-pages.yml` (job-level `contents: write` only on the
  deploy job)
- `.github/workflows/pre-commit.yml`
- `.github/workflows/repo-health.yml`
- `.github/workflows/wtd.yml` (job-level `pull-requests: write` only on
  the summary job)
- `.github/workflows/templates/prepare-poetry.yml`
- `.github/workflows/templates/assured-oss-auth.yml`

`scorecard.yml` was tightened from `permissions: read-all` to
`contents: read` at the top, with the analysis job declaring exactly
`security-events: write`, `id-token: write`, `contents: read`, `actions:
read`.

### GHA-004 (status: FIXED) — `step-security/harden-runner` added where missing

`harden-runner` (egress-policy: audit) was added to every job that did not
already have it, including:

- `gh-pages.yml`, `license.yml`, `release.yml`, `repo-health.yml`,
  `sbom.yml`, `wtd.yml`, `fips-compatibility.yml`,
  `security-pip-audit.yml`, `security-semgrep.yml`, `security-snyk.yml`,
  `weekly-check.yml` (aikido and code-hygiene jobs).
- All reusable templates: `nox-template.yml`, `nox-template-matrix.yml`,
  `python-template-pip.yml`, `assured-oss-auth.yml`, `generate-matrix.yml`,
  `lint-matrix.yml`, `test-matrix.yml`.

Recommended follow-up: once egress logs from `audit` mode have been
reviewed, switch `egress-policy` from `audit` to `block` with an explicit
`allowed-endpoints` list for each workflow. This is the highest-value
remaining hardening.

### GHA-005 (status: FIXED) — Shell-injection vector in `wtd.yml`

`.github/workflows/wtd.yml` previously interpolated
`${{ github.event.pull_request.number }}` and friends directly into a
shell command. While these particular fields are unlikely to be attacker-
controlled, the safer pattern is to expose them as env vars and reference
them via `"$VAR"`. Done.

### GHA-006 (status: deferred) — OSS-Fuzz CIFuzz on `@master`

See GHA-002 row 3 / 4. Tracked here so it isn't lost.

---

## Other observations (informational, not fixed)

- `src/ledgerbase/security.py` CSP allows `'unsafe-inline'` in
  `style-src`. Acceptable for an inline-style server-rendered admin UI but
  worth eliminating once the front-end stops needing it.
- `tests/` contains only placeholder tests
  (`pytest.assume(new=True)`). Once auth and ledger routes exist, the
  ownership-isolation tests required under A01-001 must be among the first
  real test additions.
- `Dockerfile`, `docker-compose.yml`, and the Plaid client all run as root
  / with default user — review when the image is wired into the deploy
  workflow.

---

## Summary table

| ID | Severity | Status |
| --- | --- | --- |
| A01-001 No ownership model | High (when implemented) | Forward-looking requirement |
| A01-002 No auth | High (when implemented) | Forward-looking requirement |
| A01-003 SECRET_KEY default | High | FIXED |
| A01-004 /debug-sentry exposed | Medium | FIXED |
| A02-001 Encryption helper | — | OK |
| A02-002 No field-level encryption | Medium (when implemented) | Forward-looking requirement |
| A02-003 No export auth | High (when implemented) | Forward-looking requirement |
| A02-004 Plaid logs body | Medium | FIXED |
| A03-001 ORM parameterization | — | OK |
| A03-002 Dynamic reporting | Medium (when implemented) | Forward-looking requirement |
| A03-003 Plaid URL construction | Low | OK with note |
| FIN-001 Double-entry constraint | High (when implemented) | Forward-looking requirement |
| FIN-002 Concurrent posts | High (when implemented) | Forward-looking requirement |
| FIN-003 Money types | — | OK with guidance |
| GHA-001 SHA pinning | Medium | FIXED (sweep applied) |
| GHA-002 Remaining `@main`/`@master` | Low | Documented exception |
| GHA-003 Permissions blocks | Medium | FIXED |
| GHA-004 harden-runner coverage | Medium | FIXED |
| GHA-005 wtd.yml interpolation | Low | FIXED |
| GHA-006 OSS-Fuzz on `@master` | Low | Deferred (upstream constraint) |
