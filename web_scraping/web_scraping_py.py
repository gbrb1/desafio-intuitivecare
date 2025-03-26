import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import zipfile


BASE_URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"

ZIP_PATH = "Anexos.zip"  

# Dicionário com os nomes dos anexos que serão baixados
PDF_NAMES = {
    "Anexo I": "Anexo_I.pdf",
    "Anexo II": "Anexo_II.pdf"
}

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
        resposta.raise_for_status()  # Garantindo que uma exceção seja lançada em caso de erro
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

    # Procurando por todas as tags <a> que contenham atributo href
    for link in soup.find_all("a", href=True):
        # Pegando o texto do link e remove espaços desnecessários
        texto_link = link.get_text(strip=True)
        # Iterando sobre os nomes dos anexos que buscamos
        for anexo in PDF_NAMES.keys():
            # Verificando se o texto contém o nome do anexo
            if anexo in texto_link:
                # Pegando o valor do atributo href
                href = link['href']
                # Convertendo um link relativo em absoluto utilizando a URL base
                link_completo = urljoin(base_url, href)

                # Verificando se o anexo já foi adicionado para evitar duplicação
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
        resposta.raise_for_status()  # Verificando se o download foi bem-sucedido
        # Abrindo o arquivo no modo de escrita binária e escreve o conteúdo em partes
        with open(caminho_destino, "wb") as f:
            for chunk in resposta.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"PDF baixado e salvo em: {os.path.abspath(caminho_destino)}")  
    except requests.RequestException as e:
        raise requests.RequestException(f"Erro ao baixar {url}: {e}")


def compactar_pdfs(arquivos, arquivo_zip):
    """
    Compacta todos os arquivos PDF fornecidos em um único arquivo ZIP.
    
    Parâmetros:
    - arquivos: Lista de caminhos dos arquivos PDF a serem compactados.
    - arquivo_zip: Nome do arquivo ZIP a ser criado.
    """
    with zipfile.ZipFile(arquivo_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for arquivo in arquivos:
            zipf.write(arquivo, arcname=os.path.basename(arquivo))
            print(f"Arquivo {os.path.basename(arquivo)} adicionado ao ZIP.")
    print(f"Compactação concluída. Arquivo ZIP criado: {os.path.abspath(arquivo_zip)}")


def excluir_arquivos(arquivos):
    """
    Exclui os arquivos após a compactação.
    
    Parâmetros:
    - arquivos: Lista de arquivos a serem excluídos.
    """
    for arquivo in arquivos:
        try:
            os.remove(arquivo)
            print(f"Arquivo {arquivo} excluído com sucesso.")
        except OSError as e:
            print(f"Erro ao excluir {arquivo}: {e}")


def main():
    """
    Função principal que orquestra a execução dos passos do desafio:
    1. Acesso ao site e obtenção do HTML.
    2. Extração dos links dos PDFs utilizando a estrutura HTML.
    3. Download dos PDFs dos Anexos I e II.
    4. Compactação dos PDFs em um único arquivo ZIP.
    5. Exclusão dos arquivos PDFs temporários após a compactação.
    """
    # Passo 1: Obter o conteúdo HTML da página
    html = obter_conteudo(BASE_URL)
    if html is None:
        raise Exception("Não foi possível obter o conteúdo do site. Encerrando o script.")
    
    # Extraindo os links dos PDFs com base na análise do HTML
    links_pdf = extrair_links_pdfs(html, BASE_URL)
    
    # Verificando se os dois anexos foram encontrados
    if not all(anexo in links_pdf for anexo in PDF_NAMES.keys()):
        print("Não foi possível encontrar todos os links dos anexos. Verifique a estrutura da página e ajuste os seletores se necessário.")
        return

    # Fazendo o download de cada PDF encontrado
    arquivos_baixados = []
    for anexo, url_pdf in links_pdf.items():
        caminho_destino = PDF_NAMES[anexo]
        baixar_pdf(url_pdf, caminho_destino)
        arquivos_baixados.append(caminho_destino)
    
    # Compactando os PDFs baixados em um único arquivo ZIP
    compactar_pdfs(arquivos_baixados, ZIP_PATH)
    
    # Excluindo os arquivos PDFs temporários após a compactação
    excluir_arquivos(arquivos_baixados)


if __name__ == "__main__":
    main()
