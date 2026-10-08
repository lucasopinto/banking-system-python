"""
Sistema Bancário - Projeto de gestão de clientes, contas e transações
Usa SQLite para persistência de dados.
"""

import sqlite3
from datetime import datetime


NOME_BANCO = "banco.db"


# ============================================================
# CAMADA DE BANCO DE DADOS
# ============================================================

def conectar():
    """Abre uma conexão com o banco de dados."""
    return sqlite3.connect(NOME_BANCO)


def criar_banco_dados():
    """Cria as tabelas do sistema, caso ainda não existam."""
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL UNIQUE,
        data_cadastro TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        numero_conta TEXT NOT NULL UNIQUE,
        tipo_conta TEXT NOT NULL,
        saldo REAL NOT NULL DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conta_id INTEGER NOT NULL,
        tipo TEXT NOT NULL,
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        FOREIGN KEY (conta_id) REFERENCES contas (id)
    )
    """)

    conexao.commit()
    conexao.close()


# ============================================================
# CLIENTES
# ============================================================

def cadastrar_cliente(nome, cpf):
    """Cadastra um novo cliente no banco de dados."""
    conexao = conectar()
    cursor = conexao.cursor()

    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")

    try:
        cursor.execute(
            "INSERT INTO clientes (nome, cpf, data_cadastro) VALUES (?, ?, ?)",
            (nome, cpf, data_atual)
        )
        conexao.commit()
        print(f"\nCliente '{nome}' cadastrado com sucesso!")
    except sqlite3.IntegrityError:
        print("\nErro: já existe um cliente com esse CPF.")
    finally:
        conexao.close()


def listar_clientes():
    """Lista todos os clientes cadastrados."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, cpf, data_cadastro FROM clientes")
    clientes = cursor.fetchall()
    conexao.close()

    if not clientes:
        print("\nNenhum cliente cadastrado ainda.")
        return

    print("\n--- CLIENTES CADASTRADOS ---")
    for cliente in clientes:
        id_cliente, nome, cpf, data_cadastro = cliente
        print(f"[{id_cliente}] {nome} | CPF: {cpf} | Cadastrado em: {data_cadastro}")


def buscar_cliente_por_id(cliente_id):
    """Retorna os dados de um cliente pelo ID."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, cpf FROM clientes WHERE id = ?", (cliente_id,))
    cliente = cursor.fetchone()
    conexao.close()
    return cliente


# ============================================================
# CONTAS
# ============================================================

def abrir_conta(cliente_id, tipo_conta):
    """Abre uma nova conta vinculada a um cliente."""
    cliente = buscar_cliente_por_id(cliente_id)
    if not cliente:
        print("\nErro: cliente não encontrado.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    # gera um número de conta simples baseado no id do cliente e timestamp
    numero_conta = f"{cliente_id:04d}-{datetime.now().strftime('%H%M%S')}"

    cursor.execute(
        "INSERT INTO contas (cliente_id, numero_conta, tipo_conta, saldo) VALUES (?, ?, ?, 0)",
        (cliente_id, numero_conta, tipo_conta)
    )
    conexao.commit()
    conexao.close()

    print(f"\nConta {tipo_conta} aberta para {cliente[1]}! Número da conta: {numero_conta}")


def buscar_conta(numero_conta):
    """Retorna os dados de uma conta pelo número."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, cliente_id, numero_conta, tipo_conta, saldo FROM contas WHERE numero_conta = ?",
        (numero_conta,)
    )
    conta = cursor.fetchone()
    conexao.close()
    return conta


def listar_contas():
    """Lista todas as contas, mostrando o nome do cliente dono de cada uma."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT contas.numero_conta, clientes.nome, contas.tipo_conta, contas.saldo
        FROM contas
        JOIN clientes ON contas.cliente_id = clientes.id
    """)
    contas = cursor.fetchall()
    conexao.close()

    if not contas:
        print("\nNenhuma conta cadastrada ainda.")
        return

    print("\n--- CONTAS ---")
    for conta in contas:
        numero, nome_cliente, tipo_conta, saldo = conta
        print(f"Conta {numero} | Titular: {nome_cliente} | Tipo: {tipo_conta} | Saldo: R$ {saldo:.2f}")


# ============================================================
# TRANSAÇÕES
# ============================================================

def registrar_transacao(conta_id, tipo, valor):
    """Registra uma transação no histórico."""
    conexao = conectar()
    cursor = conexao.cursor()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO transacoes (conta_id, tipo, valor, data) VALUES (?, ?, ?, ?)",
        (conta_id, tipo, valor, data_atual)
    )
    conexao.commit()
    conexao.close()


def depositar(numero_conta, valor):
    """Deposita um valor em uma conta."""
    if valor <= 0:
        print("\nErro: o valor do depósito deve ser positivo.")
        return

    conta = buscar_conta(numero_conta)
    if not conta:
        print("\nErro: conta não encontrada.")
        return

    conta_id, _, _, _, saldo_atual = conta
    novo_saldo = saldo_atual + valor

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, conta_id))
    conexao.commit()
    conexao.close()

    registrar_transacao(conta_id, "deposito", valor)
    print(f"\nDepósito de R$ {valor:.2f} realizado. Novo saldo: R$ {novo_saldo:.2f}")


def sacar(numero_conta, valor):
    """Saca um valor de uma conta, se houver saldo suficiente."""
    if valor <= 0:
        print("\nErro: o valor do saque deve ser positivo.")
        return

    conta = buscar_conta(numero_conta)
    if not conta:
        print("\nErro: conta não encontrada.")
        return

    conta_id, _, _, _, saldo_atual = conta

    if valor > saldo_atual:
        print(f"\nSaldo insuficiente. Saldo atual: R$ {saldo_atual:.2f}")
        return

    novo_saldo = saldo_atual - valor

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("UPDATE contas SET saldo = ? WHERE id = ?", (novo_saldo, conta_id))
    conexao.commit()
    conexao.close()

    registrar_transacao(conta_id, "saque", valor)
    print(f"\nSaque de R$ {valor:.2f} realizado. Novo saldo: R$ {novo_saldo:.2f}")


def transferir(numero_conta_origem, numero_conta_destino, valor):
    """Transfere um valor entre duas contas."""
    conta_origem = buscar_conta(numero_conta_origem)
    conta_destino = buscar_conta(numero_conta_destino)

    if not conta_origem or not conta_destino:
        print("\nErro: uma das contas não foi encontrada.")
        return

    saldo_origem = conta_origem[4]
    if valor > saldo_origem:
        print(f"\nSaldo insuficiente na conta de origem. Saldo atual: R$ {saldo_origem:.2f}")
        return

    sacar(numero_conta_origem, valor)
    depositar(numero_conta_destino, valor)
    print(f"\nTransferência de R$ {valor:.2f} concluída entre {numero_conta_origem} e {numero_conta_destino}.")


def extrato(numero_conta):
    """Mostra o histórico de transações de uma conta."""
    conta = buscar_conta(numero_conta)
    if not conta:
        print("\nErro: conta não encontrada.")
        return

    conta_id, _, numero, tipo_conta, saldo = conta

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT tipo, valor, data FROM transacoes WHERE conta_id = ? ORDER BY id DESC",
        (conta_id,)
    )
    transacoes = cursor.fetchall()
    conexao.close()

    print(f"\n--- EXTRATO DA CONTA {numero} ({tipo_conta}) ---")
    if not transacoes:
        print("Nenhuma transação registrada.")
    else:
        for tipo, valor, data in transacoes:
            print(f"{data} | {tipo.upper():10} | R$ {valor:.2f}")

    print(f"Saldo atual: R$ {saldo:.2f}")


# ============================================================
# RELATÓRIOS
# ============================================================

def relatorio_saldo_total():
    """Mostra o total de dinheiro sob custódia do banco."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT SUM(saldo) FROM contas")
    total = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM contas")
    num_contas = cursor.fetchone()[0]
    conexao.close()

    print("\n--- RELATÓRIO GERAL ---")
    print(f"Total de contas: {num_contas}")
    print(f"Saldo total sob custódia: R$ {total:.2f}")


def relatorio_maiores_saldos(limite=5):
    """Mostra os clientes com maiores saldos."""
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT clientes.nome, contas.numero_conta, contas.saldo
        FROM contas
        JOIN clientes ON contas.cliente_id = clientes.id
        ORDER BY contas.saldo DESC
        LIMIT ?
    """, (limite,))
    resultado = cursor.fetchall()
    conexao.close()

    print(f"\n--- TOP {limite} MAIORES SALDOS ---")
    if not resultado:
        print("Nenhuma conta cadastrada ainda.")
        return

    for posicao, (nome, numero_conta, saldo) in enumerate(resultado, start=1):
        print(f"{posicao}º | {nome} | Conta {numero_conta} | R$ {saldo:.2f}")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu():
    criar_banco_dados()

    opcoes = """
========================================
      SISTEMA BANCÁRIO
========================================
1. Cadastrar cliente
2. Listar clientes
3. Abrir conta
4. Listar contas
5. Depositar
6. Sacar
7. Transferir
8. Ver extrato
9. Relatório geral
10. Top maiores saldos
0. Sair
========================================
"""

    while True:
        print(opcoes)
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            nome = input("Nome do cliente: ").strip()
            cpf = input("CPF do cliente: ").strip()
            cadastrar_cliente(nome, cpf)

        elif opcao == "2":
            listar_clientes()

        elif opcao == "3":
            cliente_id = input("ID do cliente: ").strip()
            tipo_conta = input("Tipo de conta (corrente/poupanca): ").strip()
            if cliente_id.isdigit():
                abrir_conta(int(cliente_id), tipo_conta)
            else:
                print("\nID inválido.")

        elif opcao == "4":
            listar_contas()

        elif opcao == "5":
            numero_conta = input("Número da conta: ").strip()
            valor = input("Valor do depósito: ").strip()
            try:
                depositar(numero_conta, float(valor))
            except ValueError:
                print("\nValor inválido.")

        elif opcao == "6":
            numero_conta = input("Número da conta: ").strip()
            valor = input("Valor do saque: ").strip()
            try:
                sacar(numero_conta, float(valor))
            except ValueError:
                print("\nValor inválido.")

        elif opcao == "7":
            origem = input("Conta de origem: ").strip()
            destino = input("Conta de destino: ").strip()
            valor = input("Valor da transferência: ").strip()
            try:
                transferir(origem, destino, float(valor))
            except ValueError:
                print("\nValor inválido.")

        elif opcao == "8":
            numero_conta = input("Número da conta: ").strip()
            extrato(numero_conta)

        elif opcao == "9":
            relatorio_saldo_total()

        elif opcao == "10":
            relatorio_maiores_saldos()

        elif opcao == "0":
            print("\nEncerrando o sistema. Até logo!")
            break

        else:
            print("\nOpção inválida, tente novamente.")


if __name__ == "__main__":
    menu()