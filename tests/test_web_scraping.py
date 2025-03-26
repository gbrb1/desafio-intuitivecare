import os
from unittest.mock import patch, MagicMock, mock_open
from web_scraping.web_scraping_py import criar_diretorio, obter_conteudo, extrair_links_pdfs, baixar_pdf, compactar_pdfs

def test_criar_diretorio():
    """Testa a criação de diretórios verificando se os.makedirs é chamado corretamente"""
    with patch("os.makedirs") as mock_makedirs:
        # Diretório mockado como parâmetro
        criar_diretorio("test_dir")
        
        # Verifica se os.makedirs foi chamado <exatamente> uma vez com o parâmetro correto
        mock_makedirs.assert_called_once_with("test_dir")

@patch("requests.get")
def test_obter_conteudo(mock_get):
    """Testa a obtenção de conteúdo HTML de uma URL, simulando uma resposta HTTP"""

    mock_response = MagicMock()
    mock_response.text = "<html></html>"  # Simulando um html
    mock_get.return_value = mock_response
    
    url = "https://www.exemplo.com"
    html = obter_conteudo(url)
    assert html == "<html></html>" 
    mock_get.assert_called_once_with(url)

def test_extrair_links_pdfs():
    """Testa a extração de links PDF de um conteúdo HTML"""
    # HTML de teste contendo links para PDFs
    html = """
    <html>
        <body>
            <a href="/anexos/anexo1.pdf">Anexo I</a>
            <a href="/anexos/anexo2.pdf">Anexo II</a>
        </body>
    </html>
    """
      
    links = extrair_links_pdfs(html, "https://www.exemplo.com")
    
    assert "Anexo I" in links  # Link 1 encontrado
    assert "Anexo II" in links  # Link 2 encontrado
    assert links["Anexo I"] == "https://www.exemplo.com/anexos/anexo1.pdf"
    assert links["Anexo II"] == "https://www.exemplo.com/anexos/anexo2.pdf"

@patch("requests.get")
def test_baixar_pdf(mock_get):
    """Testa o download e salvamento de um arquivo PDF"""
    # Configura o mock da resposta de download
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"PDF CONTENT"]  # Conteúdo binário simulado
    mock_get.return_value = mock_response
    
    # Mock da função open para simular escrita de arquivo
    with patch("builtins.open", mock_open()) as mock_file:
        baixar_pdf("https://www.exemplo.com/anexo1.pdf", "test.pdf")
        
        # Escrita binária
        mock_file.assert_called_once_with("test.pdf", "wb")
        mock_file().write.assert_called_once_with(b"PDF CONTENT")

@patch("os.walk")
@patch("zipfile.ZipFile")
def test_compactar_pdfs(mock_zipfile, mock_os_walk):
    """Testa a compactação de arquivos PDF em um arquivo ZIP"""

    # Configura o mock do os.walk para simular a estrutura de diretórios
    mock_os_walk.return_value = [
        ("root", [], ["Anexo_I.pdf", "Anexo_II.pdf"])
    ]
    
    # Configura o mock do ZipFile
    mock_zip = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip
    
    compactar_pdfs("test_dir", "anexos.zip")
    

    # Cada PDF foi adicionado ao ZIP com o nome correto?
    mock_zip.write.assert_any_call(
        os.path.join("root", "Anexo_I.pdf"), 
        arcname="Anexo_I.pdf"
    )
    mock_zip.write.assert_any_call(
        os.path.join("root", "Anexo_II.pdf"), 
        arcname="Anexo_II.pdf"
    )