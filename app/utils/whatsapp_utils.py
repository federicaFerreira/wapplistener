import logging
from flask import current_app, jsonify
import json
import requests
from app.controllers.whatsapp_controller import Whatsapp
from app.controllers.gsheet_controller import GoogleSheet
from datetime import date
from app.services.openai_service import generate_response,update_openai_file
import re


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):

    contact_wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    contact_name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # solo respondo si somos martin o yo
    if(contact_wa_id not in [current_app.config["WHATSAPP_MARTIN"], current_app.config["WHATSAPP_FEDE"]]):
        return ""
    
    wa = Whatsapp()
    # wa.add_contact(contact_wa_id, contact_name)
    process = wa.process_message(message_body)

    if not process:
        # OpenAI Integration
        response = generate_response(message_body, contact_wa_id, contact_name)
        response = process_text_for_whatsapp(response)
    else:

        if wa.type == 'UPDATE_DATA':
            google = GoogleSheet()
            google.create_pdf_from_spreadsheet()
            update_openai_file()
            response = "Listo!"

        if wa.type == 'BUDGET_PAYMENT_LINK':
            google = GoogleSheet()
            response = google.get_budget_payment_link_message(wa.type_params["budget_code"], wa.type_params["amount"], wa.type_params["currency"])

        if wa.type == 'PROVIDER_PAYMENT_LINK':
            google = GoogleSheet()
            response = google.get_provider_payment_link_message(wa.type_params["provider_code"], wa.type_params["amount"], wa.type_params["currency"])

        if wa.type == 'RECONCILE_PAYMENT':
            google = GoogleSheet()
            response = google.reconcile_payment(wa.type_params["budget_code"], wa.type_params["amount"], wa.type_params["currency"])

        if wa.type == 'PAYMENT':
            google = GoogleSheet()
            response = google.add_payment(wa.type_params["provider_code"], wa.type_params["amount"], wa.type_params["currency"])

        if wa.type == 'PROVIDERS':
            google = GoogleSheet()
            response = google.get_providers()

        if wa.type == 'BUDGETS':
            google = GoogleSheet()
            response = google.get_budgets()

    data = get_text_message_input("+"+contact_wa_id, response)
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

