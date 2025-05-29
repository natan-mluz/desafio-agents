import os
import pandas as pd
from groq import Groq
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class CostAllocationCrew:
    def __init__(self):
        # Configuração do Groq LLM
        self.groq_client = Groq(
            api_key=os.getenv("GROQ_API_KEY"),
        )

        self.groq_llm = {
            "model":"mixtral-8x7b-32768",  # Modelo padrão do Groq
            "api_key": os.getenv("GROQ_API_KEY"),
            "temperature":0
        }
        
        self.data_path = "planilhas/"
        self.output_file = "planilhas/Resultado_Consolidado.xlsx"
        self.raw_data = {}
        
        # Configura os agentes
        self.setup_agents()
    
    def load_data(self):
        """Carrega todos os arquivos de dados necessários"""
        try:
            # Dados dos colaboradores
            self.raw_data['colaboradores'] = pd.read_excel(
                os.path.join(self.data_path, "Dados Colaboradores.xlsx")
            )
            
            # Ferramentas
            self.raw_data['github'] = pd.read_excel(
                os.path.join(self.data_path, "Ferramentas/Ferramenta 1 - Github.xlsx")
            )
            
            self.raw_data['google_workspace'] = pd.read_excel(
                os.path.join(self.data_path, "Ferramentas/Ferramenta 2 - Google workspace.xlsx")
            )
            
            # Benefícios
            self.raw_data['unimed'] = pd.read_excel(
                os.path.join(self.data_path, "Beneficios/Beneficio 1 - Unimed.xlsx")
            )
            
            self.raw_data['gympass'] = pd.read_excel(
                os.path.join(self.data_path, "Beneficios/Beneficio 2 - Gympass.xlsx")
            )
            
            print("Dados carregados com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            return False
    
    def setup_agents(self):
        """Configura os agentes CrewAI para o processamento"""
        # Agente para validação de dados
        self.data_validator = Agent(
            role='Especialista em Validação de Dados',
            goal='Validar a qualidade e consistência dos dados carregados',
            backstory='''
                Como um experiente analista de qualidade de dados, você é responsável por garantir
                que todos os dados carregados estejam completos, consistentes e prontos para processamento.
                Você verifica valores faltantes, formatos incorretos e anomalias nos dados.
            ''',
            allow_delegation=False,
            verbose=True,
            llm=self.groq_llm
        )
        
        # Agente para processamento de ferramentas
        self.tools_processor = Agent(
            role='Especialista em Processamento de Ferramentas',
            goal='Processar e consolidar dados de ferramentas corporativas',
            backstory='''
                Como especialista em ferramentas corporativas, você domina o processamento de dados
                de sistemas como GitHub e Google Workspace. Você sabe extrair, transformar e consolidar
                esses dados para análise de custos.
            ''',
            allow_delegation=False,
            verbose=True,
            llm=self.groq_llm
        )
        
        # Agente para processamento de benefícios
        self.benefits_processor = Agent(
            role='Especialista em Processamento de Benefícios',
            goal='Processar e consolidar dados de benefícios corporativos',
            backstory='''
                Como analista sênior de benefícios, você tem vasta experiência em processar dados
                de planos de saúde, gympass e outros benefícios. Você garante que os valores sejam
                corretamente alocados para cada colaborador.
            ''',
            allow_delegation=False,
            verbose=True,
            llm=self.groq_llm
        )
        
        # Agente para consolidação final
        self.consolidation_specialist = Agent(
            role='Especialista em Consolidação de Dados Financeiros',
            goal='Consolidar todos os dados em um relatório final',
            backstory='''
                Como especialista em consolidação financeira, você é responsável por integrar dados
                de múltiplas fontes e gerar relatórios precisos para tomada de decisão.
            ''',
            allow_delegation=False,
            verbose=True,
            llm=self.groq_llm
        )
    
    def create_validation_task(self):
        """Cria task para validação dos dados"""
        return Task(
            description='''
                Valide a qualidade dos dados carregados a partir dos arquivos Excel.
                Verifique:
                1. Se todas as colunas necessárias estão presentes em cada dataset
                2. Se há valores faltantes críticos
                3. Se os formatos dos dados estão corretos (CPF, valores monetários)
                4. Se há inconsistências nos dados
                
                Retorne um dicionário com:
                - 'status': True se os dados são válidos, False caso contrário
                - 'issues': Lista de problemas encontrados (vazia se nenhum)
            ''',
            agent=self.data_validator,
            expected_output='''
                Um dicionário Python contendo:
                {
                    'status': bool,
                    'issues': list[str]
                }
            ''',
            output_file=self.output_file.replace(".xlsx", "_validation_report.txt"),
            function=self._validate_data
        )
    
    def _validate_data(self):
        """Lógica de validação dos dados"""
        issues = []
        
        # Verifica dados dos colaboradores
        if 'colaboradores' not in self.raw_data:
            issues.append("Dados de colaboradores não carregados")
        else:
            cols = self.raw_data['colaboradores'].columns
            if 'CPF' not in cols and 'Documento' not in cols:
                issues.append("Coluna de identificação (CPF/Documento) faltante nos colaboradores")
        
        # Verifica ferramentas
        for tool in ['github', 'google_workspace']:
            if tool not in self.raw_data:
                issues.append(f"Dados da ferramenta {tool} não carregados")
            else:
                cols = self.raw_data[tool].columns
                if 'Documento' not in cols and 'CPF' not in cols:
                    issues.append(f"Coluna de identificação faltante na ferramenta {tool}")
                if 'Valor Mensal' not in cols:
                    issues.append(f"Coluna 'Valor Mensal' faltante na ferramenta {tool}")
        
        return {
            'status': len(issues) == 0,
            'issues': issues
        }
    
    def create_tools_processing_task(self):
        """Cria task para processamento das ferramentas"""
        return Task(
            description='''
                Processe e consolide os dados das ferramentas GitHub e Google Workspace.
                Use a coluna 'Documento' ou 'CPF' como chave de identificação.
                Considere apenas a coluna 'Valor Mensal' para o rateio.
                Trate valores faltantes como zero.
                Formate os valores como moeda ($) com 2 casas decimais.
            ''',
            agent=self.tools_processor,
            expected_output='''
                Um DataFrame pandas com as colunas:
                - Documento (str)
                - Valor_Github (str no formato $XX.XX)
                - Valor_Google_Workspace (str no formato $XX.XX)
            ''',
            output_file=self.output_file.replace(".xlsx", "_tools_processed.xlsx"),
            function=self._process_tools
        )
    
    def _process_tools(self):
        """Lógica de processamento das ferramentas"""
        try:
            # Processa GitHub
            github_cols = self.raw_data['github'].columns
            doc_col = 'Documento' if 'Documento' in github_cols else 'CPF'
            github_processed = self.raw_data['github'][[doc_col, 'Valor Mensal']].copy()
            github_processed.rename(
                columns={'Valor Mensal': 'Valor_Github', doc_col: 'Documento'},
                inplace=True
            )
            
            # Processa Google Workspace
            google_cols = self.raw_data['google_workspace'].columns
            doc_col = 'Documento' if 'Documento' in google_cols else 'CPF'
            google_processed = self.raw_data['google_workspace'][[doc_col, 'Valor Mensal']].copy()
            google_processed.rename(
                columns={'Valor Mensal': 'Valor_Google_Workspace', doc_col: 'Documento'},
                inplace=True
            )
            
            # Combina os dados
            tools_consolidated = pd.merge(
                github_processed,
                google_processed,
                on='Documento',
                how='outer'
            ).fillna(0)
            
            # Formata os valores
            tools_consolidated['Valor_Github'] = tools_consolidated['Valor_Github'].apply(
                lambda x: f"${float(x):.2f}"
            )
            tools_consolidated['Valor_Google_Workspace'] = tools_consolidated['Valor_Google_Workspace'].apply(
                lambda x: f"${float(x):.2f}"
            )
            
            return tools_consolidated
        except Exception as e:
            print(f"Erro ao processar ferramentas: {e}")
            return pd.DataFrame()
    
    def create_benefits_processing_task(self):
        """Cria task para processamento dos benefícios"""
        return Task(
            description='''
                Processe e consolide os dados dos benefícios Unimed e Gympass.
                Use a coluna 'CPF' ou 'Documento' como chave de identificação.
                Para Unimed, use a coluna 'Total'.
                Para Gympass, use a coluna 'Valor Mensal'.
                Trate valores faltantes como zero.
                Formate os valores como moeda ($) com 2 casas decimais.
            ''',
            agent=self.benefits_processor,
            expected_output='''
                Um DataFrame pandas com as colunas:
                - Documento (str)
                - Valor_Unimed (str no formato $XX.XX)
                - Valor_Gympass (str no formato $XX.XX)
            ''',
            output_file=self.output_file.replace(".xlsx", "_benefits_processed.xlsx"),
            function=self._process_benefits
        )
    
    def _process_benefits(self):
        """Lógica de processamento dos benefícios"""
        try:
            # Processa Unimed
            unimed_cols = self.raw_data['unimed'].columns
            doc_col = 'CPF' if 'CPF' in unimed_cols else 'Documento'
            value_col = 'Total' if 'Total' in unimed_cols else 'Valor Mensal'
            
            unimed_processed = self.raw_data['unimed'][[doc_col, value_col]].copy()
            unimed_processed.rename(
                columns={value_col: 'Valor_Unimed', doc_col: 'Documento'},
                inplace=True
            )
            
            # Processa Gympass
            gympass_cols = self.raw_data['gympass'].columns
            doc_col = 'Documento' if 'Documento' in gympass_cols else 'CPF'
            gympass_processed = self.raw_data['gympass'][[doc_col, 'Valor Mensal']].copy()
            gympass_processed.rename(
                columns={'Valor Mensal': 'Valor_Gympass', doc_col: 'Documento'},
                inplace=True
            )
            
            # Combina os dados
            benefits_consolidated = pd.merge(
                unimed_processed,
                gympass_processed,
                on='Documento',
                how='outer'
            ).fillna(0)
            
            # Formata os valores
            benefits_consolidated['Valor_Unimed'] = benefits_consolidated['Valor_Unimed'].apply(
                lambda x: f"${float(x):.2f}"
            )
            benefits_consolidated['Valor_Gympass'] = benefits_consolidated['Valor_Gympass'].apply(
                lambda x: f"${float(x):.2f}"
            )
            
            return benefits_consolidated
        except Exception as e:
            print(f"Erro ao processar benefícios: {e}")
            return pd.DataFrame()
    
    def create_consolidation_task(self, tools_data, benefits_data):
        """Cria task para consolidação final dos dados"""
        return Task(
            description='''
                Consolide todos os dados em um relatório final:
                1. Combine os dados de colaboradores com os dados processados
                2. Use CPF/Documento como chave de junção
                3. Renomeie 'Departamento' para 'Centro de Custo'
                4. Calcule o valor total por colaborador
                5. Formate todos os valores monetários como $ com 2 decimais
            ''',
            agent=self.consolidation_specialist,
            expected_output='''
                Um DataFrame pandas com relatório consolidado pronto para exportação,
                contendo todas as colunas especificadas e valores formatados corretamente.
            ''',
            output_file=self.output_file,
            function=lambda: self._consolidate_data(tools_data, benefits_data)
        )
    
    def _consolidate_data(self, tools_data, benefits_data):
        """Lógica de consolidação dos dados"""
        try:
            # Combina dados de ferramentas e benefícios
            combined_data = pd.merge(
                tools_data,
                benefits_data,
                on='Documento',
                how='outer'
            ).fillna(0)
            
            # Prepara dados dos colaboradores
            colaboradores = self.raw_data['colaboradores'].copy()
            colaboradores_cols = colaboradores.columns
            
            # Identifica colunas
            name_col = next(
                (col for col in ['Nome Colaborador', 'Nome', 'Colaborador'] 
                 if col in colaboradores_cols),
                colaboradores_cols[1]
            )
            
            cpf_col = next(
                (col for col in ['CPF', 'Documento'] 
                 if col in colaboradores_cols),
                colaboradores_cols[0]
            )
            
            # Combina com dados dos colaboradores
            final_data = pd.merge(
                colaboradores,
                combined_data,
                left_on=cpf_col,
                right_on='Documento',
                how='left'
            ).fillna(0)
            
            # Renomeia Departamento para Centro de Custo
            if 'Departamento' in final_data.columns:
                final_data = final_data.rename(columns={'Departamento': 'Centro de Custo'})
            
            # Calcula valor total
            numeric_cols = ['Valor_Github', 'Valor_Google_Workspace', 'Valor_Unimed', 'Valor_Gympass']
            for col in numeric_cols:
                if col in final_data.columns:
                    final_data[col] = final_data[col].replace('[\$,]', '', regex=True).astype(float)
            
            final_data['Valor_Total'] = final_data[numeric_cols].sum(axis=1)
            
            # Formata valores
            for col in numeric_cols + ['Valor_Total']:
                if col in final_data.columns:
                    final_data[col] = final_data[col].apply(lambda x: f"${float(x):.2f}")
            
            if 'Salario' in final_data.columns:
                final_data['Salario'] = final_data['Salario'].apply(lambda x: f"${float(x):.2f}")
            
            # Seleciona colunas finais
            report_cols = [
                name_col,
                cpf_col,
                'Centro de Custo' if 'Centro de Custo' in final_data.columns else 'Departamento',
                'Salario' if 'Salario' in final_data.columns else None,
                *[col for col in numeric_cols if col in final_data.columns],
                'Valor_Total'
            ]
            
            report_cols = [col for col in report_cols if col is not None]
            
            final_report = final_data[report_cols].copy()
            
            # Padroniza nomes das colunas
            final_report = final_report.rename(columns={
                name_col: 'Nome_Colaborador',
                cpf_col: 'CPF'
            })
            
            return final_report
        except Exception as e:
            print(f"Erro ao consolidar dados: {e}")
            return pd.DataFrame()
    
    def run(self):
        """Executa o fluxo completo de processamento"""
        try:
            # Carrega os dados
            if not self.load_data():
                raise Exception("Falha ao carregar dados")
            
            # Executa validação
            validation_task = self.create_validation_task()
            validation_crew = Crew(
                agents=[self.data_validator],
                tasks=[validation_task],
                verbose=True
            )
            validation_result = validation_crew.kickoff()
            
            if not validation_result['status']:
                print("\nProblemas encontrados na validação:")
                for issue in validation_result['issues']:
                    print(f"- {issue}")
                raise Exception("Dados inválidos - corrija os problemas antes de continuar")
            
            # Executa processamento paralelo
            tools_task = self.create_tools_processing_task()
            benefits_task = self.create_benefits_processing_task()
            
            processing_crew = Crew(
                agents=[self.tools_processor, self.benefits_processor],
                tasks=[tools_task, benefits_task],
                process=Process.sequential,  # Pode mudar para Process.parallel se suportado
                verbose=True
            )
            
            processing_results = processing_crew.kickoff()
            
            # Extrai resultados
            tools_result = processing_results[0] if isinstance(processing_results, list) else processing_results
            benefits_result = processing_results[1] if isinstance(processing_results, list) else processing_results
            
            # Executa consolidação
            consolidation_task = self.create_consolidation_task(tools_result, benefits_result)
            consolidation_crew = Crew(
                agents=[self.consolidation_specialist],
                tasks=[consolidation_task],
                verbose=True
            )
            final_result = consolidation_crew.kickoff()
            
            # Salva o resultado
            if not final_result.empty:
                final_result.to_excel(self.output_file, index=False)
                print(f"\nRelatório consolidado salvo em: {self.output_file}")
            else:
                print("\nErro: Relatório final está vazio")
            
            return final_result
            
        except Exception as e:
            print(f"\nErro durante a execução: {e}")
            return None

if __name__ == "__main__":
    crew = CostAllocationCrew()
    result = crew.run()