$desktop = [Environment]::GetFolderPath("Desktop")
$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut("$desktop\Secure OTA Demo.lnk")
$shortcut.TargetPath = "$repoRoot\launch_web_demo.bat"
$shortcut.WorkingDirectory = $repoRoot
$shortcut.IconLocation = "shell32.dll,14"
$shortcut.Save()
Write-Host "Created Desktop shortcut successfully pointing to: $repoRoot\launch_web_demo.bat"
