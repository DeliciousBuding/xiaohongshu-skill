param(
    [Parameter(Position = 0)]
    [ValidateSet("check", "test", "lint", "docs-check", "live", "site", "contracts")]
    [string]$Task = "check"
)

$ErrorActionPreference = "Stop"

function Invoke-DocsCheck {
    python -m scripts.docs_check
}

function Invoke-SiteCheck {
    python -m scripts.site_check
}

function Invoke-Lint {
    python -m ruff check scripts tests
}

function Invoke-Tests {
    python -m pytest -q
}

function Invoke-Live {
    $env:XHS_LIVE_TEST = "1"
    python -m pytest tests/live -q -m live
}

function Invoke-Site {
    python -m http.server 8000 --directory site
}

function Invoke-Contracts {
    python -m scripts contracts
    python -m scripts selectors
}

switch ($Task) {
    "docs-check" {
        Invoke-DocsCheck
        Invoke-SiteCheck
    }
    "lint" { Invoke-Lint }
    "test" { Invoke-Tests }
    "live" { Invoke-Live }
    "site" { Invoke-Site }
    "contracts" { Invoke-Contracts }
    "check" {
        Invoke-DocsCheck
        Invoke-SiteCheck
        Invoke-Lint
        Invoke-Tests
    }
}
