# Simulador RISC-V — Guia Rápido de Execução

Este projeto contém um simulador simples de RISC-V (32 bits).  
Abaixo estão apenas as instruções necessárias para executar o sistema.

---

## 1. Instale as dependências

```bash
pip install fastapi uvicorn pydantic
```

## 2. Inicie o backend

Abra um terminal na pasta backend:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

## 3. Inicie o frontend

Abra outro terminal na pasta frontend:

```bash
cd frontend
python -m http.server 5500
```

## 4. Abrir o simulador

Acesse no navegador:

```bash
http://localhost:5500
```

## 5. Executar um programa

Cole o código RISC-V no campo de texto e use:

Carregar

Passo

Executar tudo
