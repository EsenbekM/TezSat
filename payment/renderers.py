import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = data.get('non_field_errors', None)
        if not response:
            response = [data]
        return json.dumps({
            **response[0]
        })
