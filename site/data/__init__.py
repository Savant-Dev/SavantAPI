from quart import Quart

from . import tags
from . import events
from . import modmail
from . import creators
from . import leveling
from . import infractions


def load(app: Quart) -> Quart:
    blueprints = [
        (tags.api, 'tags'),
        (modmail.api, 'mail'),
        (events.api, 'events'),
        (leveling.api, 'levels'),
        (creators.api, 'creators'),
        (infractions.api, 'actions')
    ]

    for blueprint, name in blueprints:
        app.register_blueprint(blueprint, url_prefix=f'/api/{name}')

    return app
