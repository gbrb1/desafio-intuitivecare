import os
import zipfile
import pdfplumber
import pandas as pd
import subprocess

# Caminho para a pasta web_scraping
WEB_SCRAPING_PATH = os.path.abspath(os.path.join(os.getcwd(), "..", "web_scraping"))

# Caminho para o arquivo ZIP e o PDF extraídos
ZIP_PATH = os.path.join(WEB_SCRAPING_PATH, "Anexos.zip")
PDF_PATH = os.path.join(WEB_SCRAPING_PATH, "Anexo_I.pdf")  # Arquivo PDF extraído do ZIP

# Obtendo o diretório onde o script tá localizado
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Definindo o caminho absoluto do arquivo CSV
CSV_PATH = os.path.abspath(os.path.join(os.getcwd(), "dados_rol_procedimentos.csv"))

# Caminho para o arquivo ZIP de saída do CSV
ZIP_CSV_PATH = os.path.join(SCRIPT_DIR, "Teste_Gabriel.zip")

def executar_web_scraping():
    """Executa o script web_scraping.py para baixar o arquivo Anexos.zip novamente."""
    try:
        print("O arquivo Anexos.zip não foi encontrado. Executando o script web_scraping_py.py...")
        subprocess.run(["python", os.path.join(WEB_SCRAPING_PATH, "web_scraping_py.py")], check=True, cwd=WEB_SCRAPING_PATH)
        print("Script web_scraping.py executado com sucesso!")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erro ao executar o script web_scraping_py.py: {e}")

def extrair_pdf_do_zip(zip_path, pdf_path):
    """Extrai o arquivo Anexo_I.pdf de Anexos.zip para a pasta web_scraping."""
    try:
        print(f"Extraindo {pdf_path} do arquivo ZIP {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Verifica se o arquivo Anexo_I.pdf está dentro do ZIP
            if "Anexo_I.pdf" in zipf.namelist():
                zipf.extract("Anexo_I.pdf", WEB_SCRAPING_PATH)  # Extrai para a pasta web_scraping
                print(f"Arquivo {pdf_path} extraído com sucesso!")
            else:
                raise Exception("O arquivo Anexo_I.pdf não foi encontrado no arquivo ZIP.")
    except Exception as e:
        raise Exception(f"Erro ao extrair o PDF do ZIP: {e}")

def excluir_arquivos_temporarios():
    """Exclui o arquivo Anexo_I.pdf e o CSV que ficaram do lado de fora."""
    if os.path.exists(PDF_PATH):
        os.remove(PDF_PATH)
        print(f"Arquivo {PDF_PATH} excluído com sucesso!")
    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)
        print(f"Arquivo {CSV_PATH} excluído com sucesso!")

def excluir_arquivo_zip():
    """Exclui o arquivo ZIP Anexos.zip se ocorrer um erro na extração."""
    if os.path.exists(ZIP_PATH):
        os.remove(ZIP_PATH)
        print(f"Arquivo {ZIP_PATH} excluído com sucesso!")

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
            
        # Substituir as abreviações nas colunas
        df = substituir_abreviacoes(df)
        
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
        
        # Verifica se o arquivo CSV existe antes de tentar compactar
        if not os.path.exists(csv_path):
            raise Exception(f"Arquivo CSV não encontrado: {csv_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_path, os.path.basename(csv_path))
        print(f"Arquivo ZIP criado: {zip_path}")
    except Exception as e:
        raise Exception(f"Erro ao compactar CSV: {e}")

def main():
    """Função principal que executa todas as etapas do processo."""
    try:
        # Se o arquivo ZIP não existir, executar o scraping novamente
        if not os.path.exists(ZIP_PATH):
            executar_web_scraping()
        
        # Extração do PDF do ZIP
        extrair_pdf_do_zip(ZIP_PATH, PDF_PATH)
        
        # Extração de dados do PDF
        df = extrair_tabela_pdf(PDF_PATH)
        
        # Excluir arquivos temporários (Anexo_I.pdf e CSV gerado)
        excluir_arquivos_temporarios()
        
        # Salvar os dados extraídos em um CSV
        salvar_csv(df, CSV_PATH)
        
        # Compactar o CSV gerado
        compactar_csv(CSV_PATH, ZIP_CSV_PATH)
        
        # Excluir o CSV após compactação
        os.remove(CSV_PATH)
        print(f"Arquivo {CSV_PATH} excluído após compactação.")
        
        print("Processo concluído com sucesso!")
    except Exception as e:
        print(f"Erro no processo: {e}")
        # Se o erro ocorrer ao extrair o PDF, exclua o ZIP e recomece o processo
        excluir_arquivo_zip()
        main()  # Reexecuta o processo

if __name__ == "__main__":
    main()
