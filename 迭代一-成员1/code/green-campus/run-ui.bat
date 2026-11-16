@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo  绿色校园 - 迭代一成员3 Swing 骨架
echo ============================================================
echo.

set "LIBJAR="
if exist "lib\sqlite-jdbc-*.jar" for %%f in ("lib\sqlite-jdbc-*.jar") do set "LIBJAR=%%~ff"
if not defined LIBJAR if exist "%USERPROFILE%\.m2\repository\org\xerial\sqlite-jdbc\" for /r "%USERPROFILE%\.m2\repository\org\xerial\sqlite-jdbc" %%f in (sqlite-jdbc-*.jar) do set "LIBJAR=%%~ff"
if not defined LIBJAR (
    echo [ERROR] sqlite-jdbc jar not found. Put it under lib\ or install Maven.
    pause
    exit /b 1
)

if not exist "build\classes" mkdir "build\classes"
echo [1/2] Compiling UI skeleton and dependencies...
javac --release 17 -encoding UTF-8 -sourcepath src\main\java -d build\classes -cp "!LIBJAR!" src\main\java\edu\campus\recycle\ui\MainApp.java
if errorlevel 1 (
    echo [WARN] JDK 17 release mode unavailable; retrying with current JDK...
    javac -encoding UTF-8 -sourcepath src\main\java -d build\classes -cp "!LIBJAR!" src\main\java\edu\campus\recycle\ui\MainApp.java
)
if errorlevel 1 (
    echo [ERROR] Compile failed.
    pause
    exit /b 1
)

echo [2/2] Starting Swing UI...
java -Dfile.encoding=UTF-8 -cp "build\classes;src\main\resources;!LIBJAR!" edu.campus.recycle.ui.MainApp %*
endlocal
