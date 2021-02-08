import json
import typing as t

from .utils import *

from quart import request
from quart import jsonify
from quart import Response
from quart import Blueprint
from quart import make_response

query_map = {
    'all': '*',
    'case': '"Case ID"',
    'report': '"Case Report"',
    'snippet': '"Case ID", "User ID", "Case Report"',
    'initial': '"User ID", "Guild ID", "Case Report"'
}

schema = {
    'id': '"Case ID"',
    'user': '"User ID"',
    'guild': '"Guild ID"',
    'report': '"Case Report"'
}


api = Blueprint('mail_api', __name__)

@api.before_request
async def before_invoke():
    for name in ['part', 'key']:
        value = request.args.get(name, None)

        if not value:
            error = raise_error(400, f'Missing Required Argument: {name}')

            return await make_response(jsonify(error), error['code'])

@api.route('/inbox/case', methods=['GET', ])
@authenticated
@requires_data
async def fetch_case(db: Connection) -> Response:
    part = request.args.get('part')
    params = request.headers['parameters']

    try:
        filter = query_map[part.lower()]
        if part.lower() == 'initial':
            raise KeyError
    except KeyError:
        error = raise_error(400, f'Invalid Request Parameter: <part={part}>')

        return await make_response(jsonify(error), error['code'])

    filter, args = Converters.sql_filter(schema, parameters=params)

    query = f'SELECT {part} FROM "Modmail Logs" {query}'

    data = await db.fetch(query, *args)
    items = Converters.query_items(data)

    response = Converters.response('GET', 'inbox#case', params, items)

    return await make_response(jsonify(response), 200)

@api.route('/inbox/case', methods='POST')
@authenticated
@requires_data
async def new_case(db: Connection) -> Response:
    part = request.args.get('part')
    params = request.headers['parameters']

    try:
        filter = query_map[part.lower()]
        if part != 'initial':
            raise KeyError
    except KeyError:
