from quart import Quart

from . import security


def load(app: Quart) -> Quart:
    app.register_blueprint(security.api, url_prefix='/auth/')

    return app
