import json
from flask import current_app, request, Response, make_response, jsonify
from flask_login import login_required

from .tableview_blueprint import tableview_blueprint

data = [
    {"id":1,"name":"Billy Bob","age":"12","col":"red","dob":""},
    {"id":2,"name":"Mary May","age":"1","col":"blue","dob":"14/05/1982"},
    {"id":3,"name":"Christine Lobowski","age":"42","height":0,"col":"green","dob":"22/05/1982","cheese":"true"},
    {"id":4,"name":"Brendon Philips","age":"125","gender":"male","height":1,"col":"orange","dob":"01/08/1980"},
    {"id":5,"name":"Margret Marmajuke","age":"16","gender":"female","height":5,"col":"yellow","dob":"31/01/1999"},
    {"id":6,"name":"Billy Bob","age":"12","gender":"male","height":1,"col":"red","dob":"","cheese":1},
    {"id":7,"name":"Mary May","age":"1","gender":"female","height":2,"col":"blue","dob":"14/05/1982","cheese":True},
    {"id":8,"name":"Christine Lobowski","age":"42","height":0,"col":"green","dob":"22/05/1982","cheese":"true"},
    {"id":9,"name":"Brendon Philips","age":"125","gender":"male","height":1,"col":"orange","dob":"01/08/1980"},
    {"id":10,"name":"Margret Marmajuke","age":"16","gender":"female","height":5,"col":"yellow","dob":"31/01/1999"}
]

@tableview_blueprint.route('/table/<table_ident>', methods=['GET'])
def get_tableview(table_ident):
    print("GETTING", table_ident)
    # todo: retrieve from db
    if table_ident == "test_table":
       return jsonify(data)
    return make_response("", 404)
