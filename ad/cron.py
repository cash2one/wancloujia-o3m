import logging 
from django.core.management import call_command

logger = logging.getLogger(__name__)

def update_index():
    logger.debug("update index")
    call_command('update_index')
