from uuid import UUID
from mimetypes import guess_type

from flask import Blueprint, Response, request, render_template, current_app, url_for
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_all_lexers

from db import cursor
from paste import model
from util import highlight, redirect, request_content, id_url, b64_id, id_b64

paste = Blueprint('paste', __name__)

@paste.route('/')
def index():
    return Response(render_template("index.html"), mimetype='text/html')

@paste.route('/f')
def form():
    return Response(render_template("form.html"), mimetype='text/html')

@paste.route('/', methods=['POST'])
@cursor
def post():
    content, filename = request_content()
    if not content:
        return "Nope.\n", 400

    id, uuid = model.get_digest(content)
    if not id:
        id, uuid = model.insert(content)

    url = id_url(b64=id_b64(id, filename=filename))
    uuid = UUID(bytes=uuid) if uuid else '[redacted]'
    return redirect(url, "{}\nuuid: {}\n".format(url, uuid))

@paste.route('/<uuid>', methods=['PUT'])
@cursor
def put(uuid):
    content, filename = request_content()
    if not content:
        return "Nope.\n", 400

    uuid = UUID(uuid).bytes

    id, _ = model.get_digest(content)
    if id:
        url = id_url(b64=id_b64(id))
        return redirect(url, "Paste already exists.\n", 409)

    id = model.put(uuid, content)
    if id:
        url = id_url(b64=id_b64(id, filename=filename))
        return redirect(url, "{} updated.\n".format(url), 200)

    return "Not found.\n", 404

@paste.route('/<uuid>', methods=['DELETE'])
@cursor
def delete(uuid):
    uuid = UUID(uuid).bytes
    id = model.delete(uuid)
    if id:
        url = id_url(b64=id_b64(id))
        return redirect(url, "{} deleted.\n".format(url), 200)
    return "Not found.\n", 404

@paste.route('/<string(length=4):b64>')
@paste.route('/<string(length=4):b64>/<lexer>')
@cursor
def get(b64, lexer=None):
    id = b64_id(b64)
    if not id:
        return "Invalid id.\n", 400

    mimetype, _ = guess_type(b64)

    content = model.get_content(id)
    if not content:
        return "Not found.\n", 404

    if lexer:
        return highlight(content, lexer)
    elif mimetype:
        return Response(content, mimetype=mimetype)

    return content

@paste.route('/s')
@cursor
def stats():
    count, length = model.get_stats()
    return "{} pastes\n{} bytes\n".format(count, length)

@paste.route('/static/highlight.css')
def highlight_css():
    css = HtmlFormatter().get_style_defs('.highlight')
    return Response(css, mimetype='text/css')

@paste.route('/l')
def list_lexers():
    lexers = '\n'.join(' '.join(i) for _, i, _, _ in get_all_lexers())
    return '{}\n'.format(lexers)