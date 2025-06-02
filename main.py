import pandas as pd
import os
from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Carregar variáveis de ambiente para a chave da API do Grok
load_dotenv()
CHAVE_API_GROK = os.getenv("GROK_API_KEY")

# Inicializar o modelo de linguagem (LLM) com ChatGroq usando o modelo grok-3
llm = ChatGroq(model="grok-3", api_key=CHAVE_API_GROK)

# Definir caminhos dos arquivos de entrada e saída
DIRETORIO_BASE = "Planilhas"
CAMINHO_COLABORADORES = os.path.join(DIRETORIO_BASE, "Dados Colaboradores.xlsx")
CAMINHO_GITHUB = os.path.join(DIRETORIO_BASE, "Ferramentas", "Ferramenta 1 - Github.xlsx")
CAMINHO_GOOGLE = os.path.join(DIRETORIO_BASE, "Ferramentas", "Ferramenta 2 - Google workspace.xlsx")
CAMINHO_UNIMED = os.path.join(DIRETORIO_BASE, "Beneficios", "Beneficio 1 - Unimed.xlsx")
CAMINHO_GYMPASS = os.path.join(DIRETORIO_BASE, "Beneficios", "Beneficio 2 - Gympass.xlsx")
CAMINHO_SAIDA = os.path.join(DIRETORIO_BASE, "Resultado_Final.xlsx")

# Definir agentes para cada etapa do processo
# Agente Leitor de Dados: responsável por ler e validar os arquivos Excel
agente_leitor_dados = Agent(
    role="Leitor de Dados",
    goal="Ler e validar arquivos Excel de entrada",
    backstory="Especialista em ler e validar dados estruturados de arquivos Excel, garantindo que os dados sejam carregados corretamente.",
    verbose=True,
    llm=llm
)

# Agente Limpeza de Dados: padroniza e limpa os dados
agente_limpeza_dados = Agent(
    role="Limpeza de Dados",
    goal="Limpar e padronizar dados de múltiplas fontes",
    backstory="Especialista em pré-processamento de dados, lidando com valores ausentes, formatos inconsistentes e padronização de colunas.",
    verbose=True,
    llm=llm
)

# Agente Fusão de Dados: combina dados de diferentes fontes
agente_fusao_dados = Agent(
    role="Fusão de Dados",
    goal="Fundir dados de diferentes fontes usando CPF como chave",
    backstory="Proficiente em integração de dados, garantindo junções precisas e completas entre conjuntos de dados.",
    verbose=True,
    llm=llm
)

# Agente Cálculo de Custos: calcula os custos totais por funcionário
agente_calculo_custos = Agent(
    role="Cálculo de Custos",
    goal="Calcular custos por funcionário com base em regras de negócio",
    backstory="Especialista em aplicar lógica de negócio para computar custos com precisão, somando salários e custos de ferramentas/benefícios.",
    verbose=True,
    llm=llm
)

# Agente Geração de Relatório: cria o relatório final em Excel
agente_gerador_relatorio = Agent(
    role="Geração de Relatório",
    goal="Gerar um relatório consolidado em Excel",
    backstory="Habilidoso em criar relatórios estruturados e claros, formatando dados para apresentação em formato Excel.",
    verbose=True,
    llm=llm
)

# Definir funções para as tarefas dos agentes
def ler_arquivos_excel():
    """
    Função para ler todos os arquivos Excel de entrada.
    Retorna um dicionário com DataFrames para cada arquivo.
    """
    try:
        # Ler os arquivos Excel usando pandas
        dados_colaboradores = pd.read_excel(CAMINHO_COLABORADORES)
        dados_github = pd.read_excel(CAMINHO_GITHUB)
        dados_google = pd.read_excel(CAMINHO_GOOGLE)
        dados_unimed = pd.read_excel(CAMINHO_UNIMED)
        dados_gympass = pd.read_excel(CAMINHO_GYMPASS)
        # Retornar dicionário com os DataFrames
        return {
            "colaboradores": dados_colaboradores,
            "github": dados_github,
            "google": dados_google,
            "unimed": dados_unimed,
            "gympass": dados_gympass
        }
    except Exception as e:
        # Retornar mensagem de erro em caso de falha
        return f"Erro ao ler arquivos: {str(e)}"

def limpar_dados(dados):
    """
    Função para limpar e padronizar os dados dos arquivos Excel.
    Padroniza nomes de colunas, renomeia 'documento' para 'cpf', trata valores ausentes e converte colunas numéricas.
    """
    for chave, df in dados.items():
        # Padronizar nomes das colunas: remover espaços, substituir por sublinhados e converter para minúsculas
        df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]
        # Preencher valores ausentes com 0
        df.fillna(0, inplace=True)
        # Renomear 'documento' para 'cpf' para ferramentas e alguns benefícios
        if chave in ["github", "google", "gympass"]:
            if "documento" in df.columns:
                df = df.rename(columns={"documento": "cpf"})
        # Limpar a coluna 'cpf' removendo sufixo "-XX" e espaços
        if "cpf" in df.columns:
            df["cpf"] = df["cpf"].str.replace("-XX", "", regex=False).str.strip()
        # Converter colunas numéricas para valores numéricos
        if "valor_mensal" in df.columns:
            df["valor_mensal"] = pd.to_numeric(df["valor_mensal"], errors="coerce").fillna(0)
        if "total" in df.columns:
            df["total"] = pd.to_numeric(df["total"], errors="coerce").fillna(0)
        dados[chave] = df
    return dados

def fundir_dados(dados):
    """
    Função para fundir os dados de todas as fontes usando CPF como chave.
    Realiza junções à esquerda para garantir que todos os colaboradores sejam incluídos.
    """
    colaboradores = dados["colaboradores"]
    # Selecionar e renomear colunas relevantes para cada ferramenta/benefício
    github = dados["github"][["cpf", "valor_mensal"]].rename(columns={"valor_mensal": "custo_github"})
    google = dados["google"][["cpf", "valor_mensal"]].rename(columns={"valor_mensal": "custo_google"})
    unimed = dados["unimed"][["cpf", "total"]].rename(columns={"total": "custo_unimed"})
    gympass = dados["gympass"][["cpf", "valor_mensal"]].rename(columns={"valor_mensal": "custo_gympass"})

    # Fundir os DataFrames usando 'cpf' como chave
    dados_fundidos = colaboradores.merge(github, on="cpf", how="left")
    dados_fundidos = dados_fundidos.merge(google, on="cpf", how="left")
    dados_fundidos = dados_fundidos.merge(unimed, on="cpf", how="left")
    dados_fundidos = dados_fundidos.merge(gympass, on="cpf", how="left")

    # Preencher valores NaN com 0 para colunas de custo
    colunas_custo = ["custo_github", "custo_google", "custo_unimed", "custo_gympass"]
    dados_fundidos[colunas_custo] = dados_fundidos[colunas_custo].fillna(0)
    return dados_fundidos

def calcular_custos(dados_fundidos):
    """
    Função para calcular o custo total por funcionário.
    Soma o salário com os custos de ferramentas e benefícios.
    """
    dados_fundidos["custo_total"] = (
        dados_fundidos["salario"] +
        dados_fundidos["custo_github"] +
        dados_fundidos["custo_google"] +
        dados_fundidos["custo_unimed"] +
        dados_fundidos["custo_gympass"]
    )
    return dados_fundidos

def gerar_relatorio(dados):
    """
    Função para gerar o relatório final em Excel.
    Seleciona colunas, renomeia para o formato desejado e formata valores monetários.
    """
    # Selecionar colunas para o relatório final
    saida = dados[["cpf", "nome", "departamento", "salario", "custo_github", "custo_google", "custo_unimed", "custo_gympass", "custo_total"]]
    # Renomear colunas para corresponder ao formato do exemplo
    saida = saida.rename(columns={
        "cpf": "CPF",
        "nome": "Nome_Colaborador",
        "departamento": "Centro_de_Custo",
        "salario": "Salario",
        "custo_github": "Github",
        "custo_google": "Google_workspace",
        "custo_unimed": "Unimed",
        "custo_gympass": "Gympass",
        "custo_total": "Valor_Total"
    })
    # Formatar colunas monetárias para o formato R$ X,XXX.XX
    colunas_monetarias = ["Salario", "Github", "Google_workspace", "Unimed", "Gympass", "Valor_Total"]
    for col in colunas_monetarias:
        saida[col] = saida[col].apply(lambda x: f"R$ {x:,.2f}")
    # Salvar o relatório em Excel
    saida.to_excel(CAMINHO_SAIDA, index=False)
    return f"Relatório gerado em {CAMINHO_SAIDA}"

# Definir tarefas para cada agente
tarefa_leitura = Task(
    description="Ler todos os arquivos Excel de entrada e validar sua estrutura.",
    expected_output="Dicionário contendo DataFrames do pandas para cada arquivo de entrada.",
    agent=agente_leitor_dados,
    execute=ler_arquivos_excel
)

tarefa_limpeza = Task(
    description="Limpar e padronizar dados de todos os arquivos de entrada, garantindo nomes de colunas consistentes e lidando com valores ausentes.",
    expected_output="Dicionário de DataFrames do pandas limpos.",
    agent=agente_limpeza_dados,
    execute=limpar_dados,
    dependencies=[tarefa_leitura]
)

tarefa_fusao = Task(
    description="Fundir dados de todas as fontes usando CPF como chave, garantindo que todos os funcionários sejam incluídos.",
    expected_output="Um único DataFrame do pandas com dados fundidos.",
    agent=agente_fusao_dados,
    execute=fundir_dados,
    dependencies=[tarefa_limpeza]
)

tarefa_calculo = Task(
    description="Calcular custos totais por funcionário somando salário e custos de ferramentas/benefícios.",
    expected_output="DataFrame com a coluna de custo total adicionada.",
    agent=agente_calculo_custos,
    execute=calcular_custos,
    dependencies=[tarefa_fusao]
)

tarefa_relatorio = Task(
    description="Gerar um relatório consolidado em Excel com as colunas especificadas e formato.",
    expected_output="Caminho para o arquivo Excel gerado.",
    agent=agente_gerador_relatorio,
    execute=gerar_relatorio,
    dependencies=[tarefa_calculo]
)

# Criar a equipe de agentes
equipe = Crew(
    agents=[agente_leitor_dados, agente_limpeza_dados, agente_fusao_dados, agente_calculo_custos, agente_gerador_relatorio],
    tasks=[tarefa_leitura, tarefa_limpeza, tarefa_fusao, tarefa_calculo, tarefa_relatorio],
    verbose=True
)

# Iniciar a execução da equipe
resultado = equipe.kickoff()
print(resultado)