@echo off
TITLE Nexus HubSync - FastAPI Server
color 0A
echo [INFO] Ativando o ambiente virtual (venv)...
call venv\Scripts\activate.bat

echo [INFO] Iniciando o servidor Uvicorn (FastAPI)...
start /b uvicorn main:app --reload

echo [INFO] Aguardando o servidor subir...
timeout /t 3 >nul

echo [INFO] Abrindo a documentacao Swagger no navegador...
start http://127.0.0.1:8000/docs

echo.
echo [SUCESSO] Sistema rodando! Pressione Ctrl+C para encerrar o servidor.
pause >nul