/* global github, context */
const workflows = [
    {name: "Run Trivy vulnerability scan", label: "Trivy"},
    {name: "Python Security Scan (Bandit)", label: "Bandit"},
    {name: "Safety Vulnerability Audit", label: "Safety"},
    {name: "pip-audit + license check", label: "pip-audit"},
    {name: "Detect Secrets", label: "Secrets"},
    {name: "Lint & Format", label: "Lint"},
    {name: "Run Tests w/ Coverage", label: "Tests"},
    {name: "Static Type Check (mypy)", label: "Mypy"},
    {name: "Run pre-commit hooks", label: "Pre-commit"}
];

(async () => {
    const sha = context.payload.pull_request.head.sha;
    const prNumber = context.payload.pull_request.number;
    const {owner, repo} = context.repo;

    const checks = await github.rest.checks.listForRef({
        owner,
        repo,
        ref: sha
    });

    function getIcon(conclusion) {
        switch (conclusion) {
            case "success":
                return "✔️";
            case "failure":
                return "❌";
            case "cancelled":
                return "⚠️";
            default:
                return "⏳";
        }
    }

    let coveragePercent = "–";
    const testCheck = checks.data.check_runs.find(r => r.name === "Run Tests w/ Coverage");
    if (testCheck?.output?.summary) {
        const match = testCheck.output.summary.match(/([\d.]+)% coverage/);
        if (match) {
            coveragePercent = match[1] + "%";
        }
    }

    const rows = workflows.map(wf => {
        const result = checks.data.check_runs.find(r => r.name === wf.name);
        const url = result?.html_url || `https://github.com/${owner}/${repo}/actions`;
        const icon = getIcon(result?.conclusion);
        const status = `[${icon}](${url})`;
        const extra = wf.label === "Tests" ? ` (${coveragePercent})` : "";
        return `| [${wf.label}](${url}) | ${status}${extra} |`;
    }).join("\n");

    const body = `### PR Status Summary

| Check | Status |
|-------|--------|
${rows}

<sub><sup>Updated automatically by pr-status-summary.js. Coverage is shown next to Tests.</sup></sub>`;

    const comments = await github.rest.issues.listComments({
        owner,
        repo,
        issue_number: prNumber
    });

    const existing = comments.data.find(comment =>
        comment.body.includes("PR Status Summary") &&
        comment.user.type === "Bot"
    );

    if (existing) {
        await github.rest.issues.updateComment({
            owner,
            repo,
            comment_id: existing.id,
            body
        });
    } else {
        await github.rest.issues.createComment({
            owner,
            repo,
            issue_number: prNumber,
            body
        });
    }
})();
