<# Recreate this project's Windows/Python 3.13 environment without copying .venv.
   Run: powershell -ExecutionPolicy Bypass -File scripts/setup_windows.ps1
   -VerifyOnly changes no packages. -SkipSam2/-SkipWeb are optional lighter setups.
#>
[CmdletBinding()]
param([switch]$VerifyOnly, [switch]$SkipSam2, [switch]$SkipWeb)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
$snapshotPath = Join-Path $projectRoot 'requirements\windows-py313-environment.json'
$snapshot = Get-Content -LiteralPath $snapshotPath -Raw | ConvertFrom-Json

function Invoke-Checked {
    param([string]$Executable, [string[]]$Arguments)
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: $Executable (exit $LASTEXITCODE)" }
}

if (-not (Test-Path -LiteralPath $venvPython)) {
    if ($VerifyOnly) { throw 'No .venv exists. Run setup without -VerifyOnly first.' }
    Invoke-Checked 'py' @('-3.13', '-m', 'venv', (Join-Path $projectRoot '.venv'))
}
$pythonMinor = & $venvPython -c 'import sys; print(sys.version_info.major, sys.version_info.minor, sep=chr(46))'
if ($LASTEXITCODE -ne 0) { throw 'Unable to inspect the existing virtual environment interpreter.' }
if ($pythonMinor.Trim() -ne '3.13') {
    throw 'Existing .venv is not Python 3.13. Preserve it under another name and create a Python 3.13 .venv; setup will not delete it.'
}
$env:YOLO_CONFIG_DIR = Join-Path $projectRoot 'outputs\yolo_settings'
$env:YOLO_OFFLINE = 'true'
$env:MPLBACKEND = 'Agg'
if (-not $VerifyOnly) {
    # --no-deps deliberately reproduces the complete observed package snapshot,
    # including its documented EasyOCR/headless OpenCV metadata warning. Resolving
    # EasyOCR afresh would install a second distribution into the same cv2 namespace.
    Invoke-Checked $venvPython @('-m', 'pip', 'install', '--no-deps', '-r', (Join-Path $projectRoot 'requirements\windows-py313.lock.txt'))
    if (-not $SkipSam2) {
        $samRoot = Join-Path $projectRoot 'sam2'
        if (-not (Test-Path -LiteralPath $samRoot)) {
            Invoke-Checked 'git' @('clone', '--no-checkout', $snapshot.sam2.repository, $samRoot)
            Invoke-Checked 'git' @('-C', $samRoot, 'checkout', '--detach', $snapshot.sam2.commit)
        }
        $samHead = & git -C $samRoot rev-parse HEAD
        if ($LASTEXITCODE -ne 0 -or $samHead.Trim() -ne $snapshot.sam2.commit) {
            throw 'Existing sam2 checkout differs from the snapshot; preserve its changes and reconcile it explicitly.'
        }
        $samChanges = & git -C $samRoot status --porcelain
        if ($samChanges) { throw 'sam2 has local changes. Setup will not overwrite them.' }
        $previousSamCuda = $env:SAM2_BUILD_CUDA
        try {
            $env:SAM2_BUILD_CUDA = '0'
            Invoke-Checked $venvPython @('-m', 'pip', 'install', '--no-deps', '--no-build-isolation', '--editable', $samRoot)
        } finally { $env:SAM2_BUILD_CUDA = $previousSamCuda }
    }
    if (-not $SkipWeb) {
        $webRoot = Join-Path $projectRoot 'apps\web'
        if (Test-Path -LiteralPath (Join-Path $webRoot 'package-lock.json')) {
            Invoke-Checked 'npm.cmd' @('--prefix', $webRoot, 'ci')
        } else { Invoke-Checked 'npm.cmd' @('--prefix', $webRoot, 'install') }
    }
}
$verifyArgs = @((Join-Path $projectRoot 'scripts\verify_environment.py'))
if ($SkipSam2) { $verifyArgs += '--skip-sam2' }
Invoke-Checked $venvPython $verifyArgs
Write-Output "Environment ready. Use $venvPython and the .venv\Scripts\yolo.exe executable explicitly."
