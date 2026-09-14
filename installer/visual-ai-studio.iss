#define MyAppName "Visual AI Studio"
#define MyAppVersion "0.2.1"
#define MyAppExeName "Visual AI Studio.exe"

[Setup]
AppId=EtorrentOrg.VisualAIStudio
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Etorrent-Org
DefaultDirName={localappdata}\Programs\Visual AI Studio
DefaultGroupName=Visual AI Studio
PrivilegesRequired=lowest
OutputDir=output
OutputBaseFilename=Visual-AI-Studio-Setup-0.2.1
SetupIconFile=..\src\visual_ai_studio\resources\visual-ai-studio.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
CloseApplications=yes
RestartApplications=no

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis supplémentaires :"; Flags: unchecked

[InstallDelete]
Type: files; Name: "{userdesktop}\IA-Art Studio.lnk"
Type: files; Name: "{userprograms}\IA-Art Studio\IA-Art Studio.lnk"

[Files]
Source: "..\dist\Visual AI Studio\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Visual AI Studio"; Filename: "{app}\{#MyAppExeName}"
Name: "{userdesktop}\Visual AI Studio"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Lancer Visual AI Studio"; Flags: nowait postinstall skipifsilent
