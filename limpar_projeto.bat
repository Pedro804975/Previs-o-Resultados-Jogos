@echo off
setlocal enabledelayedexpansion

REM ==================================================================
REM  limpar_projeto.bat
REM  Reduz a pasta ao minimo: o codigo + as duas planilhas que ele usa.
REM  NAO APAGA NADA - move o resto para _PARA_APAGAR.
REM ==================================================================

cd /d "%~dp0"

echo.
echo ==================================================================
echo    LIMPEZA DO PROJETO
echo ==================================================================
echo.
echo    Pasta: %CD%
echo.
echo    FICAM (3 arquivos, cerca de 91 KB):
echo.
echo      02_notebook\prever_jogos_v3.ipynb    o codigo
echo      01_dados\base_jogos_limpa.xlsx       os 906 jogos
echo      01_dados\ranking_elo_externo.xlsx    forca inicial de 48 selecoes
echo.
echo    VAO PARA _PARA_APAGAR:
echo.
echo      Arquivos Importantes         planilhas originais
echo      Prever Jogos Colab           notebooks v1 e v2
echo      02_notebooks                 copia antiga do notebook
echo      01_dados\processados         copia antiga da base
echo      03_docs                      documentacao
echo      04_modelos                   o notebook regera o modelo
echo      00_leia_me.md e 00_LEIA-ME.md   documentacao
echo      Ranking Elo Selecoes.xlsx    copia solta do ranking
echo      01_dados\base_jogos_limpa.csv    igual ao .xlsx
echo      01_dados\relatorio_qualidade.json  documentacao
echo.
echo    ATENCAO: ranking_elo_externo.xlsx NAO e opcional. Sem ele o
echo    notebook ainda roda, mas perde precisao sem avisar direito.
echo.
echo ==================================================================
echo.

set "RESPOSTA="
set /p RESPOSTA="Digite  SIM  para continuar (ou Enter para cancelar): "
if /i not "%RESPOSTA%"=="SIM" goto :cancelado

echo.

REM --- trava: nao mexe em nada se faltar algum essencial ---
set FALTA=0
if not exist "01_dados\base_jogos_limpa.xlsx"    set FALTA=1
if not exist "01_dados\ranking_elo_externo.xlsx" set FALTA=1
if not exist "02_notebook\prever_jogos_v3.ipynb" set FALTA=1
if "%FALTA%"=="1" goto :faltando

if not exist "_PARA_APAGAR" mkdir "_PARA_APAGAR"

set MOVIDOS=0

call :mover "Arquivos Importantes"
call :mover "Prever Jogos Colab"
call :mover "02_notebooks"
call :mover "01_dados\processados"
call :mover "03_docs"
call :mover "04_modelos"
call :mover "00_leia_me.md"
call :mover "00_LEIA-ME.md"
call :mover "01_dados\base_jogos_limpa.csv"
call :mover "01_dados\relatorio_qualidade.json"

REM o nome tem acento, entao usa curinga para nao depender de codificacao
for %%F in ("Ranking Elo*.xlsx") do call :mover "%%~F"

echo.
echo ==================================================================
echo    PRONTO. !MOVIDOS! item(ns) movido(s) para _PARA_APAGAR
echo ==================================================================
echo.
echo    Sobrou:
echo.
echo      01_dados\base_jogos_limpa.xlsx
echo      01_dados\ranking_elo_externo.xlsx
echo      02_notebook\prever_jogos_v3.ipynb
echo      limpar_projeto.bat        (pode apagar depois de usar)
echo      _PARA_APAGAR              confira e apague quando quiser
echo.
echo    COMO USAR DAQUI PRA FRENTE:
echo      1. abrir prever_jogos_v3.ipynb no Google Colab
echo      2. no Passo 2, enviar as DUAS planilhas de 01_dados
echo      3. rodar as celulas de cima para baixo
echo.
pause
exit /b 0

REM ==================================================================
:cancelado
echo.
echo    Cancelado. Nada foi alterado.
echo.
pause
exit /b 0

:faltando
echo    ERRO: um dos 3 arquivos essenciais nao esta no lugar.
echo    A limpeza foi cancelada para nao remover a unica copia de nada.
echo.
echo    Esperado:
echo      01_dados\base_jogos_limpa.xlsx
echo      01_dados\ranking_elo_externo.xlsx
echo      02_notebook\prever_jogos_v3.ipynb
echo.
pause
exit /b 1

:mover
REM aceita tanto pasta quanto arquivo
if exist "%~1\" goto :mover_faz
if exist "%~1"  goto :mover_faz
exit /b 0
:mover_faz
move /y "%~1" "_PARA_APAGAR\" >nul 2>&1
if errorlevel 1 (
  echo    [!] nao consegui mover: %~1
) else (
  echo    [ok] movido: %~1
  set /a MOVIDOS+=1
)
exit /b 0
