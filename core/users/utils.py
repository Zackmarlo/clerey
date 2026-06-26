import requests
from django.conf import settings


class VerifaliaError(Exception):
    pass

class VerifaliaUnavailable(VerifaliaError):
    pass

def _first_entry(snapshot):
    entries = snapshot.get("entries") or {}
    data = entries.get("data") or []
    return data[0] if data else None

def verify_email_with_verifalia(email_address):
    """
    Submits an email to Verifalia for real-time verification.
    Returns a dictionary with the validation status.
    """
    url = "https://api.verifalia.com/v2.7/email-validations"
    
    payload = {
        "entries": [
            {
            "inputData": email_address
            }
        ],
        "quality": "Standard",
        "deduplication": "Off"
    }
    
    try:
        response = requests.post(
            url,
            auth=(settings.VERIFALIA_USERNAME, settings.VERIFALIA_PASSWORD),
            json=payload,
            timeout=30, # Always set a timeout for external API calls
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
            },
            params={"waitTime": 30000}
        )
        
        data = response.json() if response.content else {}

        # Raise an exception for bad HTTP status codes (e.g., 401 Unauthorized)
        response.raise_for_status()
        
        # we need to extract the first entry to get the validation results
        entry = _first_entry(data)
        if not entry:
            raise RuntimeError("Verifalia returned no email validation entry.")
        
        # Extract the classification (e.g., Deliverable, Undeliverable, Risky) and status (e.g., Success, Failed)
        classification = entry.get('classification')
        status = entry.get("status")

        return {
            "email": entry.get("emailAddress") or email_address,
            "is_valid": classification == "Deliverable" and status == "Success",
            "classification": classification,
            "status": status,
            "raw": entry,
        }
        
    except requests.exceptions.Timeout as e:
        raise VerifaliaUnavailable("Email verification timed out.") from e

    except requests.exceptions.ConnectionError as e:
        raise VerifaliaUnavailable("Email verification service is unavailable.") from e

    except requests.exceptions.RequestException as e:
        raise VerifaliaError("Email verification request failed.") from e

    except (ValueError, RuntimeError, KeyError, IndexError) as e:
        raise VerifaliaError("Invalid response from email verification service.") from e