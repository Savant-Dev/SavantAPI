'''
    This file contains methods to authenticate a HTTPS request

    Saved Login Credentials should be stored on the same server as API Data

    Credential Database:
        - `client-id` and `key` headers will be used to log into the auth database
        - The database will have 6 columns:
            --> Client ID
            --> Access Key (unique, primary key)
            --> Generated At
            --> Authorized By
            --> User Information
            --> Active

        - Using `client-id` as a reference point, the database will look for the active token
            --> Expired tokens will continue to be stored, but the `Active` field will be set to False
            --> Only the most recently activated token should be valid, per user

        - The most recently activated token will be returned, and compared to the `client-secret` header
        - If the database search yields no results, a "401: Unauthorized" error should be returned
        - If the search result and the provided header do not match, a "403: Forbidden" error should be returned

        - If, however, the comparison succeeds, a "202: Accepted" status should be returned
'''

import asyncpg
