from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from .utils import verify_email_with_verifalia, VerifaliaUnavailable, VerifaliaError

TEXT_EXTRA_CHARS = " -'"

def validate_email_format(value):
    value = str(value).strip().lower()

    try:
        validate_email(value)
    except DjangoValidationError:
        raise serializers.ValidationError("Enter a valid email address.")
    
    blocked_domains = ['tempmail.com', 'disposable.com']
    domain = value.split('@')[1]
    
    if domain in blocked_domains:
        # Raise DRF's ValidationError, not Django's!
        raise serializers.ValidationError("Disposable emails are not allowed.")
    
    return value

def validate_email_deliverability(value):
    try:
        result = verify_email_with_verifalia(value)
    except VerifaliaUnavailable as exc:
        raise serializers.ValidationError(
            "Email verification service is unavailable. Please try again later."
        ) from exc
    except VerifaliaError as exc:
        raise serializers.ValidationError(
            "Could not verify this email address. Please try again later."
        ) from exc

    if result["is_valid"]:
        return result.get("email", value)

    if result.get("classification") == "Undeliverable":
        raise serializers.ValidationError("This email address does not exist.")

    if result.get("classification") == "Risky":
        raise serializers.ValidationError("Please provide a more reliable email address.")

    raise serializers.ValidationError("This email address is not deliverable.")


def _normalize_text(value):
    return " ".join(str(value).strip().split())


def validate_person_name(value):
    value = _normalize_text(value)

    if not value:
        raise serializers.ValidationError("This field cannot be blank.")

    if not any(char.isalpha() for char in value):
        raise serializers.ValidationError("Enter a valid name.")

    if any(not (char.isalpha() or char in TEXT_EXTRA_CHARS) for char in value):
        raise serializers.ValidationError(
            "Name can contain letters, spaces, hyphens, and apostrophes only."
        )

    return value


def validate_meaningful_text(value, field_name="This field", allow_blank=False):
    value = _normalize_text(value)

    if not value:
        if allow_blank:
            return ""
        raise serializers.ValidationError(f"{field_name} cannot be blank.")

    if not any(char.isalnum() for char in value):
        raise serializers.ValidationError(
            f"{field_name} must contain at least one letter or number."
        )

    if any(not (char.isalnum() or char in TEXT_EXTRA_CHARS) for char in value):
        raise serializers.ValidationError(
            f"{field_name} can contain letters, numbers, spaces, hyphens, and apostrophes only."
        )

    return value