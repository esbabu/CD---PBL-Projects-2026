from pathlib import Path
import subprocess

repo_root = Path(__file__).resolve().parent.parent
ps_script = f"""
$desktop = [Environment]::GetFolderPath("Desktop")
$ws = New-Object -ComObject WScript.Shell
$shortcut = $ws.CreateShortcut("$desktop\\Secure OTA Demo.lnk")
$shortcut.TargetPath = "{repo_root}\\launch_web_demo.bat"
$shortcut.WorkingDirectory = "{repo_root}"
$shortcut.IconLocation = "shell32.dll,14"
$shortcut.Save()
"""

subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True)
print(f"Shortcut created successfully pointing to {repo_root}\\launch_web_demo.bat")
