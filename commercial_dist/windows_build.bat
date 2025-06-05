@echo off
echo Building Kill the VC for Windows...

REM Create a virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install required packages
pip install pygame numpy opencv-python mediapipe pyinstaller

REM Build with PyInstaller
pyinstaller --onefile --windowed --name KillTheVC ^
    --add-data "assets/Assets;assets/Assets" ^
    --add-data "assets/sounds;assets/sounds" ^
    --icon "assets/Assets/icon-removebg-preview.png" ^
    game.py

REM Create Inno Setup script
echo Creating Inno Setup script...
(
echo #define MyAppName "Kill the VC"
echo #define MyAppVersion "1.0"
echo #define MyAppPublisher "Your Company Name"
echo #define MyAppURL "https://www.yourwebsite.com"
echo #define MyAppExeName "KillTheVC.exe"
echo.
echo [Setup]
echo AppId={{GUID-FOR-YOUR-APP}}
echo AppName={#MyAppName}
echo AppVersion={#MyAppVersion}
echo AppPublisher={#MyAppPublisher}
echo AppPublisherURL={#MyAppURL}
echo AppSupportURL={#MyAppURL}
echo AppUpdatesURL={#MyAppURL}
echo DefaultDirName={autopf}\{#MyAppName}
echo DisableProgramGroupPage=yes
echo LicenseFile=LICENSE.txt
echo OutputDir=installer
echo OutputBaseFilename=KillTheVC_Setup
echo Compression=lzma
echo SolidCompression=yes
echo WizardStyle=modern
echo.
echo [Languages]
echo Name: "english"; MessagesFile: "compiler:Default.isl"
echo.
echo [Tasks]
echo Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
echo.
echo [Files]
echo Source: "dist\KillTheVC.exe"; DestDir: "{app}"; Flags: ignoreversion
echo Source: "README.txt"; DestDir: "{app}"; Flags: isreadme
echo.
echo [Icons]
echo Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
echo Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
echo.
echo [Run]
echo Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
) > setup.iss

echo Windows build script created. Run this on a Windows machine.
echo After building, use Inno Setup to create the installer with setup.iss
