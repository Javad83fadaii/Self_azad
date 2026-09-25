#ifndef MyAppName
  #define MyAppName "UFRS Student Desktop"
#endif
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#ifndef MyAppPublisher
  #define MyAppPublisher "Self Food Project"
#endif
#ifndef MyAppExeName
  #define MyAppExeName "UFRSStudentDesktop.exe"
#endif
#ifndef MyAppSourceDir
  #define MyAppSourceDir "..\dist\UFRSStudentDesktop"
#endif

[Setup]
AppId={{7E266E6A-A1FE-49C4-B2B8-7D0A978D9E0B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=ufrs-student-desktop-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=..\desktop\resources\app_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#MyAppSourceDir}\config\desktop.env.example"; DestDir: "{userappdata}\ufrs_student_desktop"; DestName: "desktop.env.example"; Flags: onlyifdoesntexist skipifsourcedoesntexist
Source: "{#MyAppSourceDir}\README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Dirs]
Name: "{userappdata}\ufrs_student_desktop"

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
