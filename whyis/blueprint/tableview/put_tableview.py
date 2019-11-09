from flask import current_app, request

from .tableview_blueprint import tableview_blueprint

@tableview_blueprint.route('/table/<table_ident>', methods=['PUT'])
def put_tableview(table_ident):
    print("PUTING", table_ident)
    data = str(request.data, 'utf-8')
    # todo: handle request on server
    return "", 201