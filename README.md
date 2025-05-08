# WhatsApp Business Bot

## Docker

### Creating image

```powershell
docker build -t whatsapp-business-bot-standart
```

### Starting Image

```powershell
docker run -it --rm -v "${PWD}:/main" --env-file .env -p 5000:5000 whatsapp-business-bot
```

### Cloud run Image

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

## Gemini API

>[!NOTE]
>[Create Gemini Api Key](https://aistudio.google.com/app/apikey)  
>[Gemini API Documentation](https://ai.google.dev/gemini-api/docs)  

We will be using `aiohttp` python package to handle asynchronous requests.  

### Example of request on Gemini API

```bash
curl 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY' \
-X POST \
-H 'Content-Type: application/json' \
-d '{
    "contents": [{
        "parts":[{
            "text": "Explain how AI works"
        }]
    }]
}'
```

## Gmail

For the email we will be using **aiosmtplib** for asynchronous email activities.  

>[!IMPORTANT]
>[Create an App password](https://myaccount.google.com/apppasswords).

## WhatsApp Business API

>[!NOTE]
>[WhatsApp Business Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)  
>[WhatsApp Redirect Links](https://faq.whatsapp.com/425247423114725/?cms_platform=iphone&fbclid=IwZXh0bgNhZW0CMTEAAR4lx_zu9Ws6yUlHIpOh7lLbg5GfwBgzV0Rn2s623WG__Arm-UEzouy33G3zhQ_aem_3gkVsuFTGTykNr3LZg-woQ)  
>[Conversation Components](https://developers.facebook.com/docs/whatsapp/cloud-api/phone-numbers/conversational-components/#commands)  
>[Messages Docs](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages)  
>[Flow Docs](https://developers.facebook.com/docs/whatsapp/flows/guides/implementingyourflowendpoint/?utm_source=social-youtube&utm_medium=m4d&utm_campaign=organic-social&utm_content=post-url&utm_offering=artificial-intelligence&utm_product=Connecting-WhatsApp-Flows-to-an-endpoint_07302024&eventSource=OrganicSocialM4D&content_id=eDxEekbvddA4lRy#setup)  

### Example of request on WhatsApp Business API

```bash
curl 'https://graph.facebook.com/<version>/<numbe id>/messages' \
-X POST \
-i \
-H 'Authorization: Bearer <access token>' \
-H 'Content-Type: application/json' \
-d '{ 
    "messaging_product": "whatsapp", 
    "to": "<number>", 
    "type": "template", 
    "template": { 
        "name": "hello_world", 
        "language": { "code": "en_US" } 
    }
}'
```

### Web Hook

### Flows

## FastAPI With Uvicorn

>[!NOTE]
>

>[!TIP]
>

>[!IMPORTANT]
>

>[!WARNING]

>[!CAUTION]