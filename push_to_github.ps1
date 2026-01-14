$repoUrl = "https://github.com/leochenn/ai-assistant-skills.git"
$branch = "main"

Write-Host "🚀 Starting backup to $repoUrl..." -ForegroundColor Cyan

# Initialize Git if not already
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..."
    git init
}

# Add Remote if not exists
$remotes = git remote
if ($remotes -notcontains "origin") {
    Write-Host "Adding remote origin..."
    git remote add origin $repoUrl
} else {
    Write-Host "Remote origin already exists, updating URL..."
    git remote set-url origin $repoUrl
}

# Pull first to avoid conflicts (allow unrelated histories for fresh repos)
Write-Host "Pulling remote changes..."
git pull origin $branch --allow-unrelated-histories

# Add all files
Write-Host "Adding files..."
git add .

# Commit
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "Backup skills: $timestamp"

# Push
Write-Host "Pushing to GitHub..."
git branch -M $branch
git push -u origin $branch

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Success! Your skills are backed up." -ForegroundColor Green
} else {
    Write-Host "`n❌ Error: Push failed. Please check your git credentials." -ForegroundColor Red
}
