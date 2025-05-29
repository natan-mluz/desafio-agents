# IA para Rateio de Custos com CrewAI e Groq LLM

## Descrição

Este projeto consiste no desenvolvimento de um Agente de IA para Rateio de Custos. O objetivo é automatizar o processo de alocação de custos corporativos (ferramentas e benefícios) entre colaboradores, consolidando todas as informações em um relatório final, conforme especificado no [Desafio DevOps](./Desafio%20DevOps.pdf).

A solução foi construída com:

- Python para processamento de dados.
- CrewAI para orquestração dos agentes autônomos.
- Groq LLM para apoio na execução inteligente das tarefas.
- Pandas para manipulação e transformação de dados.
- dotenv para gerenciamento seguro de credenciais.

## Objetivos

- Automatizar a leitura e validação de planilhas (.xlsx) com dados de colaboradores, ferramentas e benefícios.
- Consolidar e calcular o custo total por colaborador.
- Gerar um relatório final consolidado em Excel.
- Demonstrar a aplicação prática de IA generativa e orquestração de agentes para processos de automação.

## Tecnologias Utilizadas

- Python 3.10+
- CrewAI - Orquestração de múltiplos agentes inteligentes.
- Groq LLM - Modelo de linguagem (mixtral-8x7b-32768) para suporte nas decisões automatizadas.
- Pandas - Manipulação de dados tabulares.
- dotenv - Gerenciamento de variáveis de ambiente.

## Arquitetura da Solução

A aplicação é composta por um conjunto de agentes, cada um com responsabilidades específicas:

### Agentes

- Especialista em Validação de Dados  
  Garante a qualidade, consistência e integridade dos dados de entrada.

- Especialista em Processamento de Ferramentas  
  Responsável por consolidar os custos das ferramentas corporativas (GitHub, Google Workspace).

- Especialista em Processamento de Benefícios  
  Processa os custos relacionados aos benefícios (Unimed, Gympass).

- Especialista em Consolidação de Dados Financeiros  
  Integra os dados processados e gera o relatório final consolidado.

## Funcionalidades

- Carregamento automático de arquivos `.xlsx` a partir da pasta `planilhas/`.
- Validação de dados essenciais:
  - Presença de colunas obrigatórias (CPF, Documento, Valor Mensal etc.).
  - Detecção de valores faltantes.
  - Consistência de formatos.
- Processamento e formatação:
  - Cálculo de rateio por colaborador.
  - Formatação monetária padrão ($XX.XX).
- Consolidação:
  - Junção de todas as fontes de dados.
  - Cálculo do custo total.
  - Geração do relatório Resultado_Consolidado.xlsx.

## Estrutura do Projeto
├── planilhas/
│ ├── Dados Colaboradores.xlsx
│ ├── Ferramentas/
│ │ ├── Ferramenta 1 - Github.xlsx
│ │ └── Ferramenta 2 - Google workspace.xlsx
│ └── Beneficios/
│ ├── Beneficio 1 - Unimed.xlsx
│ └── Beneficio 2 - Gympass.xlsx
├── .env
├── main.py
├── README.md
└── Resultado_Consolidado.xlsx

## Fluxo de Execução

1. Inicialização:  
   O agente principal (CostAllocationCrew) é instanciado.

2. Carregamento dos Dados:  
   Planilhas de colaboradores, ferramentas e benefícios são carregadas.

3. Validação:  
   Conferência da estrutura e consistência dos dados.

4. Processamento:  
   - Ferramentas: GitHub e Google Workspace.  
   - Benefícios: Unimed e Gympass.

5. Consolidação:  
   Unificação das informações e geração do relatório final.

6. Saída:  
   O arquivo Resultado_Consolidado.xlsx é criado na pasta planilhas/.

## Como Executar

1. Clone o repositório:

2. Instale as dependências:
"pip install -r requirements.txt"

3. Configure a variável de ambiente no arquivo `.env`:
"GROQ_API_KEY=sua_chave_groq"

4. Insira as planilhas de entrada na pasta `planilhas/` conforme a estrutura indicada.

5. Execute o script:
"python main.py"

6. O relatório será gerado em:  
`planilhas/Resultado_Consolidado.xlsx`
