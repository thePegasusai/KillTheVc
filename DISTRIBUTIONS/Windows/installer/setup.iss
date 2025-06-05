#define MyAppName "Kill the VC"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ThePegasusAI"
#define MyAppURL "https://thepegasusai.com"
#define MyAppExeName "KillTheVC.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{8F6E2B5A-4C3D-4B1F-9E5A-1D2C3B4A5D6E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=EULA.txt
OutputDir=..\
OutputBaseFilename=KillTheVC-Windows-Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=python\assets\Assets\icon-removebg-preview.png
UninstallDisplayIcon={app}\python\assets\Assets\icon-removebg-preview.png
WizardStyle=modern
WizardImageFile=installer_background.bmp
WizardSmallImageFile=installer_logo.bmp

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "EULA.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "TERMS_OF_USE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "PRIVACY_POLICY.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALLATION_AGREEMENT.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "LICENSE_VERIFICATION.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "DIGITAL_RECEIPT.txt"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\KillTheVC.bat"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\KillTheVC.bat"; Tasks: desktopicon

[Run]
Filename: "{app}\KillTheVC.bat"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  LicensePage: TOutputMsgMemoWizardPage;
  ActivationPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  // Create license page
  LicensePage := CreateOutputMsgMemoPage(wpLicense,
    'License Agreement', 'Please review the license terms before installing Kill the VC',
    'Press Page Down to see the rest of the agreement. Once you have read and agree to the terms, click Next to continue.',
    '');
  
  // Load EULA text
  LoadStringFromFile(ExpandConstant('{src}\EULA.txt'), LicensePage.RichEditViewer.Lines.Text);
  
  // Create activation page
  ActivationPage := CreateInputQueryPage(wpWelcome,
    'License Activation', 'Please enter your license information',
    'If you have a license key, please enter it below. Otherwise, you can skip this step and activate later.');
  
  ActivationPage.Add('Full Name:', False);
  ActivationPage.Add('Email Address:', False);
  ActivationPage.Add('License Key:', False);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  FileName: String;
  LicenseData: TStringList;
begin
  Result := True;
  
  // Save activation data if provided
  if CurPageID = ActivationPage.ID then
  begin
    if (ActivationPage.Values[0] <> '') and (ActivationPage.Values[1] <> '') and (ActivationPage.Values[2] <> '') then
    begin
      FileName := ExpandConstant('{app}\license_data.txt');
      LicenseData := TStringList.Create;
      try
        LicenseData.Add('Name: ' + ActivationPage.Values[0]);
        LicenseData.Add('Email: ' + ActivationPage.Values[1]);
        LicenseData.Add('License: ' + ActivationPage.Values[2]);
        LicenseData.SaveToFile(FileName);
      finally
        LicenseData.Free;
      end;
    end;
  end;
end;
