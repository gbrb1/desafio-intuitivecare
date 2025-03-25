import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import zipfile

# URL base do site que será acessado
BASE_URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"

# Diretório onde os arquivos baixados serão armazenados
DOWNLOAD_DIR = "downloads"

# Dicionário com os nomes dos anexos que desejamos baixar e os nomes que serão dados aos arquivos salvos
PDF_NAMES = {
    "Anexo I": "Anexo_I.pdf",
    "Anexo II": "Anexo_II.pdf"
}

def criar_diretorio(diretorio):
    """
    Cria o diretório especificado se ele ainda não existir.
    Essa função garante que haja um local para armazenar os arquivos baixados.
    """
    if not os.path.exists(diretorio):
        os.makedirs(diretorio)
        print(f"Diretório '{diretorio}' criado.")
    else:
        print(f"Diretório '{diretorio}' já existe.")

def obter_conteudo(url):
    """
    Realiza uma requisição HTTP GET para a URL informada e retorna o conteúdo HTML da página.
    
    Parâmetros:
    - url: String contendo a URL a ser acessada.

    Retorna:
    - O conteúdo HTML da página (string) se a requisição for bem-sucedida.
    - None se ocorrer algum erro.
    """
    try:
        resposta = requests.get(url)
        resposta.raise_for_status()  # Garante que uma exceção seja lançada em caso de erro
        print(f"Sucesso ao acessar {url}")
        return resposta.text
    except requests.RequestException as e:
        raise requests.RequestException(f"Erro ao acessar {url}: {e}")


def extrair_links_pdfs(html, base_url):
    """
    Extrai os links dos PDFs dos Anexos I e II a partir do HTML da página.
    
    Essa função utiliza o BeautifulSoup para analisar a estrutura HTML e identificar os links.
    Aqui, adotei uma estratégia inicial de buscar por tags <a> cujo texto contenha "Anexo I" ou "Anexo II", que se mostrou eficaz.
    
    Parâmetros:
    - html: String contendo o conteúdo HTML da página.
    - base_url: URL base para converter links relativos em links absolutos.

    Retorna:
    - Um dicionário com os nomes dos anexos (chaves) e os links completos (valores).
    """
    soup = BeautifulSoup(html, "html.parser")
    links_pdf = {}

    # Procura por todas as tags <a> que contenham atributo href
    for link in soup.find_all("a", href=True):
        # Pega o texto do link e remove espaços desnecessários
        texto_link = link.get_text(strip=True)
        # Itera sobre os nomes dos anexos que buscamos
        for anexo in PDF_NAMES.keys():
            # Verifica se o texto contém o nome do anexo (essa lógica pode ser ajustada conforme necessário)
            if anexo in texto_link:
                # Pega o valor do atributo href
                href = link['href']
                # Converte um link relativo em absoluto utilizando a URL base
                link_completo = urljoin(base_url, href)

                # Verifica se o anexo já foi adicionado para evitar duplicação
                if anexo not in links_pdf:
                    links_pdf[anexo] = link_completo
                    print(f"Link encontrado para {anexo}: {link_completo}")
    
    if not links_pdf:
        raise Exception("Nenhum link de PDF encontrado. Verifique a estrutura da página.")
    return links_pdf


def baixar_pdf(url, caminho_destino):
    """
    Faz o download do arquivo PDF da URL informada e o salva no caminho especificado.
    
    Parâmetros:
    - url: URL do arquivo PDF.
    - caminho_destino: Caminho (incluindo o nome do arquivo) onde o PDF será salvo.
    """
    try:
        resposta = requests.get(url, stream=True)
        resposta.raise_for_status()  # Verifica se o download foi bem-sucedido
        # Abre o arquivo no modo de escrita binária e escreve o conteúdo em partes
        with open(caminho_destino, "wb") as f:
            for chunk in resposta.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"PDF baixado e salvo em: {caminho_destino}")
    except requests.RequestException as e:
        raise requests.RequestException(f"Erro ao baixar {url}: {e}")


def compactar_pdfs(diretorio_origem, arquivo_zip):
    """
    Compacta todos os arquivos PDF presentes no diretório de origem em um único arquivo ZIP.
    
    Parâmetros:
    - diretorio_origem: Diretório onde os PDFs estão salvos.
    - arquivo_zip: Nome do arquivo ZIP a ser criado.
    """
    with zipfile.ZipFile(arquivo_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Percorre recursivamente o diretório para encontrar arquivos PDF
        for root, dirs, files in os.walk(diretorio_origem):
            for file in files:
                if file.lower().endswith(".pdf"):
                    caminho_completo = os.path.join(root, file)
                    # arcname define como o arquivo será nomeado dentro do ZIP
                    zipf.write(caminho_completo, arcname=file)
                    print(f"Arquivo {file} adicionado ao ZIP.")
    print(f"Compactação concluída. Arquivo ZIP criado: {arquivo_zip}")

def main():
    """
    Função principal que orquestra a execução dos passos do desafio:
    1. Criação do diretório de downloads.
    2. Acesso ao site e obtenção do HTML.
    3. Extração dos links dos PDFs utilizando a estrutura HTML.
    4. Download dos PDFs dos Anexos I e II.
    5. Compactação dos PDFs em um arquivo ZIP.
    """
    # Passo 1: Criar o diretório de downloads
    criar_diretorio(DOWNLOAD_DIR)
    
    # Passo 2: Obter o conteúdo HTML da página
    html = obter_conteudo(BASE_URL)
    if html is None:
        raise Exception("Não foi possível obter o conteúdo do site. Encerrando o script.")

    
    # Passo 3: Extrair os links dos PDFs com base na análise do HTML
    links_pdf = extrair_links_pdfs(html, BASE_URL)
    
    # Verifica se os dois anexos foram encontrados
    if not all(anexo in links_pdf for anexo in PDF_NAMES.keys()):
        print("Não foi possível encontrar todos os links dos anexos. Verifique a estrutura da página e ajuste os seletores se necessário.")
        return

    # Passo 4: Fazer o download de cada PDF encontrado
    for anexo, url_pdf in links_pdf.items():
        caminho_destino = os.path.join(DOWNLOAD_DIR, PDF_NAMES[anexo])
        baixar_pdf(url_pdf, caminho_destino)
    
    # Passo 5: Compactar os PDFs baixados em um único arquivo ZIP
    arquivo_zip = "anexos.zip"
    compactar_pdfs(DOWNLOAD_DIR, arquivo_zip)

if __name__ == "__main__":
    main()
