from flask import Blueprint,render_template
from flask import request
from flask.json import jsonify
import constants
import json
import requests
from helper import helper

list_runtime = Blueprint("list_runtime",__name__)
utilObject=helper.Helper()
@list_runtime.route('')
def list_project_runtime():
    period_start, period_end = utilObject.getOneHour()
    url = constants.FLASK_APP_URL + '/list_runtime/' + period_start + '/'+ period_end
    headers=utilObject.getRequestHeader()
    r = requests.get(url, headers=headers, verify=False)
    input_json = r.text
    input_dict = json.loads(input_json)
    list_key_value = _countNumberOfHours(input_dict)
    return jsonify(list_key_value)

@list_runtime.route('/<period_start>/<period_end>')
def list_project_runtime_search(period_start, period_end):
    url = constants.METERING_ROUTE_LIST_ALL_PROJECTS
    headers = utilObject.getRequestHeader()
    r = requests.get(url, headers=headers, verify=False)
    input_json = r.text
    input_dict = json.loads(input_json)
    output_dict = [x for x in input_dict if x['period_start'] >= period_start]
    data = [x for x in output_dict if x['period_end'] <= period_end]
    list_key_value = _countNumberOfHours(data)
    return jsonify(list_key_value)

def _countNumberOfHours(input_dict):
    ht=dict()
    for x in input_dict:
        if x['namespace'] in ht:
            ht[x['namespace']] += 1
        else:
            ht[x['namespace']] = 1 
    list_key_value = [ dict(namespace=k, activation_time=v) for k, v in ht.items() ]
    return list_key_value