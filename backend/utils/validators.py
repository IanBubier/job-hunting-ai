import re
from typing import Dict, Tuple, Optional


def validate_search_request(data: Dict) -> Tuple[bool, Optional[Dict]]:
    """Validate search request data.

    Returns: (is_valid, error_dict)
    """
    errors: Dict[str, str] = {}

    if not isinstance(data, dict):
        return False, {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid payload',
            'details': {'payload': 'Request body must be a JSON object'}
        }

    # Validate skills
    skills = data.get('skills', [])
    if not isinstance(skills, list):
        errors['skills'] = 'Skills must be an array'
    elif len(skills) == 0:
        errors['skills'] = 'At least one skill is required'
    elif len(skills) > 20:
        errors['skills'] = 'Maximum 20 skills allowed'
    else:
        skill_pattern = re.compile(r"^[a-zA-Z0-9\s\+\#\.\-]{2,50}$")
        for skill in skills:
            if not isinstance(skill, str):
                errors['skills'] = 'All skills must be strings'
                break
            if len(skill) < 2 or len(skill) > 50:
                errors['skills'] = 'Skills must be 2-50 characters'
                break
            if not skill_pattern.match(skill):
                errors['skills'] = 'Skills contain invalid characters'
                break

    # Validate keywords
    keywords = data.get('keywords', '')
    if not isinstance(keywords, str):
        errors['keywords'] = 'Keywords must be a string'
    elif keywords and len(keywords) < 3:
        errors['keywords'] = 'Keywords must be at least 3 characters'
    elif len(keywords) > 200:
        errors['keywords'] = 'Keywords must be less than 200 characters'

    # Validate location
    location = data.get('location', '')
    if not isinstance(location, str):
        errors['location'] = 'Location must be a string'
    elif location and len(location) < 2:
        errors['location'] = 'Location must be at least 2 characters'
    elif len(location) > 100:
        errors['location'] = 'Location must be less than 100 characters'

    # Validate experience
    experience = data.get('experience', 'entry')
    valid_levels = ['entry', 'mid', 'senior']
    if experience not in valid_levels:
        errors['experience'] = (
            'Experience must be one of: ' + ', '.join(valid_levels)
        )

    # Validate max_results
    max_results = data.get('max_results', 20)
    if not isinstance(max_results, int):
        errors['max_results'] = 'max_results must be an integer'
    elif max_results < 1 or max_results > 50:
        errors['max_results'] = 'max_results must be between 1 and 50'

    if errors:
        return False, {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid input',
            'details': errors
        }

    return True, None


def sanitize_input(text: str) -> str:
    """Remove potentially dangerous characters and tags from input."""
    if not isinstance(text, str):
        return text

    # Remove script tags first
    text = re.sub(
        r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove any remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Trim whitespace
    return text.strip()
