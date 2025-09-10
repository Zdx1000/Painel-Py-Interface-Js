<<<<<<< HEAD
# Painel-Py-Interface-Js
Painel grafico com alimentação em Python e interface em js
=======
# Projeto: Cadastro com GUI (PySide6) e Banco de Dados (SQLAlchemy + SQLite)

Este projeto fornece uma interface gráfica moderna para inserir, listar e excluir registros em um banco SQLite usando SQLAlchemy.

## Requisitos

- Python 3.10+
- Ambiente virtual ativo (recomendado)

## Instalação

1. Ative o ambiente virtual (se ainda não estiver ativo) e instale as dependências:

```powershell
# Na raiz do projeto
python -m pip install --upgrade pip; pip install -r requirements.txt
```

## Executando

```powershell
python servidor.py
```

O banco SQLite será criado automaticamente em `app/data/app.db` no primeiro uso.

## Estrutura

- `app/db/models.py` — modelos SQLAlchemy
- `app/db/database.py` — engine, sessão e inicialização do banco
- `app/db/repository.py` — operações CRUD
- `app/ui/main_window.py` — interface gráfica (PySide6)
- `servidor.py` — ponto de entrada

## Notas de Boas Práticas

- Camadas separadas (UI, repositório, modelos) para melhor manutenção e testes
- Tipagem estática e nomes claros
- Transações curtas com `commit` explícito
- Interface reativa com modelo de tabela

## Próximos Passos (Opcional)

- Validações avançadas de e-mail com regex/pydantic
- Edição inline e exclusão via tabela
- Filtros por período/categoria
>>>>>>> ec7103b (Start main Painel-Py-Interface-Js)

