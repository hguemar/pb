from flask import Response

from util import publish_parts

def render(content):
    return Response(publish_parts(content), mimetype='text/html')

handlers = {
    'r': render
}

def get(handler, content):
    h = handlers.get(handler)
    if not h:
        return "Invalid handler: '{}'.".format(handler), 400
    return h(content)