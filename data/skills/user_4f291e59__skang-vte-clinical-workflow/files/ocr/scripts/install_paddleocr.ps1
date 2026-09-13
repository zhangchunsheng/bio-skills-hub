$ErrorActionPreference = "Stop"

$skillRoot = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $skillRoot ".venv-paddleocr"
$python = Join-Path $venv "Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    python -m venv $venv
}

& $python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "升级 PaddleOCR 隔离环境中的 pip 失败" }

& $python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
if ($LASTEXITCODE -ne 0) { throw "安装 PaddlePaddle CPU 版失败" }

& $python -m pip install paddleocr==3.5.0
if ($LASTEXITCODE -ne 0) { throw "安装 PaddleOCR 失败" }

& $python -c "import paddle, paddleocr; print('paddle', paddle.__version__); print('paddleocr', paddleocr.__version__)"
if ($LASTEXITCODE -ne 0) { throw "PaddleOCR 导入验证失败" }
