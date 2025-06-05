import app.users.exceptions as custom_ex
import json


def read_data_from_request(request):
    if request.content_type != "application/json":
        raise custom_ex.ValidationError(
            message="Expected application/json",
            code=415)
    try:
        data = json.loads(request.body)
        return data
    except json.JSONDecodeError:
        raise custom_ex.ValidationError(message="Invalid JSON", code=400)
