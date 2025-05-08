# %% [markdown]
# # Web Hooks
#
# [**Oficial Documentation**](https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks)
#
# A quick guide on webhooks
# %% [markdown] Index
# > ## Index
# > [WebHook Format](#webhook-format)
# >
# > [Text messages](#text-messages)
# >
# > [Reaction Messages](#reaction-messages)
# >
# > [Media Messages](#media-messages)
# >
# > [Unknown Messages](#unknown-messages)
# >
# > [Location Messages](#location-messages)
# >
# > [Contacts Messages](#contacts-messages)
# >
# > [Call back quick reply button](#received-callback-from-a-quick-reply-button)
# >
# > [List Message](#received-answer-from-list-message)
# >
# > [Button Message](#received-answer-to-reply-button)
# >
# > [WhatsApp Ads](#received-message-triggered-by-click-to-whatsapp-ads)
# >
# > [Change number](#user-changed-number-notification)
# >
# > [Message Status](#message-status-updates)
# >
# > [Simple WebHook](#simple-webhook)
# >
# %% [markdown] WebHook format
# ## WebHook format
#
# All WebHooks follow this format
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID"
#                        },
#                # specific Webhooks payload
#                    },
#                    "field": "messages"
#                }
#            ]
#        }
#    ]
# }
# ```

# %% [markdown] Text Messages
#
# ## Text Messages
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                            "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                        },
#                        "contacts": [
#                            {
#                                "profile": {"name": "<WHATSAPP_USER_NAME>"},
#                                "wa_id": "<WHATSAPP_USER_ID>",
#                            }
#                        ],
#                        "messages": [
#                            {
#                                "from": "<WHATSAPP_USER_PHONE_NUMBER>",
#                                "id": "<WHATSAPP_MESSAGE_ID>",
#                                "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                "text": {"body": "<MESSAGE_BODY_TEXT>"},
#                                "type": "text",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
# %% [markdown] Reaction messages
#
# ## Reaction messages
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": PHONE_NUMBER,
#                            "phone_number_id": PHONE_NUMBER_ID,
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": PHONE_NUMBER}
#                        ],
#                        "messages": [
#                            {
#                                "from": PHONE_NUMBER,
#                                "id": "wamid.ID",
#                                "timestamp": TIMESTAMP,
#                                "reaction": {
#                                    "message_id": "MESSAGE_ID",
#                                    "emoji": "EMOJI",
#                                },
#                                "type": "reaction",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```

# %% [markdown] Media Messages
#
# ## Media Messages
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": PHONE_NUMBER,
#                            "phone_number_id": PHONE_NUMBER_ID,
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "WHATSAPP_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "from": PHONE_NUMBER,
#                                "id": "wamid.ID",
#                                "timestamp": TIMESTAMP,
#                                "type": "image",
#                                "image": {
#                                    "caption": "CAPTION",
#                                    "mime_type": "image/jpeg",
#                                    "sha256": "IMAGE_HASH",
#                                    "id": "ID",
#                                },
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#
# **For Stickers**
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID",
#                        },
#                        "contacts": [{"profile": {"name": "NAME"}, "wa_id": "ID"}],
#                        "messages": [
#                            {
#                                "from": "SENDER_PHONE_NUMBER",
#                                "id": "wamid.ID",
#                                "timestamp": "TIMESTAMP",
#                                "type": "sticker",
#                                "sticker": {
#                                    "mime_type": "image/webp",
#                                    "sha256": "HASH",
#                                    "id": "ID",
#                                },
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
# %% [markdown] Unknown Messages
#
# ## Unknown Messages
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID",
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "WHATSAPP_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "from": "PHONE_NUMBER",
#                                "id": "wamid.ID",
#                                "timestamp": "TIMESTAMP",
#                                "errors": [
#                                    {
#                                        "code": 131051,
#                                        "details": "Message type is not currently supported",
#                                        "title": "Unsupported message type",
#                                    }
#                                ],
#                                "type": "unknown",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#

# %% [markdown] Location Messages
#
# ## Location Messages
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID",
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "WHATSAPP_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "from": "PHONE_NUMBER",
#                                "id": "wamid.ID",
#                                "timestamp": "TIMESTAMP",
#                                "location": {
#                                    "latitude": LOCATION_LATITUDE,
#                                    "longitude": LOCATION_LONGITUDE,
#                                    "name": LOCATION_NAME,
#                                    "address": LOCATION_ADDRESS,
#                                },
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```

# %% [markdown] Contacts Messages
# ## Contacts Messages
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID",
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "WHATSAPP_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "from": "PHONE_NUMBER",
#                                "id": "wamid.ID",
#                                "timestamp": "TIMESTAMP",
#                                "contacts": [
#                                    {
#                                        "addresses": [
#                                            {
#                                                "city": "CONTACT_CITY",
#                                                "country": "CONTACT_COUNTRY",
#                                                "country_code": "CONTACT_COUNTRY_CODE",
#                                                "state": "CONTACT_STATE",
#                                                "street": "CONTACT_STREET",
#                                                "type": "HOME or WORK",
#                                                "zip": "CONTACT_ZIP",
#                                            }
#                                        ],
#                                        "birthday": "CONTACT_BIRTHDAY",
#                                        "emails": [
#                                            {
#                                                "email": "CONTACT_EMAIL",
#                                                "type": "WORK or HOME",
#                                            }
#                                        ],
#                                        "name": {
#                                            "formatted_name": "CONTACT_FORMATTED_NAME",
#                                            "first_name": "CONTACT_FIRST_NAME",
#                                            "last_name": "CONTACT_LAST_NAME",
#                                            "middle_name": "CONTACT_MIDDLE_NAME",
#                                            "suffix": "CONTACT_SUFFIX",
#                                            "prefix": "CONTACT_PREFIX",
#                                        },
#                                        "org": {
#                                            "company": "CONTACT_ORG_COMPANY",
#                                            "department": "CONTACT_ORG_DEPARTMENT",
#                                            "title": "CONTACT_ORG_TITLE",
#                                        },
#                                        "phones": [
#                                            {
#                                                "phone": "CONTACT_PHONE",
#                                                "wa_id": "CONTACT_WA_ID",
#                                                "type": "HOME or WORK>",
#                                            }
#                                        ],
#                                        "urls": [
#                                            {
#                                                "url": "CONTACT_URL",
#                                                "type": "HOME or WORK",
#                                            }
#                                        ],
#                                    }
#                                ],
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#

# %% [markdown] Received Callback from a Quick Reply Button
# ## Received Callback from a Quick Reply Button
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": PHONE_NUMBER,
#                            "phone_number_id": PHONE_NUMBER_ID,
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "WHATSAPP_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "context": {"from": PHONE_NUMBER, "id": "wamid.ID"},
#                                "from": "16315551234",
#                                "id": "wamid.ID",
#                                "timestamp": TIMESTAMP,
#                                "type": "button",
#                                "button": {
#                                    "text": "No",
#                                    "payload": "No-Button-Payload",
#                                },
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```

# %% [markdown] Received Answer From List Message
# ## Received Answer From List Message
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID",
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "PHONE_NUMBER_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "from": PHONE_NUMBER_ID,
#                                "id": "wamid.ID",
#                                "timestamp": TIMESTAMP,
#                                "interactive": {
#                                    "list_reply": {
#                                        "id": "list_reply_id",
#                                        "title": "list_reply_title",
#                                        "description": "list_reply_description",
#                                    },
#                                    "type": "list_reply",
#                                },
#                                "type": "interactive",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
##

# %% [markdown] Received Answer to Reply Button
# ## Received Answer to Reply Button
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": PHONE_NUMBER_ID,
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": "PHONE_NUMBER_ID"}
#                        ],
#                        "messages": [
#                            {
#                                "from": PHONE_NUMBER_ID,
#                                "id": "wamid.ID",
#                                "timestamp": TIMESTAMP,
#                                "interactive": {
#                                    "button_reply": {
#                                        "id": "unique-button-identifier-here",
#                                        "title": "button-text",
#                                    },
#                                    "type": "button_reply",
#                                },
#                                "type": "interactive",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#

# %% [markdown] Received Message Triggered by Click to WhatsApp Ads
# ## Received Message Triggered by Click to WhatsApp Ads
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "PHONE_NUMBER",
#                            "phone_number_id": "PHONE_NUMBER_ID",
#                        },
#                        "contacts": [{"profile": {"name": "NAME"}, "wa_id": "ID"}],
#                        "messages": [
#                            {
#                                "referral": {
#                                    "source_url": "AD_OR_POST_FB_URL",
#                                    "source_id": "ADID",
#                                    "source_type": "ad or post",
#                                    "headline": "AD_TITLE",
#                                    "body": "AD_DESCRIPTION",
#                                    "media_type": "image or video",
#                                    "image_url": "RAW_IMAGE_URL",
#                                    "video_url": "RAW_VIDEO_URL",
#                                    "thumbnail_url": "RAW_THUMBNAIL_URL",
#                                    "ctwa_clid": "CTWA_CLID",
#                                },
#                                "from": "SENDER_PHONE_NUMBERID",
#                                "id": "wamid.ID",
#                                "timestamp": "TIMESTAMP",
#                                "type": "text",
#                                "text": {"body": "BODY"},
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#

# %% [markdown] User Changed Number Notification
# ## User Changed Number Notification
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": PHONE_NUMBER,
#                            "phone_number_id": PHONE_NUMBER_ID,
#                        },
#                        "messages": [
#                            {
#                                "from": PHONE_NUMBER,
#                                "id": "wamid.ID",
#                                "system": {
#                                    "body": "NAME changed from PHONE_NUMBER to PHONE_NUMBER",
#                                    "new_wa_id": NEW_PHONE_NUMBER,
#                                    "type": "user_changed_number",
#                                },
#                                "timestamp": TIMESTAMP,
#                                "type": "system",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#

# %% [markdown] Message Status Updates
# ## Message Status Updates
#
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                            "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                        },
#                        "statuses": [
#                            {
#                                "id": "<WHATSAPP_MESSAGE_ID>",
#                                "status": "sent",
#                                "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                "recipient_id": "<WHATSAPP_USER_ID>",
#                                "conversation": {
#                                    "id": "<CONVERSATION_ID>",
#                                    "expiration_timestamp": "<CONVERSATION_EXPIRATION_TIMESTAMP>",
#                                    "origin": {"type": "<CONVERSATION_CATEGORY>"},
#                                },
#                                "pricing": {
#                                    "billable": IS_BILLABLE,
#                                    "pricing_model": "CBP",
#                                    "category": "<CONVERSATION_CATEGORY>",
#                                },
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#
# ### Status Message Delivered
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                            "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                        },
#                        "statuses": [
#                            {
#                                "id": "<WHATSAPP_MESSAGE_ID>",
#                                "status": "sent",
#                                "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                "recipient_id": "<WHATSAPP_USER_ID>",
#                                "conversation": {
#                                    "id": "<CONVERSATION_ID>",
#                                    "origin": {"type": "<CONVERSATION_CATEGORY>"},
#                                },
#                                "pricing": {
#                                    "billable": IS_BILLABLE,
#                                    "pricing_model": "CBP",
#                                    "category": "<CONVERSATION_CATEGORY>",
#                                },
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#
# ### Status Message Read
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                            "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                        },
#                        "statuses": [
#                            {
#                                "id": "<WHATSAPP_MESSAGE_ID>",
#                                "status": "read",
#                                "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                "recipient_id": "<WHATSAPP_USER_ID>",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#
# ### Status Message Deleted
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": PHONE_NUMBER,
#                            "phone_number_id": PHONE_NUMBER,
#                        },
#                        "contacts": [
#                            {"profile": {"name": "NAME"}, "wa_id": PHONE_NUMBER}
#                        ],
#                        "messages": [
#                            {
#                                "from": PHONE_NUMBER,
#                                "id": "wamid.ID",
#                                "timestamp": TIMESTAMP,
#                                "errors": [
#                                    {
#                                        "code": 131051,
#                                        "details": "Message type is not currently supported",
#                                        "title": "Unsupported message type",
#                                    }
#                                ],
#                                "type": "unsupported",
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```
#
# ### Status Message Failed
#
# ```json
# {
#    "object": "whatsapp_business_account",
#    "entry": [
#        {
#            "id": "<WHATSAPP_BUSINESS_ACCOUNT_ID>",
#            "changes": [
#                {
#                    "value": {
#                        "messaging_product": "whatsapp",
#                        "metadata": {
#                            "display_phone_number": "<BUSINESS_DISPLAY_PHONE_NUMBER>",
#                            "phone_number_id": "<BUSINESS_PHONE_NUMBER_ID>",
#                        },
#                        "statuses": [
#                            {
#                                "id": "<WHATSAPP_MESSAGE_ID>",
#                                "status": "failed",
#                                "timestamp": "<WEBHOOK_SENT_TIMESTAMP>",
#                                "recipient_id": "<WHATSAPP_USER_ID>",
#                                "errors": [
#                                    {
#                                        "code": ERROR_CODE,
#                                        "title": "<ERROR_TITLE>",
#                                        "message": "<ERROR_MESSAGE>",
#                                        "error_data": {"details": "<ERROR_DETAILS>"},
#                                        "href": "https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes/",
#                                    }
#                                ],
#                            }
#                        ],
#                    },
#                    "field": "messages",
#                }
#            ],
#        }
#    ],
# }
# ```

# %% [markdown] FLow Response
# ### FLow Response
#
# ```json
#{
#    "messages": [
#        {
#            "context": {"from": "16315558151", "id": "gBGGEiRVVgBPAgm7FUgc73noXjo"},
#            "from": "<USER_ACCOUNT_NUMBER>",
#            "id": "<MESSAGE_ID>",
#            "type": "interactive",
#            "interactive": {
#                "type": "nfm_reply",
#                "nfm_reply": {
#                    "name": "flow",
#                    "body": "Sent",
#                    "response_json": '{"flow_token": "<FLOW_TOKEN>", "optional_param1": "<value1>", "optional_param2": "<value2>"}',
#                },
#            },
#            "timestamp": "<MESSAGE_SEND_TIMESTAMP>",
#        }
#    ]
#}
# ```

# %% [markdown]
# ## Simple WebHook
# %%
from dotenv import load_dotenv
import os
from pathlib import Path

dotenv_path = Path.cwd().resolve().parents[1] / ".env"
load_dotenv(dotenv_path=dotenv_path)

API_VERSION = os.getenv("API_VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
# URL to Send posts
URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"
HEADERS = {
    "Content-type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}",
}

from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403


@app.route("/webhook", methods=["POST"])
def handle_post():
    payload = request.json

    print(json.dumps(payload, indent=4))

    return jsonify({"status": "success"}), 200


should_run = input("Run simple webhook? [y/n]").lower().strip() == "y"
if should_run:
    app.run(host="0.0.0.0", port=5000)
