import subprocess
import json
#import random
#import string
#import base64
import os
import re

from jose import jwt
from jose.exceptions import JWTError

from kombu import Queue
from celery import subtask
from celery.utils import uuid
from celery import Celery, chain
from celery.utils.log import get_task_logger

#from workers.find_regions.find_regions import find_regions
#from workers.debug_regions.debug_regions import debug_regions
#from workers.mcs_ocr.mcs_ocr import mcs_ocr
#from workers.validate_address.validate_address import validate_address

from flask import current_app, request, g, send_from_directory, render_template
from flask_restful import reqparse, abort, Resource, fields, marshal_with
#from werkzeug import secure_filename
import requests

#from api.models.file import File
#from api.models.folder import Folder
from api.utils.decorators import login_required, validate_user, ocp_valid

logger = get_task_logger(__name__)

def get_token():
    token = subprocess.Popen(["/app/scripts/get_os_token.x"], stdout=subprocess.PIPE).communicate()[0]
    return token

class OCPToken(Resource):
    @ocp_valid
    def get(self):
        try:
            token = subprocess.Popen(["/app/scripts/get_os_token.x"], stdout=subprocess.PIPE).communicate()[0]
            #output = {'token': token}
            #output_json = json.dumps(output)
            d = {}
            d['token'] = token.decode("utf-8").rstrip()
            #output_json = json.loads(d)
            final = json.dumps(d)
            return final
            #return output_json
        except Exception as e:
            abort(500, message="There was an error retrieving ocp token --> {0}".format(e))

class OCPNodes(Resource):
     def get(self):
        auth_token = subprocess.Popen(["/app/scripts/get_os_token.x"], stdout=subprocess.PIPE).communicate()[0]
        #auth_token = auth_token_tmp.replace(' ', '')[:-1]
        url = 'https://devosmlb.saccap.int:8443/api/v1/nodes'
        header = {"Authorization": "bearer " + auth_token.decode("utf-8").rstrip()}
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
                return output
        else:
                return response.raise_for_status()

class OCPWeb(Resource):
     def get(self):
        auth_token = subprocess.Popen(["/app/scripts/get_os_token.x"], stdout=subprocess.PIPE).communicate()[0]
        #auth_token = auth_token_tmp.replace(' ', '')[:-1]
        url = 'https://devosmlb.saccap.int:8443/api/v1/nodes'
        header = {"Authorization": "bearer " + auth_token.decode("utf-8").rstrip()}
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
                        output.append({'Node': node, 'Status': {'OutOfDisk': diskstatus, 'MemoryPressure': memstatus, 'DiskPressure': diskpress, 'Ready': ready}})
                count = len(total)
                output.append({'TotalNodes': count})
                return render_template('ocpweb.html', result = output)
        else:
                return response.raise_for_status()
