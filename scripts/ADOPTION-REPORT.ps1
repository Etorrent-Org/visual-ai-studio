param(
    [string]$Repo = "Etorrent-Org/visual-ai-studio"
)

$ErrorActionPreference = "Stop"

$Parts = $Repo.Split("/")

if ($Parts.Count -ne 2) {
    Write-Host "ERREUR : depot attendu au format owner/repo." -ForegroundColor Red
    return
}

$Owner = $Parts[0]
$Name = $Parts[1]
$OutputDir = Join-Path $env:LOCALAPPDATA "VisualAIStudio\adoption"
$HistoryFile = Join-Path $OutputDir "adoption-history.csv"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERREUR : GitHub CLI absent." -ForegroundColor Red
    return
}

gh auth status *> $null

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERREUR : GitHub CLI non authentifie." -ForegroundColor Red
    return
}

New-Item -ItemType Directory -Force -Path $OutputDir *> $null

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host " VISUAL AI STUDIO - SUIVI D'ADOPTION"
Write-Host "==================================================" -ForegroundColor Cyan

Write-Host "`n=== COLLECTE GITHUB ===" -ForegroundColor Cyan

$RepoData = gh api "repos/$Repo" | ConvertFrom-Json
$ReleaseData = gh api "repos/$Repo/releases/latest" | ConvertFrom-Json
$ViewsData = gh api "repos/$Repo/traffic/views" | ConvertFrom-Json
$ClonesData = gh api "repos/$Repo/traffic/clones" | ConvertFrom-Json
$ReferrersData = @(gh api "repos/$Repo/traffic/popular/referrers" | ConvertFrom-Json)
$IssuesData = @(gh api "repos/$Repo/issues?state=open&per_page=100" | ConvertFrom-Json | Where-Object { -not $_.pull_request })

$DiscussionQuery = 'query($owner:String!,$name:String!){repository(owner:$owner,name:$name){discussions(first:1){totalCount}}}'
$DiscussionData = gh api graphql -f query=$DiscussionQuery -F owner=$Owner -F name=$Name | ConvertFrom-Json

$SetupDownloads = 0
$AgentDownloads = 0
$HashDownloads = 0

$SetupAsset = $ReleaseData.assets | Where-Object { $_.name -eq "Visual-AI-Studio-Setup-0.1.0.exe" } | Select-Object -First 1
$AgentAsset = $ReleaseData.assets | Where-Object { $_.name -eq "studio-visuel-agent.zip" } | Select-Object -First 1
$HashAsset = $ReleaseData.assets | Where-Object { $_.name -eq "SHA256SUMS.txt" } | Select-Object -First 1

if ($SetupAsset) {
    $SetupDownloads = [int]$SetupAsset.download_count
}

if ($AgentAsset) {
    $AgentDownloads = [int]$AgentAsset.download_count
}

if ($HashAsset) {
    $HashDownloads = [int]$HashAsset.download_count
}

$OpenIssues = $IssuesData.Count
$Discussions = [int]$DiscussionData.data.repository.discussions.totalCount
$Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

$Snapshot = [PSCustomObject]@{
    Timestamp = $Timestamp
    Release = $ReleaseData.tag_name
    SetupDownloads = $SetupDownloads
    AgentDownloads = $AgentDownloads
    HashDownloads = $HashDownloads
    Stars = [int]$RepoData.stargazers_count
    Forks = [int]$RepoData.forks_count
    Watchers = [int]$RepoData.subscribers_count
    OpenIssues = $OpenIssues
    Discussions = $Discussions
    Views14d = [int]$ViewsData.count
    UniqueVisitors14d = [int]$ViewsData.uniques
    Clones14d = [int]$ClonesData.count
    UniqueCloners14d = [int]$ClonesData.uniques
}

Write-Host "`n=== TABLEAU DE BORD ===" -ForegroundColor Cyan

$Snapshot | Format-List

Write-Host "`n=== PRINCIPAUX REFERENTS ===" -ForegroundColor Cyan

if ($ReferrersData.Count -eq 0) {
    Write-Host "Aucun referent disponible pour le moment." -ForegroundColor DarkGray
}

if ($ReferrersData.Count -gt 0) {
    $ReferrersData |
        Sort-Object count -Descending |
        Select-Object -First 10 referrer,count,uniques |
        Format-Table -AutoSize
}

if (Test-Path $HistoryFile) {
    $Snapshot | Export-Csv -Path $HistoryFile -NoTypeInformation -Encoding UTF8 -Append
}

if (-not (Test-Path $HistoryFile)) {
    $Snapshot | Export-Csv -Path $HistoryFile -NoTypeInformation -Encoding UTF8
}

Write-Host "`n=== HISTORIQUE ===" -ForegroundColor Cyan
Write-Host $HistoryFile -ForegroundColor Green

Write-Host "`nNote : les telechargements GitHub ne representent pas des installations ou des utilisateurs actifs." -ForegroundColor Yellow
Write-Host "Les donnees Views/Clones couvrent les 14 derniers jours ; executer ce rapport regulierement conserve l'historique." -ForegroundColor Yellow
