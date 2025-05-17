from .models import *


sidebar = [{'button': 'Spots', 'url_button': 'home'},
           {'button': 'Fish', 'url_button': 'fish'},
           {'button': 'Baits', 'url_button': 'baits'},
           {'button': 'Query tool', 'url_button': 'query_tool'}]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['sidebar'] = sidebar
        return context
