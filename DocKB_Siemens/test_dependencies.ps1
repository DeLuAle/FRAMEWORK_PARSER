# Script di Verifica Dipendenze DocKB_Siemens
# Verifica che tutti i tool necessari siano installati

Write-Host "`n[Check] Verifica Dipendenze DocKB_Siemens" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan

$tools = @(
    @{Name='Python'; Command='python'; Args='--version'},
    @{Name='pdftotext (Poppler)'; Command='pdftotext'; Args='-v'},
    @{Name='Pandoc'; Command='pandoc'; Args='--version'}
)

$allOk = $true

foreach ($tool in $tools) {
    $toolName = $tool.Name
    $cmd = $tool.Command
    $args = $tool.Args
    
    Write-Host -NoNewline "`nVerifica $toolName... " -ForegroundColor White
    
    # Verifica esistenza comando
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        try {
            # Esegui comando per vedere versione
            $result = & $cmd $args 2>&1 | Select-Object -First 1
            Write-Host "[OK]" -ForegroundColor Green
            if ($result) {
                $verString = $result.ToString().Trim()
                Write-Host "  -> $verString" -ForegroundColor DarkGray
            }
        } catch {
            Write-Host "[TROVATO] (errore esecuzione)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[MANCANTE]" -ForegroundColor Red
        $allOk = $false
        
        # Suggerimento installazione
        if ($toolName -like "*Poppler*") {
            Write-Host "  -> Installa: choco install poppler -y" -ForegroundColor Yellow
        } elseif ($toolName -eq "Pandoc") {
            Write-Host "  -> Installa: choco install pandoc -y" -ForegroundColor Yellow
        } elseif ($toolName -eq "Python") {
            Write-Host "  -> Installa: choco install python -y" -ForegroundColor Yellow
        }
    }
}

Write-Host "`n"
Write-Host ("=" * 50) -ForegroundColor Cyan

if ($allOk) {
    Write-Host "[SUCCESS] TUTTE LE DIPENDENZE SONO INSTALLATE!" -ForegroundColor Green
    Write-Host "`nPuoi procedere con l'estrazione dei PDF." -ForegroundColor White
    exit 0
} else {
    Write-Host "[ERROR] ALCUNE DIPENDENZE MANCANO" -ForegroundColor Red
    Write-Host "`nInstalla le dipendenze mancanti con Chocolatey:" -ForegroundColor Yellow
    Write-Host "  choco install poppler pandoc python -y" -ForegroundColor White
    Write-Host "`nPoi riavvia PowerShell e riesegui questo script." -ForegroundColor White
    exit 1
}
