# 🏦 Banking System (Python + SQLite)

🇧🇷 [Português](#-português) | 🇺🇸 [English](#-english)

---

## 🇧🇷 Português

### O que o projeto faz
Sistema bancário de linha de comando que gerencia **clientes, contas e transações**, com os dados salvos em um banco **SQLite**.

Funcionalidades:
- Cadastro e listagem de clientes (CPF único, validado pelo banco)
- Abertura de contas (corrente ou poupança) vinculadas a um cliente
- Depósito, saque (com verificação de saldo) e transferência entre contas
- Extrato com histórico de transações
- Relatórios: saldo total sob custódia e ranking dos maiores saldos

### Tecnologias
- Python 3
- SQLite (`sqlite3`, biblioteca padrão)
- SQL: `CREATE TABLE`, `INSERT`, `UPDATE`, `SELECT`, `JOIN`, `SUM`, `COUNT`, `ORDER BY`, `LIMIT`

### Modelo de dados
```
clientes (id, nome, cpf UNIQUE, data_cadastro)
contas (id, cliente_id → clientes.id, numero_conta UNIQUE, tipo_conta, saldo)
transacoes (id, conta_id → contas.id, tipo, valor, data)
```

### Como executar
```bash
git clone https://github.com/lucasopinto/banking-system-python.git
cd banking-system-python
python sistema_bancario.py
```
O arquivo `banco.db` é criado automaticamente na primeira execução. Não é preciso instalar nenhuma dependência.

### O que aprendi
- Modelar um banco relacional com chaves primárias, estrangeiras e restrição `UNIQUE`
- Usar consultas parametrizadas (`?`) para evitar SQL injection
- Fazer `JOIN` entre tabelas para montar listagens e relatórios
- Tratar erros como CPF duplicado (`IntegrityError`), saldo insuficiente e entradas inválidas
- Organizar o código em camadas: banco de dados, clientes, contas, transações e menu

---

## 🇺🇸 English

### What it does
A command-line banking system that manages **customers, accounts and transactions**, persisting data in a **SQLite** database.

Features:
- Register and list customers (unique CPF enforced by the database)
- Open checking or savings accounts linked to a customer
- Deposit, withdraw (with balance check) and transfer between accounts
- Account statement with transaction history
- Reports: total balance held and top balances ranking

### Tech stack
- Python 3
- SQLite (`sqlite3`, standard library)
- SQL: `CREATE TABLE`, `INSERT`, `UPDATE`, `SELECT`, `JOIN`, `SUM`, `COUNT`, `ORDER BY`, `LIMIT`

### How to run
```bash
git clone https://github.com/lucasopinto/banking-system-python.git
cd banking-system-python
python sistema_bancario.py
```
`banco.db` is created automatically on first run. No dependencies to install.

### What I learned
- Designing a relational schema with primary keys, foreign keys and `UNIQUE` constraints
- Using parameterized queries (`?`) to prevent SQL injection
- Using `JOIN`s to build listings and reports
- Handling errors such as duplicate CPF (`IntegrityError`), insufficient funds and invalid input
- Structuring code in layers: database, customers, accounts, transactions and menu
