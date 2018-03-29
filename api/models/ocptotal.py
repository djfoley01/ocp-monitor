import os
import re

import rethinkdb as r
from jose import jwt
from jose.exceptions import JWTError
from datetime import datetime
from passlib.hash import pbkdf2_sha256

from flask import current_app

from api.utils.errors import ValidationError, DatabaseProcessError, UnavailableContentError

from api.models.RethinkDBModel import RethinkDBModel

conn = r.connect(db='papers')

class TotalConfNode(RethinkDBModel):
    _table = 'totalnodes'

    @classmethod
    def create(cls, **kwargs):
        totalnodes = kwargs.get('totalnodes')

        doc = {
            'totalnodes': totalnodes,
            'date_created': datetime.now(r.make_timezone('+01:00')),
            'date_modified': datetime.now(r.make_timezone('+01:00')),
        }

        print(doc)

        r.table(cls._table).insert(doc).run(conn)


    @classmethod
    def get_all(cls):
        return list(r.table(cls._table).run(conn))

