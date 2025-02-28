from typing import Dict, Any, Union
from main.models import Participant

def validate_new_message_data(data: Dict[str, Any], event, enforce_participants=True) -> Union[Dict[str, Any], Dict[str, list]]:
    errors = {}
    validated_data = {}

    # Validate subject
    subject = data.get("subject", "").strip()
    if not subject:
        errors.setdefault("subject", []).append("This field is required.")
    elif len(subject.split()) >= 100:
        errors.setdefault("subject", []).append("Must be less than 100 words.")
    else:
        validated_data["subject"] = subject

    # Validate content
    content = data.get("content", "").strip()
    if not content:
        errors.setdefault("content", []).append("This field is required.")
    else:
        validated_data["content"] = content

    if enforce_participants:
        # Validate participants
        participants = data.get("participants", [])
        if not isinstance(participants, list):
            errors.setdefault("participants", []).append("Must be a list.")
        elif not participants:
            errors.setdefault("participants", []).append("At least one participant is required.")
        else:
            print("Participants: ", participants)
            print("event: ", event)
            valid_participants = list(Participant.objects.filter(id__in=participants, evenement=event).values_list("id", flat=True))
            invalid_participants = set(participants) - set(valid_participants)
            
            if invalid_participants:
                errors.setdefault("participants", []).append(f"Invalid participant IDs: {list(invalid_participants)}")
            else:
                validated_data["participants"] = [ Participant.objects.get(id=p) for p in valid_participants ]

    return (True, validated_data) if not errors else (False, errors)
