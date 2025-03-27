--item 3.5, ultimo trimestre


WITH dados_convertidos AS (
    SELECT 
        e.Razao_Social,
        e.Nome_Fantasia,
        e.Registro_ANS,
        dc.DATA,
        CAST(REPLACE(dc.VL_SALDO_FINAL, ',', '.') AS NUMERIC) AS saldo_final,
        CAST(REPLACE(dc.VL_SALDO_INICIAL, ',', '.') AS NUMERIC) AS saldo_inicial
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        Empresas e ON dc.REG_ANS = e.Registro_ANS
    WHERE 
        dc.DESCRICAO = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR '
        AND dc.DATA >= (SELECT MAX(DATA) FROM demonstracoes_contabeis) - INTERVAL '3 months'
)
SELECT 
    Registro_ANS,
    Razao_Social,
    Nome_Fantasia,
    SUM(saldo_final - saldo_inicial) AS despesa_total
FROM 
    dados_convertidos
GROUP BY 
    Registro_ANS, Razao_Social, Nome_Fantasia
ORDER BY 
    despesa_total DESC
LIMIT 10;





---------- 1 ano


WITH dados_convertidos AS (
    SELECT 
        e.Razao_Social,
        e.Nome_Fantasia,
        e.Registro_ANS,
        dc.DATA,
        CAST(REPLACE(dc.VL_SALDO_FINAL, ',', '.') AS NUMERIC) AS saldo_final,
        CAST(REPLACE(dc.VL_SALDO_INICIAL, ',', '.') AS NUMERIC) AS saldo_inicial
    FROM 
        demonstracoes_contabeis dc
    JOIN 
        Empresas e ON dc.REG_ANS = e.Registro_ANS
    WHERE 
        dc.DESCRICAO = 'EVENTOS/ SINISTROS CONHECIDOS OU AVISADOS  DE ASSISTÊNCIA A SAÚDE MEDICO HOSPITALAR '
        AND dc.DATA >= (SELECT MAX(DATA) FROM demonstracoes_contabeis) - INTERVAL '1 year'
)
SELECT 
    Registro_ANS,
    Razao_Social,
    Nome_Fantasia,
    SUM(saldo_final - saldo_inicial) AS despesa_total
FROM 
    dados_convertidos
GROUP BY 
    Registro_ANS, Razao_Social, Nome_Fantasia
ORDER BY 
    despesa_total DESC
LIMIT 10;