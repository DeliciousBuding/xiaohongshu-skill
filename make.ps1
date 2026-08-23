param(
    [Parameter(Position = 0)]
    [ValidateSet("check", "test", "lint", "docs-check", "live", "site", "contracts", "skill")]
    [string]$Task = "check"
)

$ErrorActionPreference = "Stop"
python -m scripts.quality $Task
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
