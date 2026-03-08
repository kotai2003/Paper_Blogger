; ============================================================
; Paper Blogger - Inno Setup Installer Script
; ============================================================
; Requires: Inno Setup 6.x (https://jrsoftware.org/isinfo.php)
; Build:    ISCC.exe paper_blogger_installer.iss
; ============================================================

#define MyAppName      "Paper Blogger"
#define MyAppVersion   "1.0.0"
#define MyAppPublisher "Tomomi Research"
#define MyAppExeName   "paper_blogger.exe"
#define MyAppIcon      "..\assets\favicon.ico"

; PyInstaller build output location
#define BuildDist      GetEnv("LOCALAPPDATA") + "\paper_blogger_build\dist\paper_blogger"

[Setup]
AppId={{A7E3F8B2-4D1C-4A5E-9B7F-2C8D6E0F1A3B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL=https://tomomi-research.com
AppSupportURL=https://tomomi-research.com
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=..\pyinstaller\README.md
OutputDir=output
OutputBaseFilename=setup_paper_blogger
SetupIconFile={#MyAppIcon}
UninstallDisplayIcon={app}\assets\favicon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
DisableProgramGroupPage=yes
AllowNoIcons=yes
MinVersion=10.0

; --- Wizard branding images (optional) ---
; Uncomment and provide 164x314 BMP for left panel:
; WizardImageFile=wizard_image.bmp
; Uncomment and provide 55x55 BMP for top-right corner:
; WizardSmallImageFile=wizard_small_image.bmp

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "{#BuildDist}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\favicon.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop (optional task)
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\assets\favicon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
