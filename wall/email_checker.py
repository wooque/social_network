import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError
import logging

logger = logging.getLogger()


def check_email(email):
    """
        Uses emailhunter.io for verification
        API at: https://hunter.io/api/docs
    """
    if not settings.CHECK_EMAIL:
        return True

    resp = requests.get('https://api.hunter.io/v2/email-verifier',
                        params=dict(email=email, api_key=settings.EMAILHUNTER_API_KEY))

    if resp.status_code != 200:
        logger.error("Email check error: status: {}, error: {}".format(resp.status_code, resp.text))
        raise ValidationError("Invalid email")

    return resp.json()['data']['result'] in ['deliverable', 'risky']
