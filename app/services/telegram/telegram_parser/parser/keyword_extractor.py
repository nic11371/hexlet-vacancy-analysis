from asgiref.sync import sync_to_async

from ..models import KeyWord


class KeywordExtractor:
    def __init__(self):
        self.keywords = None

    @sync_to_async
    def load_keywords(self):
        kw = KeyWord.objects.all()
        self.keywords = list(kw.values())[0]

    def matches(self, line, field):
        return any(kw in line.lower() for kw in self.keywords[field])
