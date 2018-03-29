from flask_restful import reqparse, abort, Resource

from api.models.ocpnode import Node

class AddNode(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Node', type=str, help='Node Name', required=True)
        parser.add_argument('OutOfDisk', type=str, help='Out Of Disk Status', required=True)
        parser.add_argument('MemoryPressure', type=str, help='Memory Pressure Status', required=True)
        parser.add_argument('DiskPressure', type=str, help='Disk Pressure Status', required=True)

        parser.add_argument('Ready', type=str, help='Node Status')

        args = parser.parse_args()

        node = args.get('Node')
        outofdisk = args.get('OutOfDisk')
        mempressure = args.get('MemoryPressure')
        diskpressure = args.get('DiskPressure')
        ready = args.get('Ready')

        try:
            Node.create(
                Node=node,
                OutOfDisk=outofdisk,
                MemoryPressure=mempressure,
                DiskPressure=diskpressure,
                Ready=ready,
            )
            return {'message': 'Successfully created Node.'}
        except ValidationError as e:
            abort(400, message="There was an error while trying to create Node -> {0}".format(e))
