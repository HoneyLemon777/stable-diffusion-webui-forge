$TargetFile = "E:\private\AntiGravity products\StableDiffusion_Project\webui-user.bat"
$ShortcutFile = "E:\private\AntiGravity products\StableDiffusion_Project\Stable Diffusion.lnk"
$IconFile = "E:\private\AntiGravity products\StableDiffusion_Project\sd_icon.ico"
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($ShortcutFile)
$Shortcut.TargetPath = $TargetFile
$Shortcut.WorkingDirectory = "E:\private\AntiGravity products\StableDiffusion_Project"
$Shortcut.IconLocation = "$IconFile, 0"
$Shortcut.Save()
Write-Output "Shortcut created at $ShortcutFile with icon $IconFile"
