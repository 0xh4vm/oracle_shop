from flask import render_template, jsonify, request, redirect, make_response, current_app
from app import db, jwt, socketio, db_session, DBSession #, avatar, sid_rooms
from app.auth import bp
from flask_jwt_extended import (create_access_token, get_jwt_identity, jwt_optional, \
                                jwt_required, get_jwt_claims, unset_jwt_cookies, set_access_cookies)
from app.database import ShopUser, Role,EncKey
from werkzeug.security import generate_password_hash
from os import remove
from flask_socketio import join_room, leave_room
from sqlalchemy.orm import sessionmaker, scoped_session

from sqlalchemy import create_engine
from config import Config


@socketio.on("join")
def on_join(message):
    join_room(message['room'])

@socketio.on("leave")
def on_leave(message):
    leave_room(message['room'])

@bp.route('/', methods=["GET"])
@jwt_optional
def auth_view():
    current_user_id, user = get_jwt_identity(), None

    if current_user_id is not None:
        user = ShopUser.query.get(current_user_id)
        return redirect('/', code=302)

    db.session.execute("SET ROLE NONE")
    return render_template('auth/index.html', user=user, cart=user.cart_products if user is not None and user.role.title == 'C##CUSTOMER' else [])

@bp.route('/account/', methods=['GET'])
@jwt_required
def account_view():
    current_user_id = get_jwt_identity()
    user = ShopUser.query.get(current_user_id)

    return render_template('auth/account.html', user=user, cart=user.cart_products if user is not None and user.role.title == 'C##CUSTOMER' else [])

@bp.route('/account/change_settings/', methods=['POST'])
@jwt_required
def account_change_settings():
    data, current_user_id = request.form, get_jwt_identity()
    user = ShopUser.query.get(current_user_id)
    response = redirect('/auth/account/', code=302)

    data = request.form

    if not data.get('account_email') or not data.get('account_nickname'):
        return jsonify({'status': 'fail', 'text': "Поля 'Email' и 'Логин' должны быть заполнены."})

    user.email = data.get('account_email')
    user.nickname = data.get('account_nickname')
    user.first_name = data.get('account_first_name')
    user.last_name = data.get('account_last_name')

    # if 'avatar' in request.files:
    #     user.image = avatar.save(request.files.get('avatar'), name=f'avatar_{user.id}.jpg')

    # if data.get('remove_avatar'):
    #     remove(f'app/static/users/avatar/avatar_{user.id}.jpg')
    #     user.image = None

    if data.get('account_current_password') and data.get('account_new_password') \
            and user.check_password(data.get('account_current_password')):
        user.password = generate_password_hash(data.get('account_new_password'))

    if data.get('account_del_current_password') and user.check_password(data.get('account_del_current_password')):
        db.session.delete(user)
        unset_jwt_cookies(response)

    db.session.commit()
    return response

@bp.route('/sign_in/', methods=["POST"])
def sign_in():
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    data = request.json

    if not data['login'] or not data['password']:
        return jsonify({'status': 'fail', 'text': "Заполните форму полностью"})

    user = ShopUser.query.with_entities(ShopUser).filter(ShopUser.login == data['login']).first()
    
    role_name = data['select_role'].upper()
    role = Role.query.with_entities(Role).filter_by(title=f'C##{role_name}').first()

    if role.id != user.role_id:
        return jsonify({'status': 'fail', 'text': "К сожалению вы пока еще не обладаете данной ролью. Вам необходимо при регистрации указать необходимую роль."})

    if user is None or not user.check_password(data['password']):
        return jsonify({'status': 'fail', 'text': "Введены неверные данные"})

    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    # DBSession.store[user.id] = db.create_scoped_session(options=dict(bind=db.get_engine(current_app._get_current_object()), binds={}))
    DBSession.store[user.id] = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))()
    DBSession.store[user.id].execute(f"SELECT C##SHOP_USER.USER_CTX_API.INIT_USER_CTX({int(user.id)}) FROM DUAL")

    result = DBSession.store[user.id].execute("SELECT USER AS username, SYS_CONTEXT('USER_CTX', 'client_identifier') AS client_identifier FROM dual")
    print(*result)

    DBSession.store[user.id].execute(f"SET ROLE {role.title}")

    access_token = create_access_token(identity=user)
    response = make_response(redirect('/', code=302))

    set_access_cookies(response, access_token)

    return response

@bp.route('/sign_up/', methods=["POST"])
def sign_up():
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    data = request.json

    if not data['first_name'] or not data['last_name'] or not data['email'] or not data['password'] or not data['login']:
        return jsonify({'status': 'fail', 'text': "Заполните форму полностью"})

    if data['password'] != data['confirm_password']:
        return jsonify({'status': 'fail', 'text': "Пароли не совпадают"})

    role_name = data['select_role'].upper()
    role = Role.query.with_entities(Role).filter_by(title=f'C##{role_name}').first()
    
    key = EncKey()
    db.session.add(key)
    
    user = ShopUser(first_name=data['first_name'], last_name=data['last_name'],\
                email=data['email'], login=data['login'], password=data['password'], \
                role_id=role.id, enc_key_id=key.id)

    if not user.check_login():
        return jsonify({'status': 'fail', 'text': "Пользователь на данную почту уже зарегистрирован"})

    # db.session.add(user)
    # db.session.commit()
    user.add()

    access_token = create_access_token(identity=user)
    response = make_response(redirect('/', code=302))

    set_access_cookies(response, access_token)
    
    DBSession.store[user.id].execute(f"SELECT C##SHOP_USER.USER_CTX_API.INIT_USER_CTX({int(user.id)}) FROM DUAL")
    DBSession.store[user.id].execute(f"SET ROLE {role.title}")

    return response

@jwt.unauthorized_loader
def unauthorized_loader(code):
    return redirect('/', code=302)

@jwt.invalid_token_loader
def invalid_token_loader():
    current_user_id = int(get_jwt_identity())
    response = make_response(redirect('/auth/', code=302))
    unset_jwt_cookies(response)
    DBSession.store[current_user_id].execute(f"SELECT C##SHOP_USER.USER_CTX_API.CLOSE_USER_CTX FROM DUAL")
    # DBSession.store[current_user_id].remove()
    return response

@jwt.expired_token_loader
def expired_token_loader():
    current_user_id = int(get_jwt_identity())
    response = make_response(redirect('/auth/', code=302))
    unset_jwt_cookies(response)
    DBSession.store[current_user_id].execute(f"SELECT C##SHOP_USER.USER_CTX_API.CLOSE_USER_CTX FROM DUAL")
    # DBSession.store[current_user_id].remove()
    return response

@bp.route('/refresh/', methods=['POST'])
@jwt_required
def refresh():
    current_user_id = get_jwt_identity()
    user = ShopUser.query.get(current_user_id)

    access_token = create_access_token(identity=user)
    response = redirect('/', code=302)

    set_access_cookies(response, access_token)

    return response

@bp.route('/logout/', methods=['GET'])
@jwt_required
def logout():
    response = redirect('/auth/', code=302)
    unset_jwt_cookies(response)
    current_user_id = int(get_jwt_identity())
    
    if current_user_id and current_user_id in DBSession.store:
        result = DBSession.store[current_user_id].execute(f"SELECT C##SHOP_USER.USER_CTX_API.CLOSE_USER_CTX FROM DUAL")
        print(*result)

        # result = db.session.execute(f"SELECT C##SHOP_USER.set_role('NONE') FROM DUAL")
        # print(*result)

        DBSession.store[current_user_id].execute("SET ROLE NONE")
        # result = db.session.execute("select * from session_roles")
        # print(*result)
        # DBSession.store[current_user_id].remove()


    return response

@bp.route('/reset_password/', methods=["POST"])
def reset_password():
    pass
