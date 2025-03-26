import os
import subprocess
import pdfplumber
import pandas as pd
import zipfile

# Caminho para as pastas
WEB_SCRAPING_PATH = os.path.abspath(os.path.join(os.getcwd(), "..", "web_scraping"))
DOWNLOADS_PATH = os.path.join(WEB_SCRAPING_PATH, "Downloads")
PDF_PATH = os.path.normpath(os.path.join(DOWNLOADS_PATH, "Anexo_I.pdf"))

# Caminho para o arquivo CSV de saída
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(SCRIPT_DIR, "csv")
if not os.path.exists(CSV_DIR):
    os.makedirs(CSV_DIR)
CSV_PATH = os.path.join(CSV_DIR, "dados_rol_procedimentos.csv")
ZIP_PATH = os.path.join(os.getcwd(), "Teste_Gabriel.zip")

def executar_web_scraping():
    """Executa o script web_scraping.py para baixar o arquivo Anexo_I.pdf caso ele não exista."""
    try:
        print("O arquivo Anexo_I.pdf não foi encontrado. Executando o script web_scraping_py.py...")
        subprocess.run(["python", os.path.join(WEB_SCRAPING_PATH, "web_scraping_py.py")], check=True, cwd=WEB_SCRAPING_PATH)
        print("Script web_scraping.py executado com sucesso!")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erro ao executar o script web_scraping_py.py: {e}")

def verificar_arquivo_pdf():
    """Verifica se o arquivo Anexo_I.pdf existe e executa o web scraping se necessário."""
    if not os.path.exists(PDF_PATH):
        executar_web_scraping()
    if os.path.exists(PDF_PATH):
        print(f"O arquivo Anexo_I.pdf foi encontrado em {PDF_PATH}.")
        return True
    else:
        raise Exception("O arquivo Anexo_I.pdf não foi encontrado após a execução do script.")

def extrair_tabela_pdf(pdf_path):
    """Extrai tabelas do PDF."""
    try:
        print("Extraindo dados do PDF...")
        tabelas = []
        with pdfplumber.open(pdf_path) as pdf:
            
            for page in pdf.pages:  
                table = page.extract_table()
                if table:
                    tabelas.extend(table)
        
        if not tabelas:
            return pd.DataFrame()  

        # Convertendo para DataFrame
        df = pd.DataFrame(tabelas)
        
        if len(df) > 0:
            df.columns = df.iloc[0]  # Define a primeira linha como cabeçalho
            df = df[1:].reset_index(drop=True)  # Remove a primeira linha
            
        print("Dados extraídos com sucesso!")
        return df
    except Exception as e:
        raise Exception(f"Erro ao extrair dados do PDF: {e}")

def salvar_csv(df, csv_path):
    """Salva os dados extraídos em um arquivo CSV."""
    try:
        print(f"Salvando dados em CSV em {csv_path}...")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print("CSV salvo com sucesso!")
    except Exception as e:
        raise Exception(f"Erro ao salvar CSV: {e}")

def compactar_csv(csv_path, zip_path):
    """Compacta o arquivo CSV em um arquivo ZIP."""
    try:
        print(f"Compactando o CSV em {zip_path}...")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_path, os.path.basename(csv_path))
        print(f"Arquivo ZIP criado: {zip_path}")
    except Exception as e:
        raise Exception(f"Erro ao compactar CSV: {e}")



def substituir_abreviacoes(df):
    """
    Substitui as abreviações OD e AMB pelas descrições completas conforme a legenda.
    
    Parâmetros:
    - df: DataFrame contendo os dados extraídos.
    
    Retorna:
    - Um DataFrame com as abreviações substituídas pelas descrições completas.
    """
    try:
        print("Normalizando nomes das colunas...")

        print("Substituindo abreviações...")

        # Limpa os nomes das colunas removendo espaços extras e quebras de linha
        df.columns = df.columns.str.strip().str.replace(r"\n", " ", regex=True)

        # Renomeando as colunas como foi pedido
        df = df.rename(columns={"OD": "Seg. Odontológica", "AMB": "Seg. Ambulatorial"})


        print("Abreviações substituídas com sucesso!")
        return df
    except Exception as e:
        raise Exception(f"Erro ao substituir abreviações: {e}")



def main():
    """Função principal que executa todas as etapas do processo."""
    try:
        if not verificar_arquivo_pdf():
            return
        df = extrair_tabela_pdf(PDF_PATH)
        df = substituir_abreviacoes(df)
        salvar_csv(df, CSV_PATH)
        compactar_csv(CSV_PATH, ZIP_PATH)
        print("Processo concluído com sucesso!")
    except Exception as e:
        print(f"Erro no processo: {e}")

if __name__ == "__main__":
    main()