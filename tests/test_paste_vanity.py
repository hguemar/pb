from time import time
from yaml import load

from flask import url_for

from pb.pb import create_app

def test_paste_vanity():
    app = create_app()

    c = str(time())
    rv = app.test_client().post('/foo123', data=dict(
        c = c
    ))
    location = rv.headers.get('Location')
    assert 'foo123' in location
    data = load(rv.get_data())

    rv = app.test_client().get(location)
    assert rv.status_code == 200
    assert rv.get_data() == c.encode('utf-8')

    with app.test_request_context():
        url = url_for('paste.put', uuid=data.get('uuid'))
    
    rv = app.test_client().put(url, data=dict(
        c = str(time())
    ))
    assert rv.status_code == 200

    rv = app.test_client().delete(url)
    assert rv.status_code == 200

