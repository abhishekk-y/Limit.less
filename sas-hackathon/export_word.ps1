$ErrorActionPreference='Stop'
$word=$null;$doc=$null
try {
 Add-Content -Path 'sas-hackathon/word_export.log' -Value 'begin'
 $word=New-Object -ComObject Word.Application
 Add-Content -Path 'sas-hackathon/word_export.log' -Value 'created'
 $word.Visible=$false;$word.DisplayAlerts=0;$word.AutomationSecurity=3
 $docx=[IO.Path]::GetFullPath('sas-hackathon/Pookie_Blinders_Team_117_Round_2_Report.docx')
 $pdf=[IO.Path]::GetFullPath('sas-hackathon/Pookie_Blinders_Team_117_Round_2_Report.pdf')
 Add-Content -Path 'sas-hackathon/word_export.log' -Value 'opening'
 $doc=$word.Documents.Open($docx, $false, $true, $false)
 Add-Content -Path 'sas-hackathon/word_export.log' -Value 'opened'
 $doc.ExportAsFixedFormat($pdf,17)
 Add-Content -Path 'sas-hackathon/word_export.log' -Value 'exported'
 $doc.Close(0)
 $word.Quit()
 Add-Content -Path 'sas-hackathon/word_export.log' -Value 'done'
} catch { Add-Content -Path 'sas-hackathon/word_export.log' -Value $_.Exception.ToString(); if($doc){$doc.Close(0)};if($word){$word.Quit()} }
