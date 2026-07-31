Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ([string]::Concat([char]0x65E0, [char]0x9700, [char]0x7C98, [char]0x8D34, ' TikHub Key'))

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Error 'WinGet is unavailable. Install uv from https://docs.astral.sh/uv/getting-started/installation/ and try again.'
    exit 1
}

winget install --id astral-sh.uv -e --accept-package-agreements --accept-source-agreements

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host 'uv is installed. Close and reopen the terminal, then run this script again.'
    exit 0
}

uv --version
