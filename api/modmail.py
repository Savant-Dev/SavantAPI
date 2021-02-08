import json
import typing as t

from .utils import *

from quart import Blueprint
from quart import request
from quart import jsonify
from quart import make_response

from asyncpg import Connection


api = Blueprint('mail_api', __name__)

@api.before_request
async def before_invoke():
    for name in ['part', 'id', 'key']:
        value = request.args.get(name, None)

        if not value:
            error = raise_error(400, f'Missing Required Argument: {name}')

            return await make_response(jsonify(error), error['code'])

@api.route('/inbox/case', methods=['GET', ])
@authentication_required
@connected
async def fetch_case(db: Connection) -> dict:
    part = request.args.get('part')
    case_id = int(request.args.get('id'))

    if part == 'report':
        query = 'SELECT "Case Report" FROM "Modmail Logs" WHERE "Case ID" = $1'
    else:
        query = 'SELECT * FROM "Modmail Logs" WHERE "Case ID" = $1'

    data = await db.fetch(query, case_id)

    items = Converters.query_items(data)
    if not items:
        items = ['No Records found matching your Query Parameters']

    response = Converters.response('GET', 'inbox#case', request.args, items)

    return await make_response(jsonify(response), 200)

@api.route('/inbox/case', methods=['POST', ])
@authentication_required
@connected
async def new_case(db: Connection) -> dict:
    part = request.args.get('part')
    id = request.args.get('id')

    if part == 'id':
        query = (
            'INSERT INTO "Modmail Logs" ("Guild ID", "User ID") '
            'VALUES ($1, $2) RETURNING "Case ID"'
        )
        try:
            args = (
                int(request.args.get('guild')),
                int(request.args.get('user'))
            )
        except KeyError:
            error = raise_error(400, 'Missing Required Arguments: guild, user')

            return await make_response(jsonify(error), error['code'])

        else:
            data = await db.fetch(query, *args)

            items = Converters.query_items(data)
            if not items:
                items = ['No Records found matching your Query Parameters']
            response = Converters.response('POST', 'inbox#case', request.args, items)

            return await make_response(jsonify(response), 200)
    else:
        error = raise_error(405, 'Invalid Request Method for <part="id">')

        return await make_response(jsonify(error), 405)

@api.route('/inbox/case/', methods=['PUT', ])
@authentication_required
@connected
async def close_case(db: Connection) -> dict:
    part = request.args.get('part')
    id = request.args.get('id')

    if part == 'report':
        query = (
            'UPDATE "Modmail Logs" SET "Case Report" = $1 '
            'WHERE "Case ID" = $2 RETURNING *'
        )
        args = (json.dumps(await request.get_json()), int(id))
        data = await db.fetch(query, *args)

        items = Converters.query_items(data)
        if not items:
            items = ['No Records found matching your Query Parameters']

        response = Converters.response('UPDATE', 'inbox#case', request.args, items)

        return await make_response(jsonify(response), 200)

    else:
        error = raise_error(405, 'Invalid Request Method for <part="report">')

        return await make_response(jsonify(error), error['code'])
