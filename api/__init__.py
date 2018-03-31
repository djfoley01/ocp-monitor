from flask import Flask, Blueprint, render_template
from flask_restful import Api
from flask_cors import CORS, cross_origin

from api.controllers import auth, files, users, ocp, ocptotals, ocpnodes, ocpupdate
from config import config

import json
import os
import subprocess
import requests

from kombu import Queue
from celery import subtask
from celery import Celery, chain
from celery.utils.log import get_task_logger

from workers.find_regions.find_regions import find_regions
from workers.debug_regions.debug_regions import debug_regions
from workers.mcs_ocr.mcs_ocr import mcs_ocr
from workers.validate_address.validate_address import validate_address

logger = get_task_logger(__name__)

def create_app(env):
    app = Flask(__name__)
    app.config.from_object(config[env])
    CORS(app)
    @app.route('/ocpweb')
    def webload():
        auth_token = os.environ['OCPTOKEN']
        #auth_token = auth_token_tmp.replace(' ', '')[:-1]
        url = os.environ['OCPURL'] + "/api/v1/nodes"
        header = {"Authorization": "bearer " + auth_token}
        response = requests.get(url,headers=header,verify=False)
        if(response.ok):
                nodes = json.loads(response.content)
                output = []
                items = nodes['items']
                total = []
                for item in items:
                        total.append(item['metadata']['name'])
                        node = item['metadata']['name']
                        cpucount = item['status']['capacity']['cpu']
                        memcount = item['status']['capacity']['memory']
                        for condition in item['status']['conditions']:
                           if condition['type'] == "OutOfDisk":
                              diskstatus = condition['status']
                           if condition['type'] == "MemoryPressure":
                              memstatus = condition['status']
                           if condition['type'] == "DiskPressure":
                              diskpress = condition['status']
                           if condition['type'] == "Ready":
                              ready = condition['status']
                        output.append({'Node': node, 'Labels': item['metadata']['labels'], 'Status': {'OutOfDisk': diskstatus, 'MemoryPressure': memstatus, 'DiskPressure': diskpress, 'Ready': ready}})
                count = len(total)
                output.append({'TotalNodes': count})
        podurl = os.environ['OCPURL'] + "/api/v1/pods"
        podheader = {"Authorization": "bearer " + auth_token}
        podresponse = requests.get(podurl,headers=podheader,verify=False)
        if(podresponse.ok):
                pods = json.loads(podresponse.content)
                podoutput = []
                poditems = pods['items']
                for poditem in poditems:
                        pod = poditem['metadata']['name']
                        nodename = poditem['spec'].get('nodeName')
                        phase = poditem['status']['phase']
                        nodeselector = poditem['spec'].get('nodeSelector')
                        podoutput.append({'Pod': pod, 'Node': nodename, 'NodeSelector': nodeselector, 'Status': phase})
                return render_template('ocpweb.html', result = output, podresult = podoutput)
        else:
                return response.raise_for_status()

    # Start api/v1 Blueprint
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)

    api.add_resource(auth.AuthLogin, '/auth/login')
    api.add_resource(auth.AuthRegister, '/auth/register')
    api.add_resource(files.CreateList, '/files')
    api.add_resource(files.Upload, '/upload')
    api.add_resource(files.Download, '/download/<string:file_id>')
    api.add_resource(files.ViewEditDelete, '/files/<string:file_id>')
    api.add_resource(users.List, '/users')
    api.add_resource(ocp.OCPToken, '/ocp/token')
    api.add_resource(ocp.OCPNodes, '/ocp/active/nodes')
    api.add_resource(ocpnodes.ListNodes, '/ocp/conf/nodes')
    api.add_resource(ocpupdate.AddNode, '/ocp/add/node')
#    api.add_resource(ocp.OCPWeb, '/ocpweb')

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    # End api/v1 Blueprint

    # Celery
    celery_app = Celery('tasks', broker='pyamqp://guest@localhost//')
    celery_app.config_from_object('celeryconfig')
    celery_app.conf.update(app.config)

    return app
