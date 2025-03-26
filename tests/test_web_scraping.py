import os
from unittest.mock import patch, MagicMock, mock_open
from web_scraping.web_scraping_py import obter_conteudo, extrair_links_pdfs, baixar_pdf, compactar_pdfs, excluir_arquivos

# Testa a obtenção de conteúdo HTML de uma URL
@patch("requests.get")
def test_obter_conteudo(mock_get):
    """Testa a obtenção de conteúdo HTML da URL."""
    mock_response = MagicMock()
    mock_response.text = "<html><body>Conteúdo</body></html>"  # HTML mockado
    mock_get.return_value = mock_response
    
    url = "https://www.exemplo.com"
    html = obter_conteudo(url)
    assert html == "<html><body>Conteúdo</body></html>"  # Verifica se o conteúdo retornado é o esperado
    mock_get.assert_called_once_with(url)  # Verifica se a URL foi chamada corretamente

# Testa a extração de links de PDFs
def test_extrair_links_pdfs():
    """Testa a extração de links PDF do HTML da página."""
    html = """
    <html>
        <body>
            <a href="/anexos/anexo1.pdf">Anexo I</a>
            <a href="/anexos/anexo2.pdf">Anexo II</a>
        </body>
    </html>
    """
    base_url = "https://www.exemplo.com"
    
    # Chama a função para extrair os links
    links = extrair_links_pdfs(html, base_url)
    
    # Verifica se os links foram extraídos corretamente
    assert "Anexo I" in links
    assert "Anexo II" in links
    assert links["Anexo I"] == "https://www.exemplo.com/anexos/anexo1.pdf"
    assert links["Anexo II"] == "https://www.exemplo.com/anexos/anexo2.pdf"

# Testa o download de um PDF
@patch("requests.get")
def test_baixar_pdf(mock_get):
    """Testa o download e o salvamento de um arquivo PDF."""
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"PDF CONTENT"]  # Conteúdo do PDF simulado
    mock_get.return_value = mock_response
    
    # Mock da função open para simular a escrita do arquivo
    with patch("builtins.open", mock_open()) as mock_file:
        baixar_pdf("https://www.exemplo.com/anexo1.pdf", "test.pdf")
        
        # Verifica se o arquivo foi aberto para escrita binária
        mock_file.assert_called_once_with("test.pdf", "wb")
        mock_file().write.assert_called_once_with(b"PDF CONTENT")

# Testa a compactação de arquivos PDF
@patch("zipfile.ZipFile")
def test_compactar_pdfs(mock_zipfile):
    """Testa a compactação de arquivos PDF em um arquivo ZIP."""
    arquivos = ["Anexo_I.pdf", "Anexo_II.pdf"]
    
    # Configura o mock do ZipFile
    mock_zip = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip
    
    # Chama a função para compactar os PDFs
    compactar_pdfs(arquivos, "anexos.zip")
    
    # Verifica se os arquivos foram adicionados ao ZIP
    mock_zip.write.assert_any_call("Anexo_I.pdf", arcname="Anexo_I.pdf")
    mock_zip.write.assert_any_call("Anexo_II.pdf", arcname="Anexo_II.pdf")

# Testa a exclusão de arquivos
@patch("os.remove")
def test_excluir_arquivos(mock_remove):
    """Testa a exclusão de arquivos após a compactação."""
    arquivos = ["Anexo_I.pdf", "Anexo_II.pdf"]
    
    # Chama a função para excluir os arquivos
    excluir_arquivos(arquivos)
    
    # Verifica se a função os.remove foi chamada para excluir os arquivos
    mock_remove.assert_any_call("Anexo_I.pdf")
    mock_remove.assert_any_call("Anexo_II.pdf")
