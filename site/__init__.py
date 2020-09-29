from quart import Quart

from . import auth
from . import data


app = Quart(__name__)

app = auth.load(app)
app = data.load(app)

from . import routes
