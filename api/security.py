import uuid
import asyncpg
import secrets
import hashlib

import typing as t

from quart import request
from quart import jsonify
from quart import Blueprint
from quart import make_response


class TokenAuthentication():

    def __init__(self):
        self.valid: str = None

    missing = (401, 'Missing Required URL Parameter: key')
    invalid = (401, 'Invalid Request Authorization Token')


    def verify(self, key: str) -> bool:
        encrypted = hashlib.sha256(key.encode('UTF-8'))
        comparable = encrypted.hexdigest()

        return comparable == self.valid

    @classmethod
    def generate_user(cls) -> int:
        unique = uuid.uuid4()

        return unique.hex

    @classmethod
    def generate_secret(cls) -> int:
        return secrets.token_hex(12)

    @classmethod
    def generate_key(cls) -> t.Tuple[str, int]:
        decrypted = secrets.token_urlsafe(24)

        encrypted = hashlib.sha256(decrypted.encode('UTF-8'))
        storable = encrypted.hexdigest()

        return decrypted, storable

    async def fetch_key(self, user: dict) -> None:
        try:
            conn = await asyncpg.connect(
                host = '192.168.1.74',
                port = 5432,
                database = 'Authentication',

                user = user['client-id'],
                password = user['client-secret']
            )
        except Exception as e:
            return False

        query = (
                ' SELECT * FROM "Registration" '
                ' WHERE "Application ID" = $1 AND "Status" = $2'
                )

        data = await conn.fetchrow(query, user['client-id'], True)
        await conn.close()

        if not data:
            return False

        self.valid = data['Access Key']


class UserAuthentication():

    missing = (401, 'Missing Required Request Headers')

    invalid = (401, 'Invalid Request Authorization Credentials')

    @staticmethod
    def get_user(request: request) -> dict:
        try:
            user = {
                'client-id': request.headers['client-id'],
                'client-secret': request.headers['client-secret']
            }
        except KeyError as e:
            return False

        return user
