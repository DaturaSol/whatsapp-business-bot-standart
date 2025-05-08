# %% [markdown]
# # Flows
#
# [**Oficial Documentation**](https://developers.facebook.com/docs/whatsapp/flows/guides)
# [**More documentation**](https://developers.facebook.com/docs/whatsapp/flows/reference/flowjson/#routing-model)
# %% [markdown] Send simple FLow
# ## Send simple FLow
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
from dotenv import load_dotenv
from pathlib import Path
import requests
import json
import os

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



should_send_simple_flow = input(f"Send a simplee flow to {RECIPIENT_WA_ID}? [y/n]").lower().strip() == "y"
if should_send_simple_flow:
    response = requests.post(url=URL, headers=HEADERS, json=body)
    json_response = response.json()

    print(json.dumps(json_response, indent=4))

# %% [markdown] Webhook for flow
# ## Webhook for flow
#
# Expected reponse
#
# ```json
# {
#   "messages": [{
#     "context": {
#       "from": "16315558151",
#       "id": "gBGGEiRVVgBPAgm7FUgc73noXjo"
#     },
#     "from": "<USER_ACCOUNT_NUMBER>",
#     "id": "<MESSAGE_ID>",
#     "type": "interactive",
#     "interactive": {
#       "type": "nfm_reply",
#       "nfm_reply": {
#         "name": "flow",
#         "body": "Sent",
#         "response_json": "{\"flow_token\": \"<FLOW_TOKEN>\", \"optional_param1\": \"<value1>\", \"optional_param2\": \"<value2>\"}"
#       }
#     },
#     "timestamp": "<MESSAGE_SEND_TIMESTAMP>"
#   }]
# }
# ```

# %%
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from pathlib import Path
import requests
import json
import os

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


should_run_webhook = input("Run simple WebHook? [y/n]").lower().strip() == "y"
if should_run_webhook:
    app.run(host="0.0.0.0", port=5000)

# %% [markdown] Creating a flow
# ## Creating a flow
#
# ### Example
#
# No data exchange or anything
#
# ```json
# {
#   "screens": [
#     {
#       "data": {},
#       "id": "Frist_Page",
#       "layout": {
#         "children": [
#           {
#             "children": [
#               {
#                 "text": "Datura Stramonium",
#                 "type": "TextHeading"
#               },
#               {
#                 "text": "My favorite plant",
#                 "type": "TextSubheading"
#               },
#               {
#                 "height": 400,
#                 "scale-type": "contain",
#                 "src": "",
#                 "type": "Image"
#               },
#               {
#                 "type": "TextCaption",
#                 "text": "Datura is probably my favorite plant\nabeautiful plant that should not be touched."
#               },
#               {
#                 "text": "This flow will serve for me as a way to identify how to write these things",
#                 "type": "TextBody"
#               },
#               {
#                 "label": "Continue",
#                 "on-click-action": {
#                   "name": "navigate",
#                   "next": {
#                     "name": "second_screen",
#                     "type": "screen"
#                   },
#                   "payload": {}
#                 },
#                 "type": "Footer"
#               }
#             ],
#             "name": "flow_path",
#             "type": "Form"
#           }
#         ],
#         "type": "SingleColumnLayout"
#       },
#       "title": "Media and text"
#     },
#     {
#       "data": {},
#       "id": "second_screen",
#       "layout": {
#         "children": [
#           {
#             "children": [
#               {
#                 "input-type": "text",
#                 "label": "Name",
#                 "name": "name",
#                 "required": false,
#                 "type": "TextInput",
#                 "helper-text": "Write your name"
#               },
#               {
#                 "input-type": "phone",
#                 "label": "Write your number",
#                 "name": "phone_number",
#                 "required": false,
#                 "type": "TextInput",
#                 "helper-text": "Please"
#               },
#               {
#                 "input-type": "email",
#                 "label": "Email",
#                 "name": "email",
#                 "required": false,
#                 "type": "TextInput",
#                 "helper-text": "Please"
#               },
#               {
#                 "input-type": "password",
#                 "label": "Password",
#                 "name": "password",
#                 "required": false,
#                 "type": "TextInput",
#                 "helper-text": "Your pass Word"
#               },
#               {
#                 "label": "Your story",
#                 "name": "story",
#                 "required": false,
#                 "type": "TextArea",
#                 "helper-text": "Write a bit about yourself"
#               },
#               {
#                 "label": "Pick a Date",
#                 "name": "date",
#                 "required": false,
#                 "type": "DatePicker",
#                 "helper-text": "Please"
#               },
#               {
#                 "label": "Continue",
#                 "on-click-action": {
#                   "name": "navigate",
#                   "next": {
#                     "name": "third_screen",
#                     "type": "screen"
#                   },
#                   "payload": {
#                     "name": "${form.name}",
#                     "phone_number": "${form.phone_number}",
#                     "email": "${form.email}",
#                     "password": "${form.password}",
#                     "story": "${form.story}",
#                     "date": "${form.date}"
#                   }
#                 },
#                 "type": "Footer"
#               }
#             ],
#             "name": "flow_path",
#             "type": "Form"
#           }
#         ],
#         "type": "SingleColumnLayout"
#       },
#       "title": "Text answer"
#     },
#     {
#       "data": {
#         "name": {
#           "__example__": "Example",
#           "type": "string"
#         },
#         "phone_number": {
#           "__example__": "Example",
#           "type": "string"
#         },
#         "email": {
#           "__example__": "Example",
#           "type": "string"
#         },
#         "password": {
#           "__example__": "Example",
#           "type": "string"
#         },
#         "story": {
#           "__example__": "Example",
#           "type": "string"
#         },
#         "date": {
#           "__example__": "Example",
#           "type": "string"
#         }
#       },
#       "id": "third_screen",
#       "layout": {
#         "children": [
#           {
#             "children": [
#               {
#                 "data-source": [
#                   {
#                     "id": "Option_1",
#                     "title": "Option 1"
#                   },
#                   {
#                     "id": "Option_2",
#                     "title": "Option 2"
#                   }
#                 ],
#                 "label": "Choose one",
#                 "name": "choose_one",
#                 "required": false,
#                 "type": "RadioButtonsGroup"
#               },
#               {
#                 "data-source": [
#                   {
#                     "id": "Option_1",
#                     "title": "Option 1"
#                   },
#                   {
#                     "id": "Option_2",
#                     "title": "Option 2"
#                   },
#                   {
#                     "id": "Option_3",
#                     "title": "Option 3"
#                   }
#                 ],
#                 "label": "Choose a few",
#                 "name": "choose_a_few",
#                 "required": false,
#                 "type": "CheckboxGroup"
#               },
#               {
#                 "data-source": [
#                   {
#                     "id": "Option_1",
#                     "title": "Option 1"
#                   },
#                   {
#                     "id": "Option_2",
#                     "title": "Option 2"
#                   },
#                   {
#                     "id": "Option_3",
#                     "title": "Option 3"
#                   }
#                 ],
#                 "label": "Select one",
#                 "name": "select_one",
#                 "required": false,
#                 "type": "Dropdown"
#               },
#               {
#                 "label": "Aceitar termos ?",
#                 "name": "aceitar_termos",
#                 "required": false,
#                 "type": "OptIn",
#                 "on-click-action": {
#                   "name": "navigate",
#                   "next": {
#                     "name": "OPTIN_SCREEN_screen_nnpmwb",
#                     "type": "screen"
#                   },
#                   "payload": {}
#                 }
#               },
#               {
#                 "label": "Complete",
#                 "on-click-action": {
#                   "name": "complete",
#                   "payload": {
#                     "choose_one": "${form.choose_one}",
#                     "choose_a_few": "${form.choose_a_few}",
#                     "select_one": "${form.select_one}",
#                     "aceitar_termos": "${form.Aceitar_termos}",
#                     "name": "${data.name}",
#                     "phone_n umber": "${data.phone_number}",
#                     "email": "${data.email}",
#                     "password": "${data.password}",
#                     "story": "${data.story}",
#                     "date": "${data.date}"
#                   }
#                 },
#                 "type": "Footer"
#               }
#             ],
#             "name": "flow_path",
#             "type": "Form"
#           }
#         ],
#         "type": "SingleColumnLayout"
#       },
#       "terminal": true,
#       "title": "Selection"
#     },
#     {
#       "data": {},
#       "id": "OPTIN_SCREEN_screen_nnpmwb",
#       "layout": {
#         "children": [
#           {
#             "children": [
#               {
#                 "text": "A cranium\namazing right ?",
#                 "type": "TextBody"
#               },
#               {
#                 "height": 200,
#                 "scale-type": "contain",
#                 "src": "",
#                 "type": "Image"
#               }
#             ],
#             "name": "flow_path",
#             "type": "Form"
#           }
#         ],
#         "type": "SingleColumnLayout"
#       },
#       "title": "Read more"
#     }
#   ],
#   "version": "7.0"
# }
# ```

# %% [markdown] Enconde images to use in this shiat
# ## Enconde images to use in this shiat
# %%
import base64

image_path = Path.cwd().resolve().parents[1] / "assets/images/logo.png"

with open(image_path, "rb") as image_file:
    encoded_bytes = base64.b64encode(image_file.read())

encoded_string = encoded_bytes.decode("utf-8")

print(encoded_string)


# %% [markdown] Endpoint
# ## Endpoint
#
# To make a stupid endpoint we need to create a private key...
# %% [markdown] Creating a stupid private key and uploading it
# ### Creating a stupid private key and uploading it
# %%
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

dotenv_path = Path.cwd().resolve().parents[1] / ".env"
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)

PASSPHRASE = os.getenv("PASSPHRASE")
if not all([PASSPHRASE]):
    raise ValueError("Missing one or more required environment variables (PASSPHRASE)")

print("Environment variables loaded.")

# --- Key Generation ---
print("Generating RSA key pair...")
# Generate RSA key pair (2048 bits)
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize private key using a symmetric encryption cipher (here, BestAvailableEncryption)
private_key_pem_bytes = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,  # equivalent to PKCS#1
    encryption_algorithm=serialization.BestAvailableEncryption(
        PASSPHRASE.encode("utf-8")
    ),
)

# Serialize public key in PEM format (using SubjectPublicKeyInfo)
public_key_pem_bytes = key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# *** This is the key format needed for the API ***
# Decode the bytes to a UTF-8 string
public_key_pem_string = public_key_pem_bytes.decode("utf-8")
private_key_pem_string = private_key_pem_bytes.decode("utf-8")

print("Key pair generated.")
# print("\nPublic Key (PEM Format):\n", public_key_pem_string)  # Optional: print the key

# %% [markdown] Saves Pair Key to DotEnv
# ### Saves Pair Key to DotEnv
# %%
should_upload_key = input("Save keys on .env? [y/n]").lower().strip() == "y"
if should_upload_key:
    set_key(
        dotenv_path,
        "PRIVATE_KEY",
        private_key_pem_string,
    )
    set_key(dotenv_path, "PUBLIC_KEY", public_key_pem_string)
    print("Key saved on dotenv.")

# %% [markdown] Uploads to Meta
# ### Uploads to Meta
# %%
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path.cwd().resolve().parents[1] / ".env"
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)

API_VERSION = os.getenv("API_VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
if not all([API_VERSION, PHONE_NUMBER_ID, ACCESS_TOKEN]):
    raise ValueError(
        "Missing one or more required environment variables (API_VERSION, PHONE_NUMBER_ID, ACCESS_TOKEN)"
    )

print("Environment variables loaded.")
print(f"Using API Version: {API_VERSION}")
print(f"Using Phone Number ID: {PHONE_NUMBER_ID}")

# --- Prepare API Request ---
_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/whatsapp_business_encryption"
_HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    # Content-Type is set automatically by requests when using data=dict
    # "Content-Type": "application/x-www-form-urlencoded", # Let requests handle this
}

# The data should be a dictionary. `requests` will handle urlencoding it.
# The value for 'business_public_key' is the PEM string itself.
data = {"business_public_key": public_key_pem_string}

should_send_key = input("Send key to meta? [y/n]").lower().strip() == "y"
if should_send_key:
    print(f"Sending POST request to: {_URL}")

    # --- Send API Request ---
    try:
        response = requests.post(_URL, headers=_HEADERS, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        json_response = response.json()
        print("Response from WhatsApp API:")
        print(json.dumps(json_response, indent=4))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        if e.response is not None:
            print("Error Response Status Code:", e.response.status_code)
            try:
                print("Error Response Body:", json.dumps(e.response.json(), indent=4))
            except json.JSONDecodeError:
                print("Error Response Body (non-JSON):", e.response.text)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# %% [markdown] Retrives key from DotEnv
# ### Retrives key from DotEnv
# %%
import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path.cwd().resolve().parents[1] / ".env"
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)

PUBLIC_KEY = os.getenv("PUBLIC_KEY")

print(PUBLIC_KEY)

# %% [markdown] Uploads to meta using key from DotEnv
# ### Uploads to meta using key from DotEnv
# %%
import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path.cwd().resolve().parents[1] / ".env"
print(f"Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path=dotenv_path, override=True)

API_VERSION = os.getenv("API_VERSION")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
if not all([API_VERSION, PHONE_NUMBER_ID, ACCESS_TOKEN, PUBLIC_KEY]):
    raise ValueError(
        "Missing one or more required environment variables (API_VERSION, PHONE_NUMBER_ID, ACCESS_TOKEN, PUBLIC_KEY)"
    )

print("Environment variables loaded.")
print(f"Using API Version: {API_VERSION}")
print(f"Using Phone Number ID: {PHONE_NUMBER_ID}")

# --- Prepare API Request ---
_URL = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/whatsapp_business_encryption"
_HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    # Content-Type is set automatically by requests when using data=dict
    # "Content-Type": "application/x-www-form-urlencoded", # Let requests handle this
}

# The data should be a dictionary. `requests` will handle urlencoding it.
# The value for 'business_public_key' is the PEM string itself.
data = {"business_public_key": PUBLIC_KEY}

should_send_post = input("Send public key to meta? [y/n]").lower().strip() == "y"
if should_send_post:
    print(f"Sending POST request to: {_URL}")

    try:
        response = requests.post(_URL, headers=_HEADERS, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        json_response = response.json()
        print("Response from WhatsApp API:")
        print(json.dumps(json_response, indent=4))

    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the API request: {e}")
        if e.response is not None:
            print("Error Response Status Code:", e.response.status_code)
            try:
                print("Error Response Body:", json.dumps(e.response.json(), indent=4))
            except json.JSONDecodeError:
                print("Error Response Body (non-JSON):", e.response.text)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# %% [markdown] Decrypting Request and Encrypting Response
# ### Decrypting Request and Encrypting Response
# %% [markdown] Loading Necessary Data
# #### Loading Necessary Data
# %%
from dotenv import load_dotenv
from pathlib import Path
import json
import os

dotenv_path = Path.cwd().resolve().parents[1] / ".env"

load_dotenv(dotenv_path=dotenv_path)

PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
PASSPHRASE = os.environ.get("PASSPHRASE")

if not all([PRIVATE_KEY, PASSPHRASE]):
    raise ValueError("PRIVATE_KEY or PASSPHRASE environment variable not set or empty.")

# %% [markdown] Decrypting Request
# #### Decrypting Request
# %%
from base64 import b64decode
from cryptography.hazmat.primitives.asymmetric.padding import OAEP, MGF1, hashes
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key


def decrypt_request(encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64):
    """Decrypts the incoming request data."""
    try:
        flow_data = b64decode(encrypted_flow_data_b64)
        iv = b64decode(initial_vector_b64)
        encrypted_aes_key = b64decode(encrypted_aes_key_b64)

        # Load the private key (consider loading only once if performance is critical)
        private_key = load_pem_private_key(
            PRIVATE_KEY.encode("utf-8"),
            password=PASSPHRASE,
        )

        # Decrypt the AES encryption key using RSA OAEP
        aes_key = private_key.decrypt(
            encrypted_aes_key,
            OAEP(
                mgf=MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Decrypt the Flow data using AES GCM
        # Ensure the tag length is correct (GCM default is 16 bytes)
        if len(flow_data) < 16:
            raise ValueError("Encrypted data is too short to contain a GCM tag.")
        encrypted_flow_data_body = flow_data[:-16]
        encrypted_flow_data_tag = flow_data[-16:]

        decryptor = Cipher(
            algorithms.AES(aes_key), modes.GCM(iv, encrypted_flow_data_tag)
        ).decryptor()

        decrypted_data_bytes = (
            decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
        )
        decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))

        return decrypted_data, aes_key, iv

    except ValueError as e:
        # Handle potential base64 decoding errors, data length issues, GCM tag verification errors
        print(f"Decryption Error (ValueError): {e}")
        raise  # Re-raise to be caught by the route's error handler
    except Exception as e:
        # Handle other potential errors (e.g., cryptography issues)
        print(f"Decryption Error (General Exception): {e}")
        raise  # Re-raise


# %% [makdown] Encrypting Response
# #### Encrypting Response
# %%
from base64 import b64encode
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes
import json


def encrypt_response(response_data, aes_key, iv):
    """Encrypts the outgoing response data."""
    try:
        # Flip the initialization vector bits (as required by WhatsApp Flow documentation)
        flipped_iv = bytearray()
        for byte in iv:
            flipped_iv.append(byte ^ 0xFF)

        # Encrypt the response data using AES GCM with the flipped IV
        encryptor = Cipher(
            algorithms.AES(aes_key),
            modes.GCM(bytes(flipped_iv)),  # Use bytes() to convert bytearray
        ).encryptor()

        encrypted_data = (
            encryptor.update(json.dumps(response_data).encode("utf-8"))
            + encryptor.finalize()
        )
        # The tag is appended automatically by finalize() with GCM
        encrypted_data_with_tag = encrypted_data + encryptor.tag

        # Return the result Base64 encoded
        return b64encode(encrypted_data_with_tag).decode("utf-8")

    except Exception as e:
        print(f"Encryption Error: {e}")
        raise  # Re-raise


# %% [makdown] Flask End Point
# #### Flask End Point
# %%
from flask import Flask, request, Response, jsonify

app = Flask(__name__)


@app.route("/data", methods=["POST"])
def handle_whatsapp_flow_data():
    """Handles incoming encrypted WhatsApp Flow data."""
    try:
        # Parse the request body as JSON
        # Use request.get_json() which handles content type checking and parsing
        body = request.get_json()
        if not body:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        # Read the required fields from the JSON body
        encrypted_flow_data_b64 = body.get("encrypted_flow_data")
        encrypted_aes_key_b64 = body.get("encrypted_aes_key")
        initial_vector_b64 = body.get("initial_vector")

        if not all(
            [encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64]
        ):
            return (
                jsonify({"error": "Missing required encrypted fields in JSON body"}),
                400,
            )

        # Decrypt the incoming data
        decrypted_data, aes_key, iv = decrypt_request(
            encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64
        )

        print("Decrypted Data Received:")
        print(json.dumps(decrypted_data, indent=2))  # Pretty print the decrypted data

        # --- Process the decrypted data here ---
        # Based on `decrypted_data`, determine the next screen and data
        # Example: Access data like decrypted_data['data']['user_input']
        # For this example, we'll just send a static response back

        response_payload = {
            "version": decrypted_data.get(
                "version"
            ),  # It's good practice to echo the version
            "screen": "SUCCESS_SCREEN",  # Replace with your actual next screen name
            "data": {
                "message": "Data received successfully!",
                "some_other_key": "some_value_from_server",
                # Add any data needed for the SUCCESS_SCREEN
            },
        }

        # Encrypt the response payload
        encrypted_response_b64 = encrypt_response(response_payload, aes_key, iv)

        # Return the encrypted response as plain text
        # Use Flask's Response object for full control
        return Response(encrypted_response_b64, mimetype="text/plain", status=200)

    except json.JSONDecodeError:
        print("Error: Failed to decode JSON body")
        return jsonify({"error": "Invalid JSON format"}), 400
    except KeyError as e:
        print(f"Error: Missing key in JSON request - {e}")
        return jsonify({"error": f"Missing key: {e}"}), 400
    except Exception as e:
        # Catch decryption/encryption errors or other processing errors
        print(f"Error processing request: {e}")
        # Return a generic server error response
        # Avoid leaking sensitive details in production error messages
        return jsonify({"error": "Internal server error"}), 500


should_run_endpoint = input("Run End Point? [y/n]").lower().strip() == "y"
if should_run_endpoint:
    app.run(host="0.0.0.0", port=5000)
