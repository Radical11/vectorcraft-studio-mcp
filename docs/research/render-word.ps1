param([Parameter(Mandatory=$true)][string]$InputDocx,[Parameter(Mandatory=$true)][string]$OutputPdf)
$ErrorActionPreference='Stop'
$taskDocx=(Resolve-Path -LiteralPath $InputDocx).Path
$taskPdf=[IO.Path]::GetFullPath($OutputPdf)
$taskWord=$null
$taskDocument=$null
try {
    $taskWord=New-Object -ComObject Word.Application
    $taskWord.Visible=$false
    $taskWord.DisplayAlerts=0
    $taskDocument=$taskWord.Documents.Open($taskDocx,$false,$true,$false)
    $taskDocument.ExportAsFixedFormat($taskPdf,17,$false)
    [pscustomobject]@{input=$taskDocx;pdf=$taskPdf;renderer='Microsoft Word native PDF export';readOnly=$true} | ConvertTo-Json
} finally {
    if ($null -ne $taskDocument) {$taskDocument.Close(0);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDocument) | Out-Null}
    if ($null -ne $taskWord) {$taskWord.Quit(0);[Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord) | Out-Null}
}
