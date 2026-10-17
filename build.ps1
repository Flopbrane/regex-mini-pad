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
        Remove-Item -LiteralPath $DestinationPath -Recurse -Force
    }

    $DestinationParent = Split-Path -Parent $DestinationPath
    if (-not (Test-Path -LiteralPath $DestinationParent)) {
        New-Item -ItemType Directory -Path $DestinationParent -Force | Out-Null
    }

    Copy-Item -LiteralPath $SourcePath -Destination $DestinationPath -Recurse -Force
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
    $env:Path = (($OriginalPath -split ";") | Where-Object {
            $_ -notmatch "\\\.cache\\codex-runtimes" -and
            $_ -notmatch "\\\.codex\\tmp"
        }) -join ";"

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

    Write-Host "Build completed."
    Write-Host "Copied resources to: $(Join-Path $InternalPath 'resources')"

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

# SIG # Begin signature block
# MIIFqgYJKoZIhvcNAQcCoIIFmzCCBZcCAQExDzANBglghkgBZQMEAgEFADB5Bgor
# BgEEAYI3AgEEoGswaTA0BgorBgEEAYI3AgEeMCYCAwEAAAQQH8w7YFlLCE63JNLG
# KX7zUQIBAAIBAAIBAAIBAAIBADAxMA0GCWCGSAFlAwQCAQUABCB3XdeknTKKinRJ
# zMlAy1no/tyt3L65qvRSQGkURLyrWqCCAxgwggMUMIIB/KADAgECAhBYeqtQhdAz
# iUeOfLlIHo4qMA0GCSqGSIb3DQEBCwUAMCIxIDAeBgNVBAMMF0YuS3Vyb2thd2Eg
# Q29kZSBTaWduaW5nMB4XDTI2MTAxNDAwNDgyOVoXDTI3MTAxNDAxMDgyOVowIjEg
# MB4GA1UEAwwXRi5LdXJva2F3YSBDb2RlIFNpZ25pbmcwggEiMA0GCSqGSIb3DQEB
# AQUAA4IBDwAwggEKAoIBAQC4PuGXD3IFJNFtRPomKqKw+GWVqYgNsq7/FYrIbBeM
# 1w4btBz0zk8rmMdZ+EuUBktYLz5zxRv9/TiZLmTsQ3m/LHrCjEaU9Tp5KgVM39Dc
# CQfvsxMMt08PnifB/lmg+pFerdPV9QASN7LUmFOOGi1JpAkhIAU5FfP79CgqXfDc
# uIl8A35VayCgTic4FzXoOGe4X6Jj9/gn6qxU6dUOp/fGA9K/UwusykSxVqLqLfp1
# aP9SKDON5NtHIG0eE8lq0FYzHI2FiLlnTw5R/ypPxDTzKIO2kb+KRHZ0qzGE+anf
# pWrCTTqMAlCUuJF7nzi1/pSJHSzJQDCv3dRw/iypekxhAgMBAAGjRjBEMA4GA1Ud
# DwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcDAzAdBgNVHQ4EFgQUxvSZOq0F
# J0bpRGlZk5C3YimMnugwDQYJKoZIhvcNAQELBQADggEBAKq06mYu4ePY+ENoSJaj
# 7lud+Z6Sw3+t+Jq7qFFYBZYaoW8WNzuhdxvh6WEH4v+wJT7aY/Sw7otvdkqQQrgL
# M7TdJZ/epWtmlAL3KRKJE7W2ZkJCeNrpZRpomnRzlkpGiMykR0vh9IIZEJH0Fbgc
# 79GYhIhVORvC5ke/8Nc6zbXQuRvdmX1wY3+fjJPAuATnct1M/Q7IxzGQOifeT26A
# xdAjoGphQyCO1+/pTfIDFkl7WT6tZ88r0n4q+vhx81Pj36/ZRKa6Z+6DqfhHEVNK
# /QN+RNSnk2H4bJNdJrG5wRb1o/tm4a6+W38vzbbD5zkNgrNmEAc0IqT6vf0Te3Ac
# NFcxggHoMIIB5AIBATA2MCIxIDAeBgNVBAMMF0YuS3Vyb2thd2EgQ29kZSBTaWdu
# aW5nAhBYeqtQhdAziUeOfLlIHo4qMA0GCWCGSAFlAwQCAQUAoIGEMBgGCisGAQQB
# gjcCAQwxCjAIoAKAAKECgAAwGQYJKoZIhvcNAQkDMQwGCisGAQQBgjcCAQQwHAYK
# KwYBBAGCNwIBCzEOMAwGCisGAQQBgjcCARUwLwYJKoZIhvcNAQkEMSIEIEHqJAmn
# zTC/p3SYeMZYavDE2bRTWSSgjMlWPSorQNkJMA0GCSqGSIb3DQEBAQUABIIBAGlm
# qnYXAlBIXwI02DqVjpI9qAeY1UyiI4GlievxgpHJFYrU7WA93LHzJIWXpf4DzUdp
# DlI7/tS6+Vyc1vqPxsos4ol0yodl5ZoZGkJNT9TSppd9JeWSUjmgKAzsXyHgDYnP
# biDi+H9oZ3DAc7ctZ1Ho8e0WR+Zimlob4LBl5U/JDUqo3+6Gt5gB7ooLYEBnrYJZ
# OfJ3AQouCaIgyFBOXaBYsqWPKZMFNex65d2z9kmgYDiuUTk7rPRvAz0Yo2zkV6ju
# PuIur45KqPjYt2++imH9AXrA01Byt0SYeeKl5D0Nc9AiW2UhGj5/zU2FLiNyNpSC
# FsG6zSl5nPHP1TYk414=
# SIG # End signature block
