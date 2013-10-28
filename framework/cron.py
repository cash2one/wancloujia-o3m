import logging 
from django.core.management import call_command

logger = logging.getLogger(__name__)

def clear_expired_token():
    logger.debug("clear expired token")
    call_command('cleanup_remember_tokens')
