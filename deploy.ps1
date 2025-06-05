<#
.SYNOPSIS
    Unified script to create/update Google Secret Manager secrets from a local .env file,
    grant IAM permissions on those secrets to a specified service account, and build/push/deploy
    a Dockerized bot to Google Cloud Run—passing secrets from Secret Manager as environment variables.

.DESCRIPTION
    1. Loads key/value pairs from a local .env file.
    2. For each secret defined in $SecretsToManage:
       - Creates the secret in GCP Secret Manager if it does not exist.
       - Adds a new version with the value loaded from .env.
       - Grants "roles/secretmanager.secretAccessor" to the specified service account.
    3. Enables required Google Cloud APIs.
    4. Builds and pushes a Docker image to Artifact Registry.
    5. Deploys the image to Cloud Run with min-instances=1, mapping secrets from Secret Manager
       into Cloud Run environment variables.

    Place this .ps1 file at the root of your project (next to Dockerfile and .env). Run in PowerShell 
    (with gcloud and Docker CLI installed and authenticated).

.NOTES
    - Requires: gcloud SDK, Docker CLI, PowerShell 5.1+ (or PowerShell Core).
    - Assumes the service account already exists (e.g., the Compute Engine default service account).
    - Adjust $SecretsToManage, $ServiceAccountEmail, and other configuration values as needed.

#>

#-----------------------------------------------
# --- BEGIN CONFIGURATION ---
#-----------------------------------------------
$ErrorActionPreference = "Stop"  # Halt on any error

# GCP Project and region
$ProjectID = "vital-axiom-343905"
$Region = "us-central1"

# Path to local .env file
$EnvFilePath = "./.env"

# Service account and IAM role for Secret Manager access
$ServiceAccountEmail = "142481835437-compute@developer.gserviceaccount.com"
$RoleToGrant = "roles/secretmanager.secretAccessor"

# Secrets to manage (must match keys in .env, case-sensitive)
$SecretsToManage = @(
    "GEMINI_API_KEY",
    "API_VERSION",
    "PHONE_NUMBER_ID",
    "ACCESS_TOKEN",
    "APP_SECRET",
    "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "WEBHOOK_VERIFY_TOKEN",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "SMTP_SERVER",
    "SMTP_PORT",
    "DB_URl"
)

# Docker / Artifact Registry / Cloud Run settings
$ArtifactRegistryRepository = "my-whatsapp-repo"
$ImageName = "whatsapp-bot"
$ImageTag = "latest"
$CloudRunServiceName = "whatsapp-bot-service"

# Construct the full image path for Artifact Registry
$ArtifactRegistryDomain = "$Region-docker.pkg.dev"
$FullImageName = "$ArtifactRegistryDomain/$ProjectID/$ArtifactRegistryRepository/$ImageName`:$ImageTag"

# Build the --set-secrets argument string for Cloud Run:
# Converts each secret name into "NAME=NAME:latest"
$SecretsForCloudRun = $SecretsToManage | ForEach-Object { "${_}=${_}:${ImageTag}" }
$SecretsGcloudArgumentString = "--set-secrets=$($SecretsForCloudRun -join ',')"

# API list to enable
$ApisToEnable = @(
    "iam.googleapis.com",
    "secretmanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com"
)
#-----------------------------------------------
# --- END CONFIGURATION ---
#-----------------------------------------------


#-----------------------------------------------
# Function: Get-EnvFile
#    Reads a .env‐style file (KEY=VALUE per line, ignoring comments) into a hashtable.
# Returns:
#    [hashtable] of KEY => VALUE pairs (with surrounding quotes stripped).
#-----------------------------------------------
function Get-EnvFile {
    param (
        [string]$Path
    )
    $envVars = @{}
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            $line = $_.Trim()
            if (-not [string]::IsNullOrWhiteSpace($line) -and $line -notmatch '^\s*#' -and $line -match '=') {
                $parts = $line.Split('=', 2)
                $key = $parts[0].Trim()
                $rawValue = $parts[1].Trim()

                # Strip surrounding single or double quotes, if present
                if (($rawValue.StartsWith('"') -and $rawValue.EndsWith('"')) -or
                    ($rawValue.StartsWith("'") -and $rawValue.EndsWith("'"))) {
                    if ($rawValue.Length -ge 2) {
                        $value = $rawValue.Substring(1, $rawValue.Length - 2)
                    }
                    else {
                        $value = ""
                    }
                }
                else {
                    $value = $rawValue
                }

                $envVars[$key] = $value
            }
        }
    }
    else {
        Write-Error "Environment file not found at '$Path'. Aborting."
        exit 1
    }

    return $envVars
}


#-----------------------------------------------
# STEP A: Load .env values
#-----------------------------------------------
Write-Host "=== STEP A: Loading environment variables from '$EnvFilePath' ===" -ForegroundColor Cyan
$LocalEnvValues = Get-EnvFile -Path $EnvFilePath

if ($LocalEnvValues.Count -eq 0) {
    Write-Warning "No key/value pairs loaded from '$EnvFilePath'. Ensure .env has valid entries."
}
else {
    Write-Host "Loaded the following variables from .env:" -ForegroundColor Cyan
    foreach ($kv in $LocalEnvValues.GetEnumerator()) {
        Write-Host "  $($kv.Key) = '$($kv.Value)' (Length: $($kv.Value.Length))"
    }
}
Write-Host ""


#-----------------------------------------------
# STEP B: Create or Update Secrets in Secret Manager
#-----------------------------------------------
Write-Host "=== STEP B: Creating/Updating secrets in Secret Manager ===" -ForegroundColor Cyan

foreach ($secretName in $SecretsToManage) {
    Write-Host "Processing secret: '$secretName'..." -ForegroundColor Yellow

    if (-not $LocalEnvValues.ContainsKey($secretName)) {
        Write-Warning "  SKIPPING: '$secretName' not found in .env. Ensure key exists."
        Write-Host "-----------------------------------"
        continue
    }

    $secretValueRaw = $LocalEnvValues[$secretName]
    if ($null -eq $secretValueRaw) {
        Write-Warning "  SKIPPING: '$secretName' has a null value."
        Write-Host "-----------------------------------"
        continue
    }

    # Clean CR/LF from the value
    $valueCleaned = $secretValueRaw.Replace("`r", "").Replace("`n", "")
    if ($secretValueRaw -ne $valueCleaned) {
        Write-Host "  Cleaned CR/LF from value: Length from $($secretValueRaw.Length) to $($valueCleaned.Length)." -ForegroundColor Green
    }

    # Check if the secret exists:
    $existing = $null
    try {
        $existing = gcloud secrets describe $secretName --project $ProjectID --format="value(name)" 2>$null
    }
    catch {
        # If describe fails, assume it does not exist
    }

    try {
        if ($existing) {
            Write-Host "  Secret '$secretName' exists. Adding new version..."
            $valueCleaned | gcloud secrets versions add $secretName --data-file=- --project $ProjectID
            Write-Host "  → Added new version to '$secretName'." -ForegroundColor Green
        }
        else {
            Write-Host "  Secret '$secretName' does not exist. Creating..."
            $valueCleaned | gcloud secrets create $secretName --data-file=- --replication-policy=automatic --project $ProjectID
            Write-Host "  → Created secret '$secretName'." -ForegroundColor Green
        }
    }
    catch {
        Write-Error "  ERROR processing '$secretName': $($_.Exception.Message)"
    }

    Write-Host "-----------------------------------"
}
Write-Host ""


#-----------------------------------------------
# STEP C: Grant IAM Permissions on Secrets
#-----------------------------------------------
Write-Host "=== STEP C: Granting IAM permissions on secrets ===" -ForegroundColor Cyan

foreach ($secretName in $SecretsToManage) {
    Write-Host "Granting '$RoleToGrant' on '$secretName' to '$ServiceAccountEmail'..." -ForegroundColor Yellow
    try {
        gcloud secrets add-iam-policy-binding $secretName `
            --member="serviceAccount:$ServiceAccountEmail" `
            --role="$RoleToGrant" `
            --project=$ProjectID
        Write-Host "  → Granted '$RoleToGrant' on '$secretName'." -ForegroundColor Green
    }
    catch {
        Write-Error "  FAILED to grant IAM on '$secretName': $($_.Exception.Message)"
    }
    Write-Host "-----------------------------------"
}
Write-Host ""


#-----------------------------------------------
# STEP D: Authenticate and Set GCP Project
#-----------------------------------------------
Write-Host "=== STEP D: Authenticating to Google Cloud and setting project ===" -ForegroundColor Cyan

$currentAuth = gcloud auth list --filter="status:ACTIVE" --format="value(account)"
$currentProj = gcloud config get-value project

Write-Host "Current active account: $currentAuth"
Write-Host "Current configured project: $currentProj"

if (-not $currentProj -or $currentProj -ne $ProjectID) {
    Write-Host "Setting gcloud project to '$ProjectID'..."
    gcloud config set project $ProjectID
}
else {
    Write-Host "Project already set to '$ProjectID'." -ForegroundColor Green
}
Write-Host ""


#-----------------------------------------------
# STEP E: Enable Required Google Cloud APIs
#-----------------------------------------------
Write-Host "=== STEP E: Enabling required Google Cloud APIs ===" -ForegroundColor Cyan
foreach ($api in $ApisToEnable) {
    Write-Host "Enabling API: $api..."
    try {
        gcloud services enable $api --project $ProjectID
        Write-Host "  → '$api' enabled (or was already enabled)." -ForegroundColor Green
    }
    catch {
        Write-Warning "  WARNING: Failed to enable '$api': $($_.Exception.Message)"
    }
}
Write-Host ""


#-----------------------------------------------
# STEP F: Configure Docker for Artifact Registry
#-----------------------------------------------
Write-Host "=== STEP F: Configuring Docker to authenticate with '$ArtifactRegistryDomain' ===" -ForegroundColor Cyan
try {
    gcloud auth configure-docker $ArtifactRegistryDomain --quiet
    Write-Host "  → Docker is now configured for '$ArtifactRegistryDomain'." -ForegroundColor Green
}
catch {
    Write-Error "  Failed to configure Docker authentication: $($_.Exception.Message)"
    exit 1
}
Write-Host ""


#-----------------------------------------------
# STEP G: Build and Push Docker Image
#-----------------------------------------------
Write-Host "=== STEP G: Building and pushing Docker image ===" -ForegroundColor Cyan
Write-Host "Building image: $FullImageName..."
try {
    docker build -t $FullImageName .
    Write-Host "  → Docker image built: $FullImageName" -ForegroundColor Green
}
catch {
    Write-Error "  Docker build failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "Pushing image to Artifact Registry: $FullImageName..."
try {
    docker push $FullImageName
    Write-Host "  → Docker image pushed: $FullImageName" -ForegroundColor Green
}
catch {
    Write-Error "  Docker push failed: $($_.Exception.Message)"
    exit 1
}
Write-Host ""


#-----------------------------------------------
# STEP H: Deploy to Cloud Run
#-----------------------------------------------
Write-Host "=== STEP H: Deploying to Google Cloud Run ===" -ForegroundColor Cyan
Write-Host "Service Name:          $CloudRunServiceName"
Write-Host "Region:                $Region"
Write-Host "Container Image URL:   $FullImageName"
Write-Host "Secrets Argument:      $SecretsGcloudArgumentString"
Write-Host "Min-Instances:         1"
Write-Host "Allow Unauthenticated: Yes"
Write-Host ""

# Construct and run the gcloud run deploy command via splatting
$gcloudRunArgs = @(
    "run",
    "deploy", $CloudRunServiceName,
    "--image", $FullImageName,
    "--platform", "managed",
    "--region", $Region,
    "--min-instances=1",
    "--allow-unauthenticated",
    $SecretsGcloudArgumentString,
    "--project", $ProjectID
)

try {
    Write-Host "Executing: gcloud $($gcloudRunArgs -join ' ')"
    & gcloud @gcloudRunArgs
    Write-Host "  → Cloud Run deployment submitted. Check above for status and URL." -ForegroundColor Green
}
catch {
    Write-Error "  Cloud Run deployment failed: $($_.Exception.Message)"
    exit 1
}

Write-Host "=== SCRIPT COMPLETED SUCCESSFULLY ===" -ForegroundColor Cyan
