Este projeto desenvolve um agente de inteligência artificial para automatizar o rateio de custos corporativos, como ferramentas e benefícios, entre colaboradores, conforme o [Desafio DevOps](./Desafio%20DevOps.pdf). Utilizando o framework **CrewAI**, a solução processa planilhas Excel, consolida dados, calcula custos totais por funcionário e gera um relatório final.

A solução foi construída com:

- **Python**: Para manipulação e processamento de dados.
- **CrewAI**: Para orquestração de agentes autônomos.
- **Grok LLM (grok-3)**: Modelo de linguagem para suporte na inicialização de agentes.
- **Pandas**: Para manipulação de dados tabulares.
- **python-dotenv**: Para gerenciamento seguro de credenciais.

## Objetivos

- Automatizar a leitura e validação de planilhas Excel com dados de colaboradores, ferramentas (Github, Google Workspace) e benefícios (Unimed, Gympass).
- Padronizar e limpar dados para consistência.
- Fundir dados de múltiplas fontes usando o CPF como chave.
- Calcular o custo total por colaborador, incluindo salário e custos associados.
- Gerar um relatório consolidado em Excel com valores formatados (R$ X,XXX.XX).
- Demonstrar o uso de IA generativa e orquestração de agentes em automação financeira.

## Tecnologias Utilizadas

- **Python 3.10+**: Linguagem principal.
- **CrewAI**: Orquestração de agentes inteligentes.
- **Grok LLM (grok-3)**: Modelo de linguagem da xAI.
- **Pandas**: Manipulação de dados tabulares.
- **python-dotenv**: Gerenciamento de variáveis de ambiente.
- **openpyxl**: Leitura e escrita de arquivos Excel (.xlsx).

## Arquitetura da Solução

A aplicação utiliza cinco agentes com responsabilidades específicas:

### Agentes

- **Leitor de Dados**  
  Carrega e valida os arquivos Excel, garantindo a integridade dos dados.

- **Limpeza de Dados**  
  Padroniza colunas, trata valores ausentes e renomeia campos (e.g., "documento" para "cpf").

- **Fusão de Dados**  
  Une dados de todas as fontes usando o CPF como chave.

- **Cálculo de Custos**  
  Soma salários e custos de ferramentas/benefícios para calcular o custo total.

- **Geração de Relatório**  
  Produz o relatório final em Excel com formatação monetária.

## Funcionalidades

- **Leitura Automática**: Carrega arquivos `.xlsx` da pasta `Planilhas/`.
- **Validação de Dados**:
  - Verifica colunas obrigatórias (e.g., CPF, Nome, Valor Mensal).
  - Preenche valores ausentes com zeros.
  - Remove sufixos "-XX" de CPFs e padroniza formatos.
- **Processamento**:
  - Renomeia colunas para consistência (e.g., "documento" para "cpf").
  - Converte valores monetários para formato numérico.
- **Consolidação**:
  - Funde dados com junções à esquerda, garantindo inclusão de todos os colaboradores.
  - Calcula o custo total por funcionário.
- **Relatório**:
  - Gera `Resultado_Final.xlsx` com colunas: CPF, Nome_Colaborador, Centro_de_Custo, Salario, Github, Google_workspace, Unimed, Gympass, Valor_Total.
  - Formata valores no padrão R$ X,XXX.XX.

## Estrutura do Projeto
```
├── Planilhas/
│   ├── Dados Colaboradores.xlsx
│   ├── Ferramentas/
│   │   ├── Ferramenta 1 - Github.xlsx
│   │   ├── Ferramenta 2 - Google workspace.xlsx
│   ├── Beneficios/
│   │   ├── Beneficio 1 - Unimed.xlsx
│   │   ├── Beneficio 2 - Gympass.xlsx
│   ├── Resultado_Final.xlsx
├── .env
├── main.py
├── README.md
```

## Fluxo de Execução

1. **Inicialização**:  
   Carrega a chave da API do Grok e inicializa o modelo `grok-3`.

2. **Carregamento**:  
   Lê as planilhas de colaboradores, ferramentas e benefícios.

3. **Validação e Limpeza**:  
   Padroniza dados, trata valores ausentes e corrige formatos.

4. **Fusão**:  
   Combina dados usando o CPF como chave.

5. **Cálculo**:  
   Soma salários e custos para obter o custo total.

6. **Saída**:  
   Gera o relatório `Resultado_Final.xlsx`.

## Como Executar

1. **Clone o repositório**:
   ```bash
   git clone <url_do_repositorio>
   cd desafio-devops
   ```

2. **Instale as dependências**:
   ```bash
   pip install pandas crewai langchain-groq python-dotenv openpyxl
   ```

3. **Configure o arquivo `.env`**:
   Crie um arquivo `.env` na raiz com:
   ```
   GROK_API_KEY=sua_chave_groq
   ```
   Obtenha a chave em [https://x.ai/api](https://x.ai/api).

4. **Adicione as planilhas**:
   Coloque os arquivos Excel em `Planilhas/` conforme a estrutura.

5. **Execute o script**:
   ```bash
   python main.py
   ```

6. **Verifique o resultado**:
   O relatório estará em `Planilhas/Resultado_Final.xlsx`.

## Observações

- **Travamento na fase "Thinking..."**