# ============================================
# gRPC POC - Build e execução (Windows)
# ============================================

# Força UTF-8 no console (evita "demonstraÃ§Ã£o")
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
try { chcp 65001 > $null } catch {}

Write-Host "Iniciando build.ps1..." -ForegroundColor Cyan

# Raiz do projeto
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

# PYTHONPATH: raiz e 'generated' (para user_pb2 importado dentro de *_pb2_grpc.py)
$env:PYTHONPATH = "$ROOT;$ROOT\generated"

# Garante pacotes Python (pastas com __init__.py)
$dirs = @("generated","services","clients")
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
    $init = Join-Path $d "__init__.py"
    if (-not (Test-Path $init)) { New-Item -ItemType File -Path $init | Out-Null }
}

# Compila os .proto
Write-Host "Gerando stubs gRPC..."
python -m grpc_tools.protoc `
  -I proto `
  --python_out=generated `
  --grpc_python_out=generated `
  proto\user.proto proto\order.proto proto\report.proto

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao gerar stubs .proto" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Geração concluída." -ForegroundColor Green
Write-Host ""

# Menu
Write-Host "Escolha o serviço para executar:"
Write-Host "1 - UserService (porta 50051)"
Write-Host "2 - OrderService (porta 50052)"
Write-Host "3 - ReportService (porta 50053)"
Write-Host "4 - Cliente de demonstração"
Write-Host ""
$opt = Read-Host "Digite a opção (1-4)"

switch ($opt) {
    1 {
        Write-Host "Iniciando UserService..."
        python -m services.user_service
    }
    2 {
        Write-Host "Iniciando OrderService..."
        $env:USERSVC_ADDR = "localhost:50051"
        python -m services.order_service
    }
    3 {
        Write-Host "Iniciando ReportService..."
        $env:USERSVC_ADDR = "localhost:50051"
        $env:ORDERSVC_ADDR = "localhost:50052"
        python -m services.report_service
    }
    4 {
        Write-Host "Executando cliente de demonstração..."
        # Tenta como pacote:
        try {
            python -m clients.demo
        } catch {
            Write-Host "Pacote 'clients' não encontrado; tentando executar como script..." -ForegroundColor Yellow
            python clients\demo.py
        }
    }
    Default {
        Write-Host "Opção inválida. Saindo..." -ForegroundColor Yellow
        exit 0
    }
}
