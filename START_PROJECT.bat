
@echo off
title Movie Recommendation Project Launcher
setlocal

set "ROOT=%~dp0"
set "KAFKA=C:\kafka"

echo ==========================================
echo   MOVIE RECOMMENDATION PROJECT
echo ==========================================

echo.
echo [1/4] Starting Kafka Server...
start "Kafka Server" cmd /k "cd /d ""%KAFKA%"" && set KAFKA_HEAP_OPTS=-Xms1G -Xmx1G && bin\windows\kafka-server-start.bat config\server.properties"

echo Waiting for Kafka to start...
timeout /t 15 /nobreak >nul

echo.
echo [2/4] Starting Spark Streaming...
if exist "%ROOT%.venv\Scripts\spark-submit.cmd" (
    start "Spark Streaming" cmd /k "cd /d ""%ROOT%"" && call .venv\Scripts\activate.bat && .venv\Scripts\spark-submit.cmd --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6 spark_stream.py"
) else (
    start "Spark Streaming" cmd /k "cd /d ""%ROOT%"" && call .venv\Scripts\activate.bat && spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.6 spark_stream.py"
)

echo Waiting for Spark Streaming...
timeout /t 25 /nobreak >nul

echo.
echo [3/4] Starting Kafka Producer...
start "Kafka Producer" cmd /k "cd /d ""%ROOT%"" && call .venv\Scripts\activate.bat && python producer.py"

echo.
echo [4/4] Starting Streamlit Dashboard...
timeout /t 3 /nobreak >nul
start "Movie Dashboard" cmd /k "cd /d ""%ROOT%"" && call .venv\Scripts\activate.bat && streamlit run app.py"

echo.
echo ==========================================
echo   PROJECT STARTUP COMMANDS SENT!
echo   Check all four terminal windows.
echo ==========================================
pause
