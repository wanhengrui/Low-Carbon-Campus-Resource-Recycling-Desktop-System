# -*- coding: utf-8 -*-
"""生成 GBK 编码的 start.bat（cmd 对 UTF-8 批处理解析不可靠，中文必须写成 ANSI/GBK）。"""
import io, os

TARGET = r"C:\Users\wanhe\Desktop\软件构造\迭代一-成员1\code\green-campus\start.bat"

BAT = r"""@echo off
chcp 936 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "JAR=target\green-campus-1.0.0.jar"
set "MAIN=edu.campus.recycle.Main"

echo ============================================================
echo  绿色校园闲置物品循环流转平台 - 启动脚本（迭代一 D7 骨架）
echo ============================================================
echo.

if exist "%JAR%" (
    echo [启动] 检测到已构建的可执行 Jar：%JAR%
    java -jar "%JAR%"
    goto :end
)

where mvn >nul 2>nul
if not errorlevel 1 (
    echo [1/2] 正在用 Maven 构建（首次构建需联网下载依赖）...
    call mvn -q -DskipTests package
    if errorlevel 1 goto :mvn_fail
    if exist "%JAR%" (
        echo [2/2] 构建成功，启动程序...
        java -jar "%JAR%"
        goto :end
    )
    goto :mvn_fail
)

echo [提示] 未检测到 Maven 与已构建 Jar，尝试用 javac 直接编译运行（详见 部署说明.md 第 3 节）。
set "LIBJAR="
if exist "lib\sqlite-jdbc-*.jar" for %%f in ("lib\sqlite-jdbc-*.jar") do set "LIBJAR=%%~ff"
if not defined LIBJAR if exist "%USERPROFILE%\.m2\repository\org\xerial\sqlite-jdbc\" for /r "%USERPROFILE%\.m2\repository\org\xerial\sqlite-jdbc" %%f in (sqlite-jdbc-*.jar) do set "LIBJAR=%%~ff"
if not defined LIBJAR (
    echo [错误] 未找到 sqlite-jdbc 依赖 jar，无法离线编译运行。
    echo        请安装 Maven，或把 sqlite-jdbc-*.jar 放入本目录 lib\ 后重试。
    goto :fail
)

if not exist "build\classes" mkdir "build\classes"
echo [1/2] 正在编译 src\main\java ...
javac --release 17 -encoding UTF-8 -sourcepath src\main\java -d build\classes -cp "!LIBJAR!" src\main\java\edu\campus\recycle\Main.java
if errorlevel 1 goto :compile_fail
echo [2/2] 编译完成，启动程序...
java -cp "build\classes;src\main\resources;!LIBJAR!" %MAIN%
goto :end

:mvn_fail
echo [错误] Maven 构建失败，请检查网络或本地仓库，详见 部署说明.md。
goto :fail

:compile_fail
echo [错误] 编译失败，请确认已安装 JDK 17 及以上版本（javac -version）。
goto :fail

:fail
echo.
echo 启动中止。请阅读同目录 部署说明.md 的“常见问题”一节。
endlocal
exit /b 1

:end
endlocal
exit /b 0
"""

data = BAT.replace("\r\n", "\n").replace("\n", "\r\n")
with open(TARGET, "wb") as f:
    f.write(data.encode("gbk"))
print("written:", TARGET, os.path.getsize(TARGET), "bytes (GBK)")
