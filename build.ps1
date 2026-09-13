$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe"
$SpecPath = Join-Path $ProjectRoot "regex-pad.spec"
$PyInstallerCachePath = Join-Path $env:LOCALAPPDATA "pyinstaller"

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python interpreter was not found: $PythonExe"
}

if (-not (Test-Path -LiteralPath $SpecPath)) {
    throw "PyInstaller spec file was not found: $SpecPath"
}

Push-Location $ProjectRoot
try {
    $OriginalPath = $env:Path
    $env:Path = (($OriginalPath -split ";") | Where-Object {
            $_ -notmatch "\\\.cache\\codex-runtimes" -and
            $_ -notmatch "\\\.codex\\tmp"
        }) -join ";"

    & $PythonExe -m PyInstaller --noconfirm --clean $SpecPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    if (Test-Path -LiteralPath $PyInstallerCachePath) {
        $LocalAppDataPath = (Resolve-Path -LiteralPath $env:LOCALAPPDATA).Path
        $ResolvedCachePath = (Resolve-Path -LiteralPath $PyInstallerCachePath).Path
        if (-not $ResolvedCachePath.StartsWith($LocalAppDataPath + [System.IO.Path]::DirectorySeparatorChar)) {
            throw "Refusing to remove unexpected PyInstaller cache path: $ResolvedCachePath"
        }
        Remove-Item -LiteralPath $ResolvedCachePath -Recurse -Force
    }
}
finally {
    if ($null -ne $OriginalPath) {
        $env:Path = $OriginalPath
    }
    Pop-Location
}
