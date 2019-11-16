from flask import current_app

from .tableview_blueprint import tableview_blueprint

@tableview_blueprint.route('/table/<table_ident>', methods=['DELETE'])
def delete_tableview(table_ident):
    print("DELETING", table_ident)
    # todo: delete table_ident from db
    return '', 204