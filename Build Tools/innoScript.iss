; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "The Github Button"
#define MyAppVersion "1.0"
#define MyAppPublisher "Bean Industries"
#define MyAppURL "https://alfiedev.co.uk"
#define MyAppExeName "TheGithubButton.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{6E37D267-CE5B-4DE9-891D-F690DCD09F62}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={userappdata}\{#MyAppName}
DisableProgramGroupPage=yes
; Uncomment the following line to run in non administrative install mode (install for current user only.)
PrivilegesRequired=lowest
OutputBaseFilename=GithubButtonInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\asdaFemboy\Downloads\Git-2.41.0.2-64-bit.exe"; DestDir: "{app}"; AfterInstall: RunOtherInstaller
Source: "C:\Users\asdaFemboy\Desktop\Github Repos\AutoComitter\dist\{#MyAppExeName}"; DestDir: "{userappdata}\{#MyAppName}"; Flags: ignoreversion
Source: "C:\Users\asdaFemboy\Desktop\Github Repos\AutoComitter\icon.png"; DestDir: "{userappdata}\{#MyAppName}"; Flags: ignoreversion
Source: "C:\Users\asdaFemboy\Desktop\Github Repos\AutoComitter\icon.ico"; DestDir: "{userappdata}\{#MyAppName}"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{userappdata}\{#MyAppName}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{userappdata}\{#MyAppName}\{#MyAppExeName}"; IconFilename: "{userappdata}\{#MyAppName}\icon.ico"
Name: "{userstartup}\{#MyAppName}"; Filename: "{userappdata}\{#MyAppName}\{#MyAppExeName}"; IconFilename: "{userappdata}\{#MyAppName}\icon.ico"

[Run]
Filename: "{userappdata}\{#MyAppName}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
procedure RunOtherInstaller;
var
  ResultCode: Integer;
begin
  if not Exec(ExpandConstant('{app}\Git-2.41.0.2-64-bit.exe'), '', '', SW_SHOWNORMAL,
    ewWaitUntilTerminated, ResultCode)
  then
    MsgBox('Other installer failed to run!' + #13#10 +
      SysErrorMessage(ResultCode), mbError, MB_OK);
end;

[InstallDelete]
Type: files; Name: "{userappdata}\{#MyAppName}\TheGithubButton.exe"
Type: files; Name: "{userappdata}\{#MyAppName}\versions.txt"