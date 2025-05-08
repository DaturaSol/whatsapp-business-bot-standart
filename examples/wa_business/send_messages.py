# %% [markdown]
# # Send Messages
# 
# [**Oficial Documentation**](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/send-messages)  
# 
# We will be discussing how to send messages using the
# WhatsApp Business API and what kind of response is 
# expected to come with each.  
# 
# For our simple case we will use `Flask` in order 
# to keep everything simple, yet in our main 
# project we will be using Fast API to
# has access to asynchronous capabilities.
# %% [markdown] Index
# > ## Index
# > [Message Types](#message-types)  
# >
# > [Text Messages](#text-message)  
# >
# > [Message reply](#message-reply)  
# >
# > [Audio Messsages](#audio-messages)  
# >
# > [Video Messages](#video-messages)  
# >
# > [Images Messages](#image-message)  
# >
# > [Document Messages](#document-messages)  
# >
# > [Contact Messages](#contact-message)  
# >
# > [Call to Action url Button Message](#interactive-call-to-action-url-button-messages)  
# >
# > [List Messages](#interactive-list-messages)  
# >
# > [Button Messages](#interactive-reply-buttons-messages)  
# >
# 
# %% [markdown] Requirements for sending a message.
# ## Requirements for sending a message.
# 
# 1. API VERSION  
# 2. PHONE NUMBER ID  
# 3. ACCESS TOKEN  
# 4. RECIPIENT WA_ID  
# 
# We will be fetching from our current `.env`, 
# the information needed.  
# All can be found in the [app dashboard](https://developers.facebook.com/apps/).
# 
# ### Making links for message content.
# 
# ```bash
# https://drive.google.com/uc?export=download&id=YOUR_FILE_ID
# 
# ```
# 

# %% [markdown] Loads Data 
# ## Loads Data
# %%
from dotenv import load_dotenv
import os
from pathlib import Path
import requests
import json

dotenv_path = Path.cwd().resolve().parents[1] / ".env"
load_dotenv(dotenv_path=dotenv_path)

API_VERSION = os.getenv("API_VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
# URL to Send posts
URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}
# Etc
RECIPIENT_WA_ID = os.getenv("TESTER_NUMBER")
RECIPIENT_EMAIL = os.getenv("TESTER_EMAIL")

# %% [markdown] Message Types
# ## Message Types
# 
# All messages are sent as `POST` to this address 
# A Post need to be made to:  
# ```bash
# POST https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages
# ```
# 
# **With headers:**
# 
# ```json
# {
#     "Content-type": "application/json", 
#     "Authorization": "Bearer {ACCESS_TOKEN}"
# }
# ```
# 
# **The payload follows this structure**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "<MESSAGE_TYPE>",
#   "<MESSAGE_TYPE>": {<MESSAGE_CONTENTS>}
# }
# ```
# 
# **The response will usually follow this structure**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "contacts": [
#     {
#       "input": "<WHATSAPP_USER_PHONE_NUMBER>",
#       "wa_id": "<WHATSAPP_USER_ID>"
#     }
#   ],
#   "messages": [
#     {
#       "id": "<WHATSAPP_MESSAGE_ID>",
#       "message_status": "<PACING_STATUS>"
#     }
#   ]
# }
# ```
# 
# **RESPONSE error**
# ```json
# {
#     "error": {
#         "message": <MESSAGE>, 
#         "type": <EXCEPTION>, 
#         "code": 100, 
#         "error_subcode": 33, 
#         "fbtrace_id": <ID>
#     }
# }
# ```
# 

# %% [markdown] Text Message 
# ### Text Message 
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "text",
#   "text": {
#     "preview_url": <ENABLE_LINK_PREVIEW>,
#     "body": "<BODY_TEXT>"
#   }
# }
# ```

# %% No link
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "text",
    "text": {"body": "This is a message sent using GRAPH API"},
}


should_send = input(f"Send a text Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% With Link
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "text",
    "text": {
        "preview_url": True,
        "body": "https://music.youtube.com/watch?v=qlT3i80nSjc&si=SoxvMOUJkKa-XN5E\nI really like this song!",
    },
}


should_send = input(f"Send a text Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Message reply
# ### Message reply 
# 
# Requires WEBHOOK to get `message.id`.  
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "context": {
#     "message_id": "WAMID_TO_REPLY_TO"
#   },
# 
#   /* Message type and type contents goes here */
# 
# }
# ```
# 
# **MARKS AS READ**  
# 
# ```json
# {
#     "messaging_product": "whatsapp",
#     "status": "read",
#     "message_id": "message.id",
# }
# ```

# %%


# %% [markdown] Audio Messages 
# ### Audio Messages 
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "audio",
#   "audio": {
#     "id" : "<MEDIA_ID>", /* Only if using uploaded media */
#     "link" : "<MEDIA_URL>" /* Only if linking to your media */
#   }
# }
# ```
# 

# %%
# https://drive.google.com/uc?export=download&id=YOUR_FILE_ID
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "audio",
    "audio": {
        "link": "https://drive.google.com/uc?export=download&id=1Ld7eQG2zgGsrn9uVx5TVZYgpmcGyATqS"
    },
}


should_send = input(f"Send an audio Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Video Messages
# ### Video Messages
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "{{wa-user-phone-number}}",
#   "type": "video",
#   "video": {
#     "id" : "<MEDIA_ID>", /* Only if using uploaded media */
#     "link": "<MEDIA_URL>", /* Only if linking to your media */
#     "caption": "<VIDEO_CAPTION_TEXT>"
#   }
# }
# ```

# %%
# https://drive.google.com/uc?export=download&id=YOUR_FILE_ID
# https://drive.google.com/file/d/1hZK1sDInp398fBvOgnVXk7_hSSniOjVj/view?usp=sharing
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "video",
    "video": {
        "link": "https://drive.google.com/uc?export=download&id=1hZK1sDInp398fBvOgnVXk7_hSSniOjVj"
    },
}


should_send = input(f"Send a video Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Image Message
# ### Image Message
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "image",
#   "image": {
#     "id" : "<MEDIA_ID>", /* Only if using uploaded media */
#     "link": "<MEDIA_URL>", /* Only if linking to your media */
#     "caption": "<IMAGE_CAPTION_TEXT>"
#   }
# }
# ```
# 

# %%
# https://drive.google.com/file/d/1_fGiJYpiqh57qzb8P2cEg5JaVe-0Qo6R/view?usp=sharing
# https://drive.google.com/uc?export=download&id=YOUR_FILE_ID
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "image",
    "image": {
        "link": "https://drive.google.com/uc?export=download&id=1_fGiJYpiqh57qzb8P2cEg5JaVe-0Qo6R"
    },
}


should_send = input(f"Send a image Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Document Messages
# ### Document Messages
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "document",
#   "document": {
#     "id" : "<MEDIA_ID>", /* Only if using uploaded media */
#     "link": "<MEDIA_URL>", /* Only if linking to your media */
#     "caption": "<DOCUMENT_CAPTION>",
#     "filename": "<DOCUMENT_FILENAME>"
#   }
# }
# ```

# %%
# https://drive.google.com/file/d/1KNFjALfvC3G6cALGIfHBlHGc-sfIX0gK/view?usp=sharing
# https://drive.google.com/uc?export=download&id=YOUR_FILE_ID
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "document",
    "document": {
        "link": "https://drive.google.com/uc?export=download&id=1KNFjALfvC3G6cALGIfHBlHGc-sfIX0gK",
        "caption": "The communist manisfest for them communist",
        "filename": "Communist_Manifest.pdf",
    },
}


should_send = input(f"Send a document Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))


# %% [markdown] Contact Message 
# ### Contact Message 
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "contacts",
#   "contacts": [
#     {
#       "addresses": [
#         {
#           "street": "<STREET_NUMBER_AND_NAME>",
#           "city": "<CITY>",
#           "state": "<STATE_CODE>",
#           "zip": "<ZIP_CODE>",
#           "country": "<COUNTRY_NAME>",
#           "country_code": "<COUNTRY_CODE>",
#           "type": "<ADDRESS_TYPE>"
#         }
#         /* Additional addresses objects go here, if using */
#       ],
#       "birthday": "<BIRTHDAY>",
#       "emails": [
#         {
#           "email": "<EMAIL_ADDRESS>",
#           "type": "<EMAIL_TYPE>"
#         }
#         */ Additional emails objects go here, if using */
#       ],
#       "name": {
#         "formatted_name": "<FULL_NAME>",
#         "first_name": "<FIRST_NAME>",
#         "last_name": "<LAST_NAME>",
#         "middle_name": "<MIDDLE_NAME>",
#         "suffix": "<SUFFIX>",
#         "prefix": "<PREFIX>"
#       },
#       "org": {
#         "company": "<COMPANY_OR_ORG_NAME>",
#         "department": "<DEPARTMENT_NAME>",
#         "title": "<JOB_TITLE>"
#       },
#       "phones": [
#         {
#           "phone": "<PHONE_NUMBER>",
#           "type": "<PHONE_NUMBER_TYPE>",
#           "wa_id": "<WHATSAPP_USER_ID>"
#         }
#         /* Additional phones objects go here, if using */
#       ],
#       "urls": [
#         {
#           "url": "<WEBSITE_URL>",
#           "type": "<WEBSITE_TYPE>"
#         },
#         /* Additional URLs go here, if using */
#       ]
#     }
#   ]
# }
# ```

# %%
body = {
    "messaging_product": "whatsapp",
    "to": RECIPIENT_WA_ID,
    "type": "contacts",
    "contacts": [
        {
            "birthday": "2001-03-03",
            "emails": [{"email": RECIPIENT_EMAIL, "type": "E-Mail institucional"}],
            "name": {
                "formatted_name": "Gabriel Martins Silveira de Oliveira",
                "first_name": "Gabriel",
                "last_name": "Oliveira",
            },
            "org": {
                "company": "UnB",
                "department": "Engenharia da Computação",
                "title": "Estudante",
            },
            "phones": [
                {
                    "phone": RECIPIENT_WA_ID,
                    "wa_id": RECIPIENT_WA_ID,
                }
            ],
        }
    ],
}



should_send = input(f"Send a contact Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Interactive Call-to-Action URL Button Messages
# ### Interactive Call-to-Action URL Button Messages
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<CUSTOMER_PHONE_NUMBER>",
#   "type": "interactive",
#   "interactive": {
#     "type": "cta_url",
# 
#     /* Header optional */
#     "header": {
#       "type": "text",
#       "text": "<HEADER_TEXT>"
#     },
# 
#     /* Body optional */
#     "body": {
#       "text": "<BODY_TEXT>"
#     },
# 
#     /* Footer optional */
#     "footer": {
#       "text": "<FOOTER_TEXT>"
#     },
#     "action": {
#       "name": "cta_url",
#       "parameters": {
#         "display_text": "<BUTTON_TEXT>",
#         "url": "<BUTTON_URL>"
#       }
#     }
#   }
# }
# ```

# %%
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "interactive",
    "interactive": {
        "type": "cta_url",
        "header": {"type": "text", "text": "I Absolutely love this song"},
        "body": {"text": "One of my favorites bands Leprous"},
        "action": {
            "name": "cta_url",
            "parameters": {
                "display_text": "Music Video",
                "url": "https://youtu.be/IM5-xkdzCA4?si=AMnLGRiksVwyb_se",
            },
        },
    },
}



should_send = input(f"Send a Interactive Call-to-Action URL Button Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Interactive List Messages
# ### Interactive List Messages
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "interactive",
#   "interactive": {
#     "type": "list",
#     "header": {
#       "type": "text",
#       "text": "<MESSAGE_HEADER_TEXT"
#     },
#     "body": {
#       "text": "<MESSAGE_BODY_TEXT>"
#     },
#     "footer": {
#       "text": "<MESSAGE_FOOTER_TEXT>"
#     },
#     "action": {
#       "sections": [
#         {
#           "title": "<SECTION_TITLE_TEXT>",
#           "rows": [
#             {
#               "id": "<ROW_ID>",
#               "title": "<ROW_TITLE_TEXT>",
#               "description": "<ROW_DESCRIPTION_TEXT>"
#             }
#             /* Additional rows would go here*/
#           ]
#         }
#         /* Additional sections would go here */
#       ],
#       "button": "<BUTTON_TEXT>",
#     }
#   }
# }
# ```

# %%
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "interactive",
    "interactive": {
        "type": "list",
        "header": {"type": "text", "text": "Interactive List"},
        "body": {"text": "This is an interactive list message"},
        "action": {
            "sections": [
                {
                    "title": "Section 1",
                    "rows": [
                        {
                            "id": "test_id1",
                            "title": "Test 1",
                            "description": "This is a test",
                        },
                        {
                            "id": "test_id2",
                            "title": "test 2",
                            "description": "This is some description",
                        },
                    ],
                },
                {
                    "title": "Secrion 2",
                    "rows": [
                        {
                            "id": "test4",
                            "title": "Another test",
                            "description": "Another description",
                        }
                    ],
                },
            ],
            "button": "Options",
        },
    },
}


should_send = input(f"Send a Interactive List Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Interactive Reply Buttons Messages
# ### Interactive Reply Buttons Messages
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "<WHATSAPP_USER_PHONE_NUMBER>",
#   "type": "interactive",
#   "interactive": {
#     "type": "button",
#     "header": {<MESSAGE_HEADER>},
#     "body": {
#       "text": "<BODY_TEXT>"
#     },
#     "footer": {
#       "text": "<FOOTER_TEXT>"
#     },
#     "action": {
#       "buttons": [
#         {
#           "type": "reply",
#           "reply": {
#             "id": "<BUTTON_ID>",
#             "title": "<BUTTON_LABEL_TEXT>"
#           }
#         }
#       ]
#     }
#   }
# }
# ```
# 

# %%
body = {
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": RECIPIENT_WA_ID,
    "type": "interactive",
    "interactive": {
        "type": "button",
        "body": {"text": "Hey this is a button message"},
        "action": {
            "buttons": [
                {"type": "reply", "reply": {"id": "test_id1", "title": "✔️ Yes"}},
                {"type": "reply", "reply": {"id": "tesdt_id2", "title": "❌ No"}},
            ]
        },
    },
}


should_send = input(f"Send a Interactive Reply Buttons Message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

# %% [markdown] Template Messages
# ### Template Messages
# 
# **REQUEST**
# 
# ```json
# {
#   "messaging_product": "whatsapp",
#   "recipient_type": "individual",
#   "to": "PHONE_NUMBER",
#   "type": "template",
#   "template": {
#     "name": "TEMPLATE_NAME",
#     "language": {
#       "code": "LANGUAGE_AND_LOCALE_CODE"
#     },
#     "components": [
#          <NAMED_PARAMETER_INPUT>
#          <POSITIONAL_PARAMETER_INPUT>
#         ]
#       }
#     ]
#   }
# }
# ```

# %%


# %% [markdown] FLows 
# ### FLows 
# 
# [**DOCUMENTATION**](https://developers.facebook.com/docs/whatsapp/flows/guides/sendingaflow)
# 
# **REQUEST**
# 
# Minimum Parameters
# 
# ```json
# {
#   "recipient_type": "individual",
#   "messaging_product": "whatsapp",
#   "to": "whatsapp-id",
#   "type": "interactive",
#   "interactive": {
#     "type": "flow",
#     "header": {
#       "type": "text",
#       "text": "Flow message header"
#     },
#     "body": {
#       "text": "Flow message body"
#     },
#     "footer": {
#       "text": "Flow message footer"
#     },
#     "action": {
#       "name": "flow",
#       "parameters": {
#         "mode": "draft",
#         "flow_message_version": "3",
#         "flow_name": "appointment_booking_v1", //or flow_id
#         "flow_cta": "Book!"
#       }
#     }
#   }
# }
# ```
# 
# All Parameters 
# 
# ```json
# {
#   "recipient_type": "individual",
#   "messaging_product": "whatsapp",
#   "to": "whatsapp-id",
#   "type": "interactive",
#   "interactive": {
#     "type": "flow",
#     "header": {
#       "type": "text",
#       "text": "Flow message header"
#     },
#     "body": {
#       "text": "Flow message body"
#     },
#     "footer": {
#       "text": "Flow message footer"
#     },
#     "action": {
#       "name": "flow",
#       "parameters": {
#         "flow_message_version": "3",
#         "flow_token": "AQAAAAACS5FpgQ_cAAAAAD0QI3s.",
# 
#         "flow_name": "appointment_booking_v1",
#         //or
#         "flow_id": "123456",
# 
#         "flow_cta": "Book!",
#         "flow_action": "navigate",
#         "flow_action_payload": {
#           "screen": "<SCREEN_NAME>",
#           "data": { 
#             "product_name": "name",
#             "product_description": "description",
#             "product_price": 100
#           }
#         }
#       }
#     }
#   }
# }
# ```

# %%
body = {
    "recipient_type": "individual",
    "messaging_product": "whatsapp",
    "to": RECIPIENT_WA_ID,
    "type": "interactive",
    "interactive": {
        "type": "flow",
        "header": {"type": "text", "text": "Flow message header"},
        "body": {"text": "Flow message body"},
        "footer": {"text": "Flow message footer"},
        "action": {
            "name": "flow",
            "parameters": {
                "mode": "draft",
                "flow_message_version": "3",
                "flow_name": "Message templates_MARKETING_3035607b-7",
                "flow_cta": "Test Flow",
            },
        },
    },
}


should_send = input(f"Send a simple flow message to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()
    print(json.dumps(json_response, indent=4))

