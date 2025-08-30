@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ===== Config =====
set "APPDIR=%~dp0"
set "VENV=%APPDIR%venv"
set "PY=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"
set "REQ=%APPDIR%requirements.txt"
set "HASHFILE=%APPDIR%.req_hash"
:: ==================

title SISTEMA DE LICENCAS LSG - INICIALIZACAO
chcp 65001 >nul

echo ==========================================
echo   SISTEMA DE LICENCAS LSG - INICIALIZACAO
echo ==========================================
echo.

:: 1) Criar venv se preciso
if not exist "%PY%" (
  echo [INFO] Criando ambiente virtual...
  py -3 -m venv "%VENV%"
  if errorlevel 1 (
    echo [ERRO] Falha ao criar o ambiente virtual.
    pause
    exit /b 1
  )
)

echo [INFO] Ativando ambiente virtual...
call "%VENV%\Scripts\activate.bat"

:: 2) Calcular hash atual do requirements.txt (se existir)
set "CURHASH="
if exist "%REQ%" (
  for /f "usebackq skip=1 tokens=1" %%H in (`certutil -hashfile "%REQ%" SHA256 ^| find /i /v "hash" ^| find /i /v "certutil"`) do (
    set "CURHASH=%%H"
    goto :gotHash
  )
)
:gotHash

:: 3) Ler hash antigo salvo
set "OLDHASH="
if exist "%HASHFILE%" (
  set /p OLDHASH=<"%HASHFILE%"
)

:: 4) Testar pacotes essenciais (Flask/Pandas/Openpyxl)
set "NEED_INSTALL=0"
"%PY%" -c "import importlib.util,sys;mods=['flask','pandas','openpyxl'];sys.exit(1 if any(importlib.util.find_spec(m) is None for m in mods) else 0)"
if errorlevel 1 (
  set "NEED_INSTALL=1"
)

:: 5) Se venv novo, requirements mudou ou falta pacote -> instalar
if "%NEED_INSTALL%"=="0" (
  if not "%CURHASH%"=="%OLDHASH%" (
    set "NEED_INSTALL=1"
  )
)

if "%NEED_INSTALL%"=="1" (
  echo [INFO] Instalando dependencias...
  "%PY%" -m pip install --upgrade pip
  if exist "%REQ%" (
    "%PIP%" install -r "%REQ%"
  ) else (
    echo [AVISO] requirements.txt nao encontrado; pulando instalacao de lista.
  )
  if defined CURHASH (
    >"%HASHFILE%" echo %CURHASH%
  )
) else (
  echo [OK] Dependencias ja atendidas. Sem reinstalar.
)

echo.
echo [INFO] Iniciando o sistema Flask...
"%PY%" app.py
echo.
pause
exit /b 0
