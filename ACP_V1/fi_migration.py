import os

# The correct PowerShell script content
ps_content = r"""# Aletheia ACP_V1 Migration Script
$ErrorActionPreference = "Stop"
$Root = Get-Location
$TargetRoot = Join-Path $Root "ACP_V1"

# --- 0. Define Helper Function ---
function Move-Component ($SourcePath, $DestPath, $Name) {
    if (Test-Path $SourcePath) {
        Write-Host "📦 Migrating $Name..." -ForegroundColor Yellow
        
        if (-not (Test-Path $DestPath)) { 
            New-Item -ItemType Directory -Force -Path $DestPath | Out-Null 
        }

        if ((Get-Item $SourcePath).PSIsContainer) {
            Copy-Item "$SourcePath\*" "$DestPath" -Recurse -Force
        } else {
            Copy-Item "$SourcePath" "$DestPath" -Force
        }
        
        Write-Host "   ✅ $Name installed." -ForegroundColor Green
    } else {
        Write-Warning "   ⚠️ Source not found: $Name"
    }
}

Write-Host "🚀 Starting Migration to ACP_V1 at: $TargetRoot" -ForegroundColor Cyan

# --- 1. Create Skeleton Structure ---
$DirsToCreate = @(
    "tooling\bundler", "tooling\ingest", "tooling\analysis", "validation",
    "brain\identity\configs", "brain\lenses", "brain\pipelines", "services",
    "ui\llm_builder", "ui\dashboard", "memory\sql", "memory\vector",
    "safe_ops\context\active", "safe_ops\context\archive", "config", "interface", "workflows"
)

foreach ($Dir in $DirsToCreate) {
    $Path = Join-Path $TargetRoot $Dir
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
        Write-Host "   + Created: $Dir" -ForegroundColor Gray
    }
}

# --- 2. Validation Suite ---
Move-Component "$Root\IRER_Validation_suite_run_ID-9" "$TargetRoot\validation" "IRER Validation Suite"

# --- 3. LLM Identity & Brain ---
$LLMSource = "$Root\Workspace_packager_LLM_construct"
if (-not (Test-Path $LLMSource)) { $LLMSource = "$Root\LLM_placeholder_identity" }

Move-Component "$LLMSource\identity" "$TargetRoot\brain\identity" "Identity Matrices"
Move-Component "$LLMSource\backend\configs" "$TargetRoot\brain\identity\configs" "Cognitive Configs"
Move-Component "$LLMSource\lenses" "$TargetRoot\brain\lenses" "Reasoning Lenses"
Move-Component "$LLMSource\pipelines" "$TargetRoot\brain\pipelines" "Cognitive Pipelines"
Move-Component "$LLMSource\frontend" "$TargetRoot\ui\llm_builder" "LLM Builder UI"

# --- 4. Canonical Logic ---
Move-Component "$Root\canonical_code_platform_port\analysis" "$TargetRoot\tooling\analysis" "Static Analysis Engine"
Move-Component "$Root\canonical_code_platform_port\extracted_services" "$TargetRoot\services" "Microservices Library"
Move-Component "$Root\canonical_code_platform_port\workflows" "$TargetRoot\workflows" "Workflow Definitions"
Move-Component "$Root\canonical_code_platform_port\ui_app.py" "$TargetRoot\ui\dashboard" "Streamlit Dashboard"

# --- 5. Core Tooling ---
Move-Component "$Root\directory_bundler_port" "$TargetRoot\tooling\bundler" "Directory Bundler"
Move-Component "$Root\Ingest_pipeline_V4r" "$TargetRoot\tooling\ingest" "Ingest Pipeline"

# --- 6. Perception Layer ---
if (Test-Path "$Root\Context_State") {
    Write-Host "👁️  Migrating Perception Layer..." -ForegroundColor Yellow
    Copy-Item "$Root\Context_State\*" "$TargetRoot\safe_ops\context" -Recurse -Force
}

# --- 7. Database Consolidation ---
Write-Host "🧠 Moving Knowledge Bases..." -ForegroundColor Yellow
$DBCandidates = @(
    "$Root\project_meta.db",
    "$Root\canonical_code_platform_port\canon.db",
    "$Root\canon.db"
)
$DBMoved = $false
foreach ($DB in $DBCandidates) {
    if (Test-Path $DB) {
        Copy-Item $DB "$TargetRoot\memory\sql\project_meta.db" -Force
        Write-Host "   > Installed SQL Brain from: $(Split-Path $DB -Leaf)" -ForegroundColor Green
        $DBMoved = $true
        break
    }
}
if (-not $DBMoved) { Write-Warning "No SQL Database found to migrate." }

# --- 8. Orchestrator Installation ---
if (Test-Path "$Root\backend_startup.py") {
    Copy-Item "$Root\backend_startup.py" "$TargetRoot\orchestrator.py" -Force
    Write-Host "   > Installed Orchestrator" -ForegroundColor Green
}
if (Test-Path "$Root\startup_config.yaml") {
    Copy-Item "$Root\startup_config.yaml" "$TargetRoot\config\startup.yaml" -Force
    Write-Host "   > Installed Configuration" -ForegroundColor Green
}

# --- 9. Cleanup Warnings ---
Write-Host "🏷️  Legacy Folder Status..." -ForegroundColor Yellow
$LegacyFolders = @("canonical_code_platform_port", "control_hub_port", "Ingest_pipeline_V4r", "directory_bundler_port")
foreach ($Folder in $LegacyFolders) {
    if (Test-Path "$Root\$Folder") {
        Write-Host "   [LEGACY] $Folder exists (Ready to archive)" -ForegroundColor Gray
    }
}

Write-Host "`n✅ MIGRATION COMPLETE!" -ForegroundColor Green
Write-Host "New System Root: $TargetRoot"
Write-Host "Next Step: Run 'cd ACP_V1' and then 'python orchestrator.py'"
"""

# Write the file safely
with open("migrate_to_acp.ps1", "w", encoding="utf-8") as f:
    f.write(ps_content)

print("✅ Successfully regenerated: migrate_to_acp.ps1")