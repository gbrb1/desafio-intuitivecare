import unittest
from unittest.mock import patch, MagicMock, call
import os
import zipfile
import pandas as pd
import subprocess
import pdfplumber

# Importando todas as funções a serem testadas
from data_transformation.data_transformation_py import (
    executar_web_scraping,
    extrair_pdf_do_zip,
    excluir_arquivos_temporarios,
    excluir_arquivo_zip,
    substituir_abreviacoes,
    extrair_tabela_pdf,
    salvar_csv,
    compactar_csv,
    ZIP_PATH, PDF_PATH, CSV_PATH, ZIP_CSV_PATH, WEB_SCRAPING_PATH
)

## 1. Testes para executar_web_scraping
@patch("subprocess.run")
def test_executar_web_scraping_success(mock_run):
    """Testa execução bem-sucedida do web scraping"""
    mock_run.return_value = MagicMock(returncode=0)
    
    try:
        executar_web_scraping()
        mock_run.assert_called_once_with(
            ["python", os.path.join(WEB_SCRAPING_PATH, "web_scraping_py.py")],
            check=True,
            cwd=WEB_SCRAPING_PATH
        )
    except Exception as e:
        assert False, f"Falha inesperada: {e}"

@patch("subprocess.run")
def test_executar_web_scraping_failure(mock_run):
    """Testa falha na execução do web scraping"""
    mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
    
    with unittest.TestCase().assertRaises(Exception) as context:
        executar_web_scraping()
    
    assert "Erro ao executar o script web_scraping_py.py" in str(context.exception)

## 2. Testes para extrair_pdf_do_zip
@patch("zipfile.ZipFile")
def test_extrair_pdf_do_zip_success(mock_zip):
    """Testa extração bem-sucedida do PDF"""
    # Configuração do mock
    mock_instance = MagicMock()
    mock_instance.namelist.return_value = ["Anexo_I.pdf"]
    mock_zip.return_value.__enter__.return_value = mock_instance
    
    # Execução
    extrair_pdf_do_zip(ZIP_PATH, PDF_PATH)
    
    # Verificação
    mock_instance.extract.assert_called_once_with("Anexo_I.pdf", WEB_SCRAPING_PATH)

@patch("zipfile.ZipFile")
def test_extrair_pdf_do_zip_file_not_found(mock_zip):
    """Testa quando o PDF não está no arquivo ZIP"""
    mock_instance = MagicMock()
    mock_instance.namelist.return_value = ["outro_arquivo.txt"]
    mock_zip.return_value.__enter__.return_value = mock_instance
    
    with unittest.TestCase().assertRaises(Exception) as context:
        extrair_pdf_do_zip(ZIP_PATH, PDF_PATH)
    
    assert "O arquivo Anexo_I.pdf não foi encontrado" in str(context.exception)

## 3. Testes para excluir_arquivos_temporarios
@patch("os.remove")
@patch("os.path.exists", side_effect=lambda x: True)
def test_excluir_arquivos_temporarios(mock_exists, mock_remove):
    """Testa exclusão dos arquivos temporários"""
    excluir_arquivos_temporarios()
    
    # Verifica se removeu ambos arquivos
    expected_calls = [call(PDF_PATH), call(CSV_PATH)]
    mock_remove.assert_has_calls(expected_calls, any_order=True)

@patch("os.remove")
@patch("os.path.exists", side_effect=lambda x: False)
def test_excluir_arquivos_temporarios_not_exists(mock_exists, mock_remove):
    """Testa quando os arquivos não existem"""
    excluir_arquivos_temporarios()
    mock_remove.assert_not_called()

## 4. Testes para excluir_arquivo_zip
@patch("os.remove")
@patch("os.path.exists", return_value=True)
def test_excluir_arquivo_zip(mock_exists, mock_remove):
    """Testa exclusão do arquivo ZIP"""
    excluir_arquivo_zip()
    mock_remove.assert_called_once_with(ZIP_PATH)

## 5. Testes para substituir_abreviacoes
def test_substituir_abreviacoes():
    """Testa substituição das abreviações"""
    df = pd.DataFrame({
        "OD": [1, 2],
        "AMB": [3, 4],
        "Outra": [5, 6]
    })
    
    result = substituir_abreviacoes(df)
    
    assert "Seg. Odontológica" in result.columns
    assert "Seg. Ambulatorial" in result.columns
    assert "Outra" in result.columns
    assert "OD" not in result.columns
    assert "AMB" not in result.columns

## 6. Testes para extrair_tabela_pdf
@patch("pdfplumber.open")
def test_extrair_tabela_pdf_success(mock_pdf):
    """Testa extração bem-sucedida da tabela"""
    # Configuração do mock
    mock_instance = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_table.return_value = [
        ["Código", "Descrição", "OD", "AMB"],
        ["123", "Exemplo", "1", "0"]
    ]
    mock_instance.pages = [mock_page]
    mock_pdf.return_value.__enter__.return_value = mock_instance
    
    # Mock da substituição de abreviações
    with patch('data_transformation.data_transformation_py.substituir_abreviacoes') as mock_sub:
        mock_sub.return_value = pd.DataFrame({
            "Código": ["123"],
            "Descrição": ["Exemplo"],
            "Seg. Odontológica": ["1"],
            "Seg. Ambulatorial": ["0"]
        })
        
        result = extrair_tabela_pdf(PDF_PATH)
        
        assert not result.empty
        mock_sub.assert_called_once()

## 7. Testes para salvar_csv
@patch("pandas.DataFrame.to_csv")
def test_salvar_csv_success(mock_to_csv):
    """Testa salvamento do CSV"""
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    
    salvar_csv(df, CSV_PATH)
    
    mock_to_csv.assert_called_once_with(
        CSV_PATH,
        index=False,
        encoding='utf-8-sig'
    )

## 8. Testes para compactar_csv
@patch("zipfile.ZipFile")
@patch("os.path.exists", return_value=True)
def test_compactar_csv_success(mock_exists, mock_zip):
    """Testa compactação bem-sucedida"""
    mock_instance = MagicMock()
    mock_zip.return_value.__enter__.return_value = mock_instance
    
    compactar_csv(CSV_PATH, ZIP_CSV_PATH)
    
    mock_instance.write.assert_called_once_with(
        CSV_PATH,
        os.path.basename(CSV_PATH)
    )

@patch("zipfile.ZipFile")
@patch("os.path.exists", return_value=False)
def test_compactar_csv_file_not_found(mock_exists, mock_zip):
    """Testa quando o arquivo não existe"""
    with unittest.TestCase().assertRaises(Exception) as context:
        compactar_csv(CSV_PATH, ZIP_CSV_PATH)
    
    # Verifica se a mensagem de erro contém o texto esperado
    assert "Arquivo CSV não encontrado" in str(context.exception)
    
    # Garante que o ZipFile não foi chamado
    mock_zip.assert_not_called()

if __name__ == "__main__":
    unittest.main()