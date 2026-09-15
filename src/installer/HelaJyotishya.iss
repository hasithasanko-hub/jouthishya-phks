#define MyAppName "Hela Jyotishya"
#define MyAppVersion "4.0"
#define MyAppPublisher "PHKS Creation"
#define MyAppExeName "HelaJyotishya.exe"

[Setup]
AppSupportURL=https://wa.me/94715954563
AppId={{E7D8D71D-A1F4-4AE9-9D06-5CB071271A25}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Hela Jyotishya
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\release
OutputBaseFilename=Hela_Jyotishya_Setup_v40_PHKS_Trial_Paid
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
SetupIconFile=HelaJyotishya.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\HelaJyotishya.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autoprograms}\{#MyAppName} - License"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--license-manager"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch Hela Jyotishya"; Flags: nowait postinstall skipifsilent
