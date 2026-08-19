$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$OutputEncoding = [Console]::OutputEncoding

$Root = "C:\h9-workspace\visual-ai-studio"
$ImagesDir = "$Root\docs\images"

Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;

public static class VisualAIStudioCapture
{
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(
        IntPtr hWnd,
        out RECT lpRect
    );

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(
        IntPtr hWnd
    );
}
"@

function Get-VisualAIStudioProcess {

    $Process = Get-Process |
        Where-Object {
            $_.MainWindowHandle -ne 0 -and
            $_.MainWindowTitle -like "*Visual AI Studio*"
        } |
        Select-Object -First 1

    return $Process
}

function Start-VisualAIStudio {

    $InstalledExe = Join-Path `
        $env:LOCALAPPDATA `
        "Programs\Visual AI Studio\Visual AI Studio.exe"

    $BuildExe = "$Root\dist\Visual AI Studio\Visual AI Studio.exe"

    $Exe = $null

    if (Test-Path $InstalledExe) {
        $Exe = $InstalledExe
    }

    if (-not $Exe) {
        if (Test-Path $BuildExe) {
            $Exe = $BuildExe
        }
    }

    if (-not $Exe) {
        Write-Host "ERREUR : Visual AI Studio.exe introuvable." -ForegroundColor Red
        return $null
    }

    Start-Process $Exe | Out-Null

    Start-Sleep -Seconds 3

    return Get-VisualAIStudioProcess
}

function Save-VisualAIStudioScreenshot {

    param(
        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    $Process = Get-VisualAIStudioProcess

    if (-not $Process) {
        $Process = Start-VisualAIStudio
    }

    if (-not $Process) {
        Write-Host "ERREUR : fenêtre Visual AI Studio introuvable." -ForegroundColor Red
        return
    }

    $Handle = $Process.MainWindowHandle

    [VisualAIStudioCapture]::SetForegroundWindow(
        $Handle
    ) | Out-Null

    Start-Sleep -Milliseconds 800

    $Rect = New-Object VisualAIStudioCapture+RECT

    $Result = [VisualAIStudioCapture]::GetWindowRect(
        $Handle,
        [ref]$Rect
    )

    if (-not $Result) {
        Write-Host "ERREUR : dimensions de la fenêtre introuvables." -ForegroundColor Red
        return
    }

    $Width = $Rect.Right - $Rect.Left
    $Height = $Rect.Bottom - $Rect.Top

    if ($Width -le 0) {
        Write-Host "ERREUR : largeur de fenêtre invalide." -ForegroundColor Red
        return
    }

    if ($Height -le 0) {
        Write-Host "ERREUR : hauteur de fenêtre invalide." -ForegroundColor Red
        return
    }

    $Bitmap = New-Object `
        System.Drawing.Bitmap `
        $Width,
        $Height

    $Graphics = [System.Drawing.Graphics]::FromImage(
        $Bitmap
    )

    $Graphics.CopyFromScreen(
        $Rect.Left,
        $Rect.Top,
        0,
        0,
        $Bitmap.Size
    )

    $Output = Join-Path `
        $ImagesDir `
        $FileName

    $Bitmap.Save(
        $Output,
        [System.Drawing.Imaging.ImageFormat]::Png
    )

    $Graphics.Dispose()
    $Bitmap.Dispose()

    Write-Host "Capture créée : $Output" -ForegroundColor Green
}

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host " CAPTURES README - VISUAL AI STUDIO"
Write-Host "==================================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Pour chaque capture :" -ForegroundColor Yellow
Write-Host "1. affiche l'écran demandé dans Visual AI Studio"
Write-Host "2. reviens dans PowerShell"
Write-Host "3. appuie sur Entrée"
Write-Host ""

Read-Host "1/5 - Affiche PROJETS puis Entrée"
Save-VisualAIStudioScreenshot "projets.png"

Read-Host "2/5 - Affiche BRIEF CRÉATIF puis Entrée"
Save-VisualAIStudioScreenshot "brief.png"

Read-Host "3/5 - Affiche PRÉPARATION STUDIO VISUEL puis Entrée"
Save-VisualAIStudioScreenshot "studio-visuel.png"

Read-Host "4/5 - Affiche VALIDATION DU RÉSULTAT puis Entrée"
Save-VisualAIStudioScreenshot "validation.png"

Read-Host "5/5 - Affiche PARAMÈTRES puis Entrée"
Save-VisualAIStudioScreenshot "parametres.png"

Write-Host "`n=== CAPTURES CREEES ===" -ForegroundColor Cyan

Get-ChildItem `
    $ImagesDir `
    -Filter "*.png" |
    Select-Object Name, Length |
    Format-Table -AutoSize

Write-Host "`nCAPTURES TERMINEES." -ForegroundColor Green