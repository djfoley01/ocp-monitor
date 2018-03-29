
from api.models.ocptotal import TotalConfNode
from flask_restful import abort, Resource, fields, marshal_with

totalnodes_serializer = {
    'totalnodes': fields.String,
    'date_created': fields.DateTime(dt_format='rfc822'),
    'date_modified': fields.DateTime(dt_format='rfc822')
}

class TotalConfNodes(Resource):

    @marshal_with(totalnodes_serializer)
    def get(self):
        try:
            return TotalConfNode.get_all()
        except Exception as e:
            abort(400, message="Error getting total nodes -> {0}".format(e))
