import re
from rest_framework.serializers import ValidationError

YOUTUBE_DOMAINS = ['youtube.com', 'youtu.be']

class NoExternalLinksValidator:
    def __call__(self, attrs):
        url_pattern = re.compile(r'https?://[^\s)]+')
        errors = {}

        for field_name, value in attrs.items():
            if isinstance(value, str):
                links = url_pattern.findall(value)
                for link in links:
                    if not any(domain in link for domain in YOUTUBE_DOMAINS):
                        errors[field_name] = f'Поле содержит ссылку на запрещенный ресурс: {link}'

        if errors:
            raise ValidationError(errors)
