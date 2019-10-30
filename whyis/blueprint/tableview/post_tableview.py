import json
from flask import current_app, request

from .tableview_blueprint import tableview_blueprint

@tableview_blueprint.route("/table/<table_ident>", methods=['POST'])
def post_tableview(table_ident):
    print("POSTING", table_ident)
    data = str(request.data, 'utf-8')
    print(json.loads(data))
    return "TEST"