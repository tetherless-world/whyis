import json
from flask import current_app, make_response, request, Response

from whyis.blueprint.tableview.tableview_blueprint import tableview_blueprint

@tableview_blueprint.route("/table/<table_ident>", methods=['POST'])
@tableview_blueprint.route('/table', methods=['POST'])
def post_tableview(table_ident=None):
    print("POSTING", table_ident)
    data = str(request.data, 'utf-8')
    # todo: save data to server
    return make_response("TEST", 204)