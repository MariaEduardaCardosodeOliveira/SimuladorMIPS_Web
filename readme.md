# Simulador MIPS

Este projeto é um **Simulador MIPS interativo** que executa código em linguagem Assembly MIPS, instrução por instrução, exibindo o conteúdo dos registradores, memória, programa e instruções em binário. É ideal para fins didáticos e estudo de Arquitetura e Organização de Computadores.

⚠️ Observação: Este simulador é focado em execução prática de instruções MIPS e chamadas de sistema, com suporte a entrada direta. Diretivas como 
.data, .text e rótulos foram omitidas intencionalmente para simplificar o foco didático na execução das instruções, registradores e memória. As strings e valores são carregados diretamente, como se já estivessem resolvidos pelo assembler.

## Como Executar o Projeto

### Pré-requisitos

- **Python 3.10 ou superior**
- **Bibliotecas necessárias:** `fastapi`, `uvicorn`, `pydantic`
- Um navegador moderno (Chrome, Firefox, Edge, etc.)

### 1. Instale as dependências do backend

```bash
pip install fastapi uvicorn pydantic
```

### 2. Execute o backend

- **No diretório onde está o arquivo main.py:**
```bash
python -m uvicorn backend.main:app --reload
```

### 3. Execute o frontend
- Abra o arquivo **index.html** no seu navegador (basta dar dois cliques ou abrir com o botão direito > "Abrir com navegador").

## Funcionalidades

- Suporte a instruções aritméticas e lógicas (`add`, `sub`, `mult`, `and`, `or`, `sll`, `slt`, `slti`)
- Instruções de carga imediata e memória (`li`, `lui`, `lw`, `sw`)
- Interface interativa com opções de:
  - Executar passo a passo
  - Executar tudo de uma vez
  - Executar devagar (com delay)
  - Exibir relatório final
- Exibição em tempo real de:
  - Saída do programa
  - Conteúdo dos registradores `$t0` a `$t9`
  - Conteúdo da memória
  - Valor do contador de programa (PC)
  - Instruções em binário MIPS

## Tecnologias Utilizadas

- **Backend:** Python 3.13 + FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Comunicação:** REST API com CORS habilitado



