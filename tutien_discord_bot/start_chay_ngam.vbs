' ============================================================
' Tu Tien Discord Bot - Khoi Dong Chay Ngam (An Cua So Console)
' ============================================================
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strPath = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strPath

' Uu tien pythonw trong moi truong ao neu co
pythonExe = "pythonw"
If fso.FileExists(strPath & "\venv\Scripts\pythonw.exe") Then
    pythonExe = strPath & "\venv\Scripts\pythonw.exe"
ElseIf fso.FileExists(strPath & "\.venv\Scripts\pythonw.exe") Then
    pythonExe = strPath & "\.venv\Scripts\pythonw.exe"
End If

' Dung Start-Process de tao tien trinh doc lap hoan toan, an cua so
psCmd = "powershell.exe -NoProfile -WindowStyle Hidden -Command ""Start-Process '" & pythonExe & "' -ArgumentList 'main.py' -WorkingDirectory '" & strPath & "' -WindowStyle Hidden"""
WshShell.Run psCmd, 0, False

Set WshShell = Nothing
Set fso = Nothing
