Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host ([string]::Concat([char]0x65E0, [char]0x9700, [char]0x7C98, [char]0x8D34, ' TikHub Key'))

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Error 'WinGet is unavailable. Install uv from https://docs.astral.sh/uv/getting-started/installation/ and try again.'
    exit 1
}

winget install --id astral-sh.uv -e --accept-package-agreements --accept-source-agreements

if ($LASTEXITCODE -ne 0) {
    throw "WinGet installation failed with exit code $LASTEXITCODE."
}

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host 'uv may be installed. Close and reopen the terminal, then run this script again.'
    throw 'uv is unavailable in the current terminal session.'
}

uv --version

if ($LASTEXITCODE -ne 0) {
    throw "uv verification failed with exit code $LASTEXITCODE."
}

exit $LASTEXITCODE
