from asgiref.sync import sync_to_async

from ..models import KeyWord


class KeywordExtractor:
    def __init__(self):
        self.keywords = {
            'title': [],
            'company': [],
            'salary': [],
            'city': [],
            'schedule': [],
            'address': [],
            'experience': [],
            'description': []
        }

    @sync_to_async
    def load_keywords(self):
        for kw in KeyWord.objects.all():
            for field in self.keywords:
                value = getattr(kw, field)
                if value:
                    self.keywords[field] += [
                        v.strip().lower() for v in value.split(',')]

    def matches(self, line, field):
        return any(kw in line.lower() for kw in self.keywords[field])
