# WhatsApp Business Bot

```powershell
docker build -t whatsapp-business-bot
```

```powershell
docker run -it --rm -v "${PWD}:/main" --env-file .env -p 5000:5000 whatsapp-business-bot
```

```powershell
# Replace placeholders with your actual values
gcloud run deploy my-cloud-run-service-name \
    --image YOUR_REGION-docker.pkg.dev/YOUR_PROJECT_ID/YOUR_REPO/whatsapp-business-bot:latest \
    --platform managed \
    --region YOUR_REGION \
    --allow-unauthenticated \ # Or use --no-allow-unauthenticated
    --set-secrets="API_KEY=your-secret-manager-api-key-name:latest" \
    --set-secrets="DATABASE_URL=your-secret-manager-db-url-name:latest"
    # Add other --set-secrets flags as needed
```
