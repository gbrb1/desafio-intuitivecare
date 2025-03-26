import os
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from data_transformation.data_transformation_py import (executar_web_scraping, verificar_arquivo_pdf, 
                                                         extrair_tabela_pdf, salvar_csv, compactar_csv, 
                                                         substituir_abreviacoes, main, WEB_SCRAPING_PATH)

# Teste para a função executar_web_scraping
@patch("subprocess.run")
def test_executar_web_scraping(mock_run):
    """Testa a execução do web scraping verificando os parâmetros usados na chamada do subprocess.run"""
    
    # Configura o mock para retornar None (simulando execução bem-sucedida)
    mock_run.return_value = None
    
    # Executa a função que está sendo testada
    executar_web_scraping()
    
    # Prepara os caminhos esperados normalizados (para compatibilidade entre sistemas)
    expected_script = os.path.normpath(os.path.join(WEB_SCRAPING_PATH, "web_scraping_py.py"))
    expected_cwd = os.path.normpath(WEB_SCRAPING_PATH)
    
    # Debug: mostra os caminhos que estão sendo comparados
    print(f"Script esperado: {expected_script}")
    print(f"Diretório esperado: {expected_cwd}")
    
    # Verifica se o subprocess.run foi chamado exatamente uma vez
    mock_run.assert_called_once()
    
    # Obtém os argumentos usados na chamada
    args, kwargs = mock_run.call_args
    
    # Verificando cada componente individualmente:
    # 1. Caminho do script
    assert os.path.normpath(args[0][1]) == expected_script
    # 2. Flag check=True
    assert kwargs['check'] is True
    # 3. Diretório de trabalho
    assert os.path.normpath(kwargs['cwd']) == expected_cwd


def test_arquivo_existente():
    """Testa o cenário onde o arquivo PDF já existe no sistema"""
    
    # Configura o mock para simular que o arquivo existe
    with patch("data_transformation.data_transformation_py.os.path.exists", return_value=True):
        # Verifica se a função retorna True quando o arquivo existe
        assert verificar_arquivo_pdf() is True

def test_arquivo_criado_com_sucesso():
    """Testa o cenário onde o arquivo é criado com sucesso pelo web scraping"""
    
    # Configurando mocks para:
    # - Verificação de existência do arquivo (False depois True)
    # - Execução do web scraping
    with patch("data_transformation.data_transformation_py.os.path.exists") as mock_exists, \
         patch("data_transformation.data_transformation_py.executar_web_scraping") as mock_scraping:
        
        # Simula:
        # 1a chamada: arquivo não existe
        # 2a chamada: arquivo existe (após scraping)
        mock_exists.side_effect = [False, True]
        
        # Configurando o mock do scraping para retornar None (sucesso)
        mock_scraping.return_value = None
        
        # Verificando se retorna True após criar o arquivo
        assert verificar_arquivo_pdf() is True
        
        # Verificando se o scraping foi chamado uma vez
        mock_scraping.assert_called_once()

def test_falha_ao_criar_arquivo():
    """Testa o cenário onde o web scraping falha ao criar o arquivo"""
    
    # Configurando mocks para:
    # - Arquivo nunca existe
    # - Execução do scraping
    # - Captura de exceção
    with patch("data_transformation.data_transformation_py.os.path.exists", return_value=False), \
         patch("data_transformation.data_transformation_py.executar_web_scraping") as mock_scraping, \
         pytest.raises(Exception, match="não foi encontrado após a execução do script"):
        
        # Executando a função (que deve levantar exceção)
        verificar_arquivo_pdf()
        
        # Verificando se o scraping foi chamado
        mock_scraping.assert_called_once()


@patch("pdfplumber.open")
def test_extrair_tabela_pdf(mock_pdf):
    """Testa a extração de tabelas de um PDF"""
    
    # Configura mock do PDF com:
    # - 1 página
    # - Tabela simulada com cabeçalhos e dados
    mock_pdf.return_value.__enter__.return_value.pages = [MagicMock()]
    mock_page = MagicMock()
    mock_page.extract_table.return_value = [["Header", "Data"], ["Row1", "Value1"]]
    mock_pdf.return_value.__enter__.return_value.pages[0] = mock_page

    # Executa a extração
    df = extrair_tabela_pdf("path_to_pdf")
    
    # Verificações:
    # - Retorno é DataFrame
    assert isinstance(df, pd.DataFrame)
    # - Formato correto (1 linha, 2 colunas)
    assert df.shape == (1, 2)
    # - Cabeçalhos corretos
    assert df.columns[0] == "Header"
    # - Dados corretos
    assert df.iloc[0, 0] == "Row1"


@patch("pandas.DataFrame.to_csv")
def test_salvar_csv(mock_to_csv):
    """Testa o salvamento de DataFrame para CSV"""
    
    # Criando DataFrame de teste
    df = pd.DataFrame([["Row1", "Value1"]], columns=["Header", "Data"])
    salvar_csv(df, "path_to_csv")
    
    # Verifica se to_csv foi chamado com parâmetros corretos:
    # - Caminho do arquivo
    # - Sem índice
    # - Codificação utf-8-sig
    mock_to_csv.assert_called_once_with("path_to_csv", index=False, encoding='utf-8-sig')

# Teste para a função compactar_csv
@patch("zipfile.ZipFile")
def test_compactar_csv(mock_zipfile):
    """Testa a compactação do arquivo CSV para ZIP"""
    
    # Configura mock do ZipFile
    mock_zip = MagicMock()
    mock_zipfile.return_value.__enter__.return_value = mock_zip
    
    # Executa a compactação
    compactar_csv("path_to_csv", "path_to_zip")
    
    # Verifica se o arquivo foi adicionado ao ZIP
    mock_zip.write.assert_called_once_with("path_to_csv", os.path.basename("path_to_csv"))

# Teste para a função substituir_abreviacoes
def test_substituir_abreviacoes():
    """Testa a substituição de abreviações nos nomes das colunas"""
    
    # Cria DataFrame com colunas abreviadas
    df = pd.DataFrame({"OD": ["A", "B"], "AMB": ["C", "D"]})
    
    # Executa a substituição
    df_modificado = substituir_abreviacoes(df)
    
    # Verificações:
    # - Colunas renomeadas corretamente
    assert "Seg. Odontológica" in df_modificado.columns
    assert "Seg. Ambulatorial" in df_modificado.columns
    # - Colunas antigas removidas
    assert "OD" not in df_modificado.columns
    assert "AMB" not in df_modificado.columns

# Teste para a função main
@patch("data_transformation.data_transformation_py.verificar_arquivo_pdf")
@patch("data_transformation.data_transformation_py.extrair_tabela_pdf")
@patch("data_transformation.data_transformation_py.substituir_abreviacoes")
@patch("data_transformation.data_transformation_py.salvar_csv")
@patch("data_transformation.data_transformation_py.compactar_csv")
def test_main(mock_compactar_csv, mock_salvar_csv, mock_substituir_abreviacoes, 
             mock_extrair_tabela_pdf, mock_verificar_arquivo_pdf):
    """Testa o fluxo principal da aplicação"""
    
    # Configura mocks para todas as funções chamadas pela main
    mock_verificar_arquivo_pdf.return_value = True
    mock_extrair_tabela_pdf.return_value = pd.DataFrame([["Header", "Data"]])
    mock_substituir_abreviacoes.return_value = pd.DataFrame([["Row1", "Value1"]])
    
    # Executa a main verificando a saída impressa
    with patch("builtins.print") as mock_print:
        main()
        
        # Verifica se a mensagem final foi impressa
        mock_print.assert_any_call("Processo concluído com sucesso!")