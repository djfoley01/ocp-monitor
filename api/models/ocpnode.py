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

class Node(RethinkDBModel):
    _table = 'ocpnodes'

    @classmethod
    def create(cls, **kwargs):
        node = kwargs.get('Node')
        outofdisk = kwargs.get('OutOfDisk')
        mempressure = kwargs.get('MemoryPressure')
        diskpressure = kwargs.get('DiskPressure')
        ready = kwargs.get('Ready')

        doc = {
            'Node': node,
            'Status': {
                'OutOfDisk': outofdisk,
                'MemoryPressure': mempressure,
                'DiskPressure': diskpressure,
                'Ready': ready
            },
            'date_created': datetime.now(r.make_timezone('+01:00')),
            'date_modified': datetime.now(r.make_timezone('+01:00')),
        }

        print(doc)

        nodes = list(r.table(cls._table).filter({'Node': node}).run(conn))
        if len(nodes):
            raise ValidationError("Node Already Exists: {0}".format(node))

        r.table(cls._table).insert(doc).run(conn)


    @classmethod
    def get_all(cls):
        return list(r.table(cls._table).run(conn))

