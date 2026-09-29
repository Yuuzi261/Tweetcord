import os

ENABLE_FILE_LOG: bool = os.getenv('ENABLE_FILE_LOGGING', 'true').lower() in ('true', '1', 't', 'y', 'yes')

AUTOCOMPLETE_MAX_CHOICES: int = 25
AUTOCOMPLETE_MAX_CHOICE_LENGTH: int = 100