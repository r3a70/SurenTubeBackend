from enum import Enum


class Regex(Enum):

    YOUTUBE = r'(?:https?:\/\/)?(?:www\.)?(?:m\.)?(?:youtube\.com\/' \
        r'(?:[^\/\n\s]+\/[^\/\n\s]+\/|(?:v|embed|shorts)\/|watch\?(?:' \
        r'[^&\n\s]+&)*v=|(?:[^&\n\s]+&)*youtu\.be\/)|youtu\.be\/)([^&?\/\n\s]{11})'
