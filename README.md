# 🧩 gRPC POC — Python Microservices Architecture

Este repositório demonstra uma arquitetura de **microserviços distribuídos** que se comunicam **somente via gRPC**. 

Cada serviço é independente e utiliza **Protocol Buffers (`.proto`)** para definir contratos de comunicação.

---

## 🧱 Estrutura do Projeto

```
grpc-poc/
├─ proto/                # Definições gRPC (.proto)
│   ├─ user.proto
│   ├─ order.proto
│   └─ report.proto
│
├─ services/             # Serviços independentes
│   ├─ user_service.py
│   ├─ order_service.py
│   ├─ report_service.py
│   └─ __init__.py
│
├─ clients/              # Clientes gRPC (CLI e demo)
│   ├─ demo.py
│   ├─ cli.py
│   └─ __init__.py
│
├─ generated/            # Código Python gerado pelo protoc
│   ├─ user_pb2.py
│   ├─ user_pb2_grpc.py
│   ├─ order_pb2.py
│   ├─ order_pb2_grpc.py
│   ├─ report_pb2.py
│   └─ report_pb2_grpc.py
│
├─ build.ps1             # Script para Windows (gera stubs e executa serviços)
├─ requirements.txt
└─ README.md
```

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia | Função |
|-------------|--------|
| 🐍 Python 3.11+ | Linguagem base |
| 💬 gRPC | Comunicação entre microserviços |
| 📦 Protocol Buffers | Definição dos contratos `.proto` |
| 🧰 grpcio-tools | Geração de código cliente/servidor |
| 🪟 PowerShell | Automação no Windows (`build.ps1`) |

---

## 🚀 Execução (Windows)

### 1️⃣ Clonar o repositório
```powershell
git clone https://github.com/SEU_USUARIO/grpc-poc.git
cd grpc-poc
```

### 2️⃣ Criar ambiente virtual
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3️⃣ Rodar o script de build e execução
```powershell
.uild.ps1
```

Escolha o serviço desejado:

| Opção | Serviço | Porta |
|--------|----------|-------|
| 1 | UserService | 50051 |
| 2 | OrderService | 50052 |
| 3 | ReportService | 50053 |
| 4 | Cliente de demonstração | — |

---

## 🧑‍💼 Serviços

### 🧑‍💼 UserService (porta 50051)
- CRUD simples de usuários (em memória)

### 📦 OrderService (porta 50052)
- Cria e lista pedidos
- Consulta usuários via gRPC (UserService)

### 📊 ReportService (porta 50053)
- Gera relatórios combinando usuários e pedidos
- Consulta ambos via gRPC

---

## 💻 Cliente de Demonstração

### Execução
```powershell
python -m clients.demo
```

### Saída esperada (exemplo)
```
Users created: [Alice, Bob]
Report Alice: orders=2, total=75.0
Top: Alice | count=2 total=75.0
Top: Bob | count=1 total=80.0
```

---

## 🧠 Conceitos Demonstrados

✅ Comunicação entre serviços via **Remote Procedure Calls (RPC)**  
✅ Contratos `.proto` como fonte única da verdade  
✅ Desacoplamento e isolamento entre domínios  
✅ Uso de *stubs* e *servicers* gerados automaticamente  
✅ Execução multiplataforma (Windows / Linux / macOS)

---

## 🛠️ Manutenção

Gerar novamente os stubs gRPC:
```bash
python -m grpc_tools.protoc -I proto --python_out=generated --grpc_python_out=generated proto/*.proto
```

Limpar artefatos:
```bash
rm -rf generated/__pycache__
```

---
