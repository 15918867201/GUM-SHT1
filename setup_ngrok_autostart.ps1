$Action = New-ScheduledTaskAction -Execute "C:\Users\libo2\Downloads\停机监控 - 副本\GUM-SHT1\start_ngrok.bat"
$Trigger = New-ScheduledTaskTrigger -AtLogon
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "StartNgrok" -Action $Action -Trigger $Trigger -Settings $Settings -RunLevel Highest -Force
Write-Host "Scheduled task created successfully! ngrok will start automatically on login."
