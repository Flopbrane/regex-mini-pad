param(
    [switch] $SkipWordPressRuntime
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = "D:\Dev\venvs\venv_txt_edit312\Scripts\python.exe"
$SpecPath = Join-Path $ProjectRoot "regex-pad.spec"
$PyInstallerCachePath = Join-Path $env:LOCALAPPDATA "pyinstaller"

# PyInstallerで生成された onedir 版の EXE 名。
# dist 配下にこのフォルダが作られている前提です。
$AppDistName = "regex-pad"

# アプリ実行時に読み込む外部リソース。
# PyInstallerのspec側で同梱していない場合でも、ビルド後に確実にコピーします。
$ResourceSourcePath = Join-Path $ProjectRoot "resources"
$AssetSourcePath = Join-Path $ProjectRoot "assets"
$WordPressRuntimePath = Join-Path $ProjectRoot "runtime\wordpress-preview"
$DeletionListSourcePath = Join-Path $ProjectRoot "DELET_ITEMS_LIST.md"

function Copy-DirectoryFresh {
    param(
        [Parameter(Mandatory = $true)]
        [string] $SourcePath,

        [Parameter(Mandatory = $true)]
        [string] $DestinationPath
    )

    if (-not (Test-Path -LiteralPath $SourcePath)) {
        throw "Source directory was not found: $SourcePath"
    }

    if (Test-Path -LiteralPath $DestinationPath) {
        $ResolvedDestination = (Resolve-Path -LiteralPath $DestinationPath).Path
        $ExpectedDistRoot = [System.IO.Path]::GetFullPath((Join-Path $ProjectRoot "dist"))
        if (-not $ResolvedDestination.StartsWith($ExpectedDistRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to replace a directory outside project dist: $ResolvedDestination"
        }
        Remove-Item -LiteralPath $ResolvedDestination -Recurse -Force
    }

    $DestinationParent = Split-Path -Parent $DestinationPath
    if (-not (Test-Path -LiteralPath $DestinationParent)) {
        New-Item -ItemType Directory -Path $DestinationParent -Force | Out-Null
    }

    Copy-Item -LiteralPath $SourcePath -Destination $DestinationPath -Recurse -Force
}

function Copy-ReleaseDocumentation {
    param(
        [Parameter(Mandatory = $true)]
        [string] $SourceRoot,

        [Parameter(Mandatory = $true)]
        [string] $DestinationRoot
    )

    $DocumentFiles = @(
        "readme.txt", "readme_jp.txt", "LICENSE", "LICENSE.txt", "SOURCE_CODE.md",
        "README.md", "README_jp.md", "SCRIPT_STEP.md", "THIRD_PARTY_NOTICES.md"
    )
    $DocumentFolders = @("docs", "docs_jp", "LICENSES")

    $RequiredLicenseFiles = @(
        "qt-for-python\LGPL-3.0-only.txt", "qt-for-python\GPL-3.0-only.txt",
        "qt-for-python\GPL-2.0-only.txt", "qt-for-python\LicenseRef-Qt-Commercial.txt",
        "qt-for-python\SOURCES.md", "qt-virtual-keyboard\OpenWnn-NOTICE.txt",
        "qt-virtual-keyboard\PinyinIME-NOTICE.txt", "qt-virtual-keyboard\TCIME-COPYING.txt",
        "qt-virtual-keyboard\SOURCES.md"
    )

    # Validate the complete set before copying; the license notice is not generated.
    foreach ($Name in $DocumentFiles) {
        $SourcePath = Join-Path $SourceRoot $Name
        if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
            throw "Required release document was not found: $SourcePath"
        }
    }
    foreach ($Name in $DocumentFolders) {
        $SourcePath = Join-Path $SourceRoot $Name
        if (-not (Test-Path -LiteralPath $SourcePath -PathType Container)) {
            throw "Required release documentation folder was not found: $SourcePath"
        }
    }

    foreach ($Name in $RequiredLicenseFiles) {
        $SourcePath = Join-Path (Join-Path $SourceRoot "LICENSES") $Name
        if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
            throw "Required upstream license document was not found: $SourcePath"
        }
    }
    foreach ($Name in $DocumentFiles) {
        Copy-Item -LiteralPath (Join-Path $SourceRoot $Name) `
            -Destination (Join-Path $DestinationRoot $Name) -Force
    }
    foreach ($Name in $DocumentFolders) {
        $DestinationFolder = Join-Path $DestinationRoot $Name
        New-Item -ItemType Directory -Path $DestinationFolder -Force | Out-Null
        Get-ChildItem -LiteralPath (Join-Path $SourceRoot $Name) -Force | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $DestinationFolder -Recurse -Force
        }
    }
}

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python interpreter was not found: $PythonExe"
}

if (-not (Test-Path -LiteralPath $SpecPath)) {
    throw "PyInstaller spec file was not found: $SpecPath"
}

if (-not (Test-Path -LiteralPath $ResourceSourcePath)) {
    throw "resources directory was not found: $ResourceSourcePath"
}

Push-Location $ProjectRoot
try {
    $OriginalPath = $env:Path
    $OriginalSkipWordPressRuntime = $env:REGEXPAD_SKIP_WORDPRESS_RUNTIME
    $env:Path = (($OriginalPath -split ";") | Where-Object {
            $_ -notmatch "\\\.cache\\codex-runtimes" -and
            $_ -notmatch "\\\.codex\\tmp"
        }) -join ";"

    if ($SkipWordPressRuntime) {
        $env:REGEXPAD_SKIP_WORDPRESS_RUNTIME = "1"
    }
    else {
        $env:REGEXPAD_SKIP_WORDPRESS_RUNTIME = "0"
        & $PythonExe -m preview.package_runtime --runtime-root $WordPressRuntimePath
        if ($LASTEXITCODE -ne 0) {
            throw "WordPress runtime preparation failed with exit code $LASTEXITCODE"
        }
    }

    & $PythonExe -m PyInstaller --noconfirm --clean $SpecPath
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    $DistAppPath = Join-Path (Join-Path $ProjectRoot "dist") $AppDistName
    if (-not (Test-Path -LiteralPath $DistAppPath)) {
        throw "PyInstaller dist directory was not found: $DistAppPath"
    }

    $InternalPath = Join-Path $DistAppPath "_internal"
    if (-not (Test-Path -LiteralPath $InternalPath)) {
        throw "PyInstaller _internal directory was not found: $InternalPath"
    }
    Copy-Item -LiteralPath $DeletionListSourcePath -Destination (Join-Path $InternalPath "DELET_ITEMS_LIST.md") -Force

    # Translator が実行時に読む JSON を _internal\resources に配置します。
    Copy-DirectoryFresh `
        -SourcePath $ResourceSourcePath `
        -DestinationPath (Join-Path $InternalPath "resources")

    # 実行時にQIcon等で assets を参照する場合に備えて、assetsも同梱します。
    # assets が無い構成でもビルドを止めないよう、存在する場合だけコピーします。
    if (Test-Path -LiteralPath $AssetSourcePath) {
        Copy-DirectoryFresh `
            -SourcePath $AssetSourcePath `
            -DestinationPath (Join-Path $InternalPath "assets")
    }

    $RequiredTextFile = Join-Path $InternalPath "resources\app_text_en.json"
    if (-not (Test-Path -LiteralPath $RequiredTextFile)) {
        throw "Required resource was not copied: $RequiredTextFile"
    }

    $RequiredBridge = Join-Path $InternalPath "resources\wordpress_preview\bridge.mjs"
    if (-not (Test-Path -LiteralPath $RequiredBridge)) {
        throw "Required WordPress preview bridge was not copied: $RequiredBridge"
    }
    if (-not $SkipWordPressRuntime) {
        $BundledRuntimePath = Join-Path $InternalPath "runtime\wordpress-preview"
        & $PythonExe -m preview.package_runtime --verify --runtime-root $BundledRuntimePath
        if ($LASTEXITCODE -ne 0) {
            throw "Bundled WordPress verification failed with exit code $LASTEXITCODE"
        }
        Write-Host "WordPress preview runtime bundled at: $BundledRuntimePath"
    }

    Copy-ReleaseDocumentation -SourceRoot $ProjectRoot -DestinationRoot $DistAppPath

    Write-Host "Build completed."
    Write-Host "Copied resources to: $(Join-Path $InternalPath 'resources')"
    Write-Host "Copied release documentation beside regex-pad.exe: $DistAppPath"

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
    $env:REGEXPAD_SKIP_WORDPRESS_RUNTIME = $OriginalSkipWordPressRuntime
    Pop-Location
}
