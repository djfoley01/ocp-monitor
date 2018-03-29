
from api.models.ocpnode import Node
from flask_restful import abort, Resource, fields, marshal_with

status_serializer = {
    'OutOfDisk': fields.String,
    'MemoryPressure': fields.String,
    'DiskPressure': fields.String,
    'Ready': fields.String
}

node_serializer = {
    'id': fields.String,
    'Node': fields.String,
    'Status': fields.Nested(status_serializer),
    'date_created': fields.DateTime(dt_format='rfc822'),
    'date_modified': fields.DateTime(dt_format='rfc822')
}

class ListNodes(Resource):

    @marshal_with(node_serializer)
    def get(self):
        try:
            return Node.get_all()
        except Exception as e:
            abort(400, message="Error getting all nodes -> {0}".format(e))
