import json
import asyncpg
import functools

import typing as t

from quart import jsonify
from quart import request
from quart import make_response

from .security import UserAuthentication
from .security import TokenAuthentication


def raise_error(status: int, message: str) -> dict:
    status = {
        'code': status,
        'error': message
    }

    return status

def authentication_required(func: t.Callable) -> t.Callable:
    @functools.wraps(func)
    async def verify(*args, **kwargs):
        error = None
        user = UserAuthentication.get_user(request)

        if not user:
            error = raise_error(*UserAuthentication.missing)

        key = request.args.get('key', None)
        if not key:
            error = raise_error(*TokenAuthentication.missing)

        if not error:
            auth = TokenAuthentication()
            await auth.fetch_key(user)

            status = auth.verify(key)
            if not status:
                error = raise_error(*TokenAuthentication.invalid)

        if error:
            return await make_response(jsonify(error), error['code'])

        return await func(*args, **kwargs)

    return verify

def connected(func: t.Callable = None, *, database: str='Application Data'):
    if not func:
        return functools.partial(connected, database=database)

    @functools.wraps(func)
    async def connect(*args, **kwargs):
        error = None
        user = UserAuthentication.get_user(request)

        if not user:
            error = raise_error(*UserAuthentication.missing)

        try:
            conn = await asyncpg.connect(
                host = '192.168.1.74',
                port = 5432,
                database = database,

                user = user['client-id'],
                password = user['client-secret']
            )
        except Exception as e:
            error = raise_error(*UserAuthentication.invalid)
            error.update(
                {'debug': str(e)}
            )

        if error:
            return await make_response(jsonify(error), error['code'])

        return await func(conn, *args, **kwargs)

    return connect


class Converters():

    @staticmethod
    def query_items(records: t.List[asyncpg.Record]) -> t.List:
        items = []

        for record in records:
            data = {}

            for field, value in record.items():
                if isinstance(value, str):
                    if any(char in value for char in ['{', '}', '[', ']']):
                        try:
                            value = json.loads(value)
                        except JSONDecodeError:
                            pass

                data[field] = value

            items.append(data)

        return items

    @staticmethod
    def response(method: str, url: str, args: dict, items: list) -> dict:
        params = {key: value for key, value in args.items() if key != 'key'}

        data = {
            "code": 200,
            "error": "None",
            "fields"
                "kind": method,
                "method": url,
                "parameters": params
            },

            "items": items
        }

        return data

    @staticmethod
    def sql_filter(map: dict, *, parameters: dict) -> t.Tuple[str, list]
        temp = []
        position = 1
        conditions = []

        for parameter, value in params.items():
            try:
                qualified = map[parameter.lower()]
            except KeyError:
                continue
            else:
                conditions.append(f'WHERE {qualified} = ${position}')
                values.append(value)
                position += 1

        query = ' AND '.join(conditions)

        return query, values
