import hashlib
import re
import json
import requests
import email
import os
import gradio as gr

# Define available categories and sub request types
REQUEST_TYPES = [
    "Adjustment", "AU Trasfer", "Closing Notice", "Commitment Change",
    "Fee Payment", "Money Movement Inbound", "Money Movement Outbound"
]
SUB_REQUEST_TYPES = {
    "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
    "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement Inbound": ["Principal", "Interest", "Principal+Interest", "Principal+Interest+Fee"],
    "Money Movement Outbound": ["Timebound", "Foreign Currency"]
}

# --- Duplicate Detection ---
email_hash_set = set()

def compute_email_hash(email_text: str) -> str:
    """Compute a unique SHA-256 hash for the email content."""
    return hashlib.sha256(email_text.encode("utf-8")).hexdigest()

def is_duplicate(email_text: str) -> (bool, str):
    """Check if an email is a duplicate based on its hash."""
    email_hash = compute_email_hash(email_text)
    if email_hash in email_hash_set:
        return True, f"Duplicate email detected (hash: {email_hash})."
    else:
        email_hash_set.add(email_hash)
        return False, ""

# --- OpenRouter DeepSeek API Call with Three-Line Parsing ---
def call_openrouter_deepseek(email_text: str) -> dict:
    """
    Call the OpenRouter DeepSeek R1 API to classify the email.
    The API is instructed to return the result on three lines:
      - First line: Primary Request Type.
      - Second line: Sub Request Type (if applicable; if not, leave blank).
      - Third line: Confidence: <decimal number between 0 and 1>.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        # "HTTP-Referer": "<YOUR_SITE_URL>",
        # "X-Title": "<YOUR_SITE_NAME>"
    }

    messages = [
        {
            "role": "user",
            "content": (
                "Analyze the following email and determine the primary request type from the predefined categories: "
                f"{', '.join(REQUEST_TYPES)}. Email text: {email_text}\n"
                "Return the result on three lines:\n"
                "First line: Primary Request Type\n"
                "Second line: Sub Request Type (if applicable; if not, leave blank).\n"
                "Third line: Confidence: <decimal number between 0 and 1>."
            )
        }
    ]

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": messages
    }

    response = requests.post(url=url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        result = response.json()
        response_text = result.get("choices", [{}])[0].get("message", {}).get("content", "Unknown")
        # Split the response by newline to separate the three expected lines.
        lines = [line.strip() for line in response_text.strip().split("\n") if line.strip()]

        primary_request = lines[0] if len(lines) > 0 else "Unknown"
        sub_request = lines[1] if len(lines) > 1 and lines[1] != "" else None

        # Validate the sub request: if provided, it must be in the allowed list for the primary.
        if sub_request and primary_request in SUB_REQUEST_TYPES:
            if sub_request not in SUB_REQUEST_TYPES[primary_request]:
                sub_request = None
        else:
            sub_request = None

        # Parse the third line for confidence.
        confidence = None
        if len(lines) > 2:
            match = re.search(r"Confidence:\s*([\d\.]+)", lines[2])
            if match:
                try:
                    confidence = float(match.group(1))
                except ValueError:
                    confidence = None
        return {
            "primary_request": primary_request,
            "sub_request": sub_request,
            "confidence": confidence,
            "details": "DeepSeek R1 analysis confirms the classification."
        }
    else:
        return {
            "primary_request": "Error",
            "sub_request": None,
            "confidence": 0.0,
            "details": f"Error calling DeepSeek API: {response.status_code} {response.text}"
        }

# --- Field Extraction ---
def extract_fields(email_text: str) -> dict:
    """
    Extract configurable fields from the email text using regex.
    For demonstration, extracts deal name, amount, and expiration date.
    """
    fields = {}
    deal_match = re.search(r"Deal:\s*([\w\s\-]+)", email_text)
    fields["deal_name"] = deal_match.group(1).strip() if deal_match else None

    amount_match = re.search(r"\$\s*([\d,]+(?:\.\d{2})?)", email_text)
    fields["amount"] = amount_match.group(1) if amount_match else None

    date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", email_text)
    fields["expiration_date"] = date_match.group(1) if date_match else None

    return fields

# --- End-to-End Email Processing ---
def process_email(email_text: str, attachments: list = None) -> dict:
    """
    Process an email by performing:
      1. Duplicate detection.
      2. Classification using DeepSeek.
      3. Field extraction from email text and attachments.
    """
    # Step 1: Duplicate Detection
    duplicate_flag, duplicate_reason = is_duplicate(email_text)

    # Step 2: Classification using DeepSeek API
    deepseek_result = call_openrouter_deepseek(email_text)

    # Step 3: Field Extraction from the email text
    extracted_fields = extract_fields(email_text)

    # Process attachments (if any) using the same extraction logic.
    attachment_results = []
    if attachments:
        for attachment in attachments:
            attachment_fields = extract_fields(attachment)
            attachment_results.append(attachment_fields)

    # Assemble the final structured output
    output = {
        "duplicate": duplicate_flag,
        "duplicate_reason": duplicate_reason,
        "classification": deepseek_result,
        "extracted_fields": extracted_fields,
        "attachments_extracted_fields": attachment_results,
    }
    return output

# --- File Upload Handling for .eml and .msg Files ---
def process_email_file(file_path: str) -> dict:
    """
    Process an email file (.eml or .msg) by extracting its text content and then processing it.
    For .eml files, uses Python's built-in email module.
    For .msg files, uses the 'extract_msg' library (install via pip if needed).
    """
    ext = os.path.splitext(file_path)[1].lower()
    email_text = ""
    
    if ext == ".eml":
        with open(file_path, "r", encoding="utf-8") as f:
            msg = email.message_from_file(f)
            if msg.is_multipart():
                parts = []
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        charset = part.get_content_charset() or "utf-8"
                        parts.append(part.get_payload(decode=True).decode(charset, errors="ignore"))
                email_text = "\n".join(parts)
            else:
                charset = msg.get_content_charset() or "utf-8"
                email_text = msg.get_payload(decode=True).decode(charset, errors="ignore")
    elif ext == ".msg":
        try:
            import extract_msg
        except ImportError:
            raise ImportError("Please install the 'extract_msg' library to process .msg files (pip install extract_msg).")
        msg = extract_msg.Message(file_path)
        email_text = msg.body
    else:
        raise ValueError("Unsupported file type. Only .eml and .msg files are supported.")
    
    return process_email(email_text)

# --- Gradio UI Implementation ---
def gradio_process_email(file_obj):
    """
    Gradio wrapper function to process an uploaded email file.
    The uploaded file is passed as a file object; its name attribute is used to determine the extension.
    """
    if file_obj is None:
        return "No file uploaded."
    # file_obj.name is the temporary file path provided by Gradio.
    try:
        result = process_email_file(file_obj.name)
        return json.dumps(result, indent=4)
    except Exception as e:
        return f"Error processing file: {str(e)}"

# Create the Gradio interface for file upload.
iface = gr.Interface(
    fn=gradio_process_email,
    inputs=gr.File(label="Upload Email File (.eml or .msg)"),
    outputs="text",
    title="Email Processing",
    description="Upload a .eml or .msg file to extract classification and fields from the email."
)

if __name__ == "__main__":
    iface.launch()
