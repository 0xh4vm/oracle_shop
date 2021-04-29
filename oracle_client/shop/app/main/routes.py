from flask import render_template, request, jsonify, redirect
from app.main import bp
from flask_jwt_extended import get_jwt_claims, jwt_optional, get_jwt_identity, get_raw_jwt
from app.database import ShopUser

from app import db, DBSession

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@jwt_optional
def index():
    current_user_id, claims = get_jwt_identity(), get_jwt_claims()

    if current_user_id is None or claims == dict():
        return render_template('main/index.html', user=None, cart=[])

    # user = ShopUser.query.get(current_user_id) if current_user_id and claims is not None else None
    user = DBSession.store[int(current_user_id)].query(ShopUser).get(current_user_id) if current_user_id and claims is not None else None

    # result = db.session.execute("SELECT USER AS username, SYS_CONTEXT('USER_CTX', 'client_identifier') AS client_identifier FROM dual")
    result = DBSession.store[user.id].execute("SELECT USER AS username, SYS_CONTEXT('USER_CTX', 'client_identifier') AS client_identifier FROM dual")
    print(*result)

    # result = db.session.execute("select * from session_roles")
    result = DBSession.store[user.id].execute("select * from session_roles")
    print(*result)

    print (DBSession.store)
    print (DBSession.store[user.id])
  
    return render_template('main/index.html', user=user, cart=user.cart_products if user.role.title == 'C##CUSTOMER' else [])

