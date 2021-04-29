from flask import jsonify, render_template, request
from app import db, socketio, DBSession
from app.product import bp
from app.database import ShopProduct, ShopUser, Purchase
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import SocketIO
from itertools import chain
from datetime import datetime


@bp.route('/', methods=['GET'])
@jwt_required
def product_view():
    current_user_id = get_jwt_identity()
    per_page, user = 20, DBSession.store[current_user_id].query(ShopUser).get(current_user_id)
    page = request.args.get('page', 1, type=int)

    # products = ShopProduct.query.order_by(ShopProduct.date_of_creation.desc())\
    #     .paginate(page, per_page)
    
    # purchase = {item.shop_product_id: item.count for item in Purchase.query.all()}
    products = DBSession.store[current_user_id].query(ShopProduct).order_by(ShopProduct.date_of_creation.desc()).all()
    
    purchase = {item.shop_product_id: item.count for item in DBSession.store[current_user_id].query(Purchase).all()}

    return render_template('product/index.html', user=user, products=products, 
        cart=user.cart_products if user.role.title == 'C##CUSTOMER' else [], purchase=purchase)

@socketio.on('like')
@jwt_required
def like(data):
    current_user_id = get_jwt_identity()
    user = DBSession.store[current_user_id].query(ShopUser).get(current_user_id)
    socketio = SocketIO(message_queue="redis://")

    try:
        print(data['product_id'])
        product = DBSession.store[current_user_id].query(ShopProduct).get(data['product_id'])

        if user in product.likes:
            product.likes.remove(user)
            active = False
        else:
            product.likes.append(user)
            active = True

        # db.session.commit()
        DBSession.store[current_user_id].commit()

        socketio.emit("get_count_like", {
            "count": len(product.likes),
            "product_id": product.id,
        })

        socketio.emit("get_state_like", {
            "status": "success",
            "product_id": product.id,
            "active": active
        }, room=request.sid)

    except:

        socketio.emit("get_state_like", {
            "status": "fail",
            "text": f'Не получилось лайкнуть товар {product.title}.',
        }, room=request.sid)

@socketio.on('dislike')
@jwt_required
def dislike(data):
    current_user_id = get_jwt_identity()
    user = DBSession.store[current_user_id].query(ShopUser).get(current_user_id)
    socketio = SocketIO(message_queue="redis://")

    try:
        product = DBSession.store[current_user_id].query(ShopProduct).get(data['product_id'])

        if user in product.dislikes:
            product.dislikes.remove(user)
            active = False
        else:
            product.dislikes.append(user)
            active = True

        # db.session.commit()
        DBSession.store[current_user_id].commit()

        socketio.emit("get_count_dislike", {
            "count": len(product.dislikes),
            "product_id": product.id,
        })

        socketio.emit("get_state_dislike", {
            "status": "success",
            "product_id": product.id,
            "active": active
        }, room=request.sid)

    except:
        socketio.emit("get_state_dislike", {
            "status": "fail",
            "text": f'Не получилось дизлайкнуть товар {product.title}.',
        }, room=request.sid)

@bp.route('/to_cart/', methods=['POST'])
@jwt_required
def to_cart():    
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    current_user_id = get_jwt_identity()
    user = DBSession.store[current_user_id].query(ShopUser).get(current_user_id)
    try:
        product_id = int(request.json['product_id'])
        product = DBSession.store[current_user_id].query(ShopProduct).get(product_id)
        
        if str(product.date_of_creation) != str(request.json['version']):
            return jsonify({'status': 'fail', 'text': f'Данные товара {product.title} были изменены автором. Обновите страницу, чтобы увидеть обновленую версию.'})
            
        if product in user.cart_products:
            user.cart_products.remove(product)
            active = False
        else:
            user.cart_products.append(product)
            active = True

        DBSession.store[current_user_id].commit()
        print('len(user.cart_products)', len(user.cart_products))
        return jsonify({'status': 'success', 
            'text': f'Товар {product.title} успешно {"добавлен в корзину." if active else "удален из корзины."}',
            'active': active,  'count_cart': len(user.cart_products),
            'product':product.as_dict()})
    except:
        return jsonify({'status': 'fail', 'text': f'Не получилось добавить в корзину товар {product.title}.'})

@bp.route('/remove/', methods=['POST'])
@jwt_required
def remove():
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    current_user_id = get_jwt_identity()
    try:
        product_id = int(request.json['product_id'])
        product = DBSession.store[current_user_id].query(ShopProduct).get(product_id)
        DBSession.store[current_user_id].delete(product)
        DBSession.store[current_user_id].commit()

        return jsonify({'status': 'success', 'text': f'Товар {product.title} был успешно удален.'})
    except:
        return jsonify({'status': 'fail', 'text': f'Не получилось удалить товар {product.title}.'})

@bp.route('/lock_edit/', methods=['POST'])
@jwt_required
def lock_edit():
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    current_user_id = get_jwt_identity()
    try:
        product_id = int(request.json['product_id'])
        product = DBSession.store[current_user_id].query(ShopProduct).with_entities(ShopProduct).with_for_update(
            nowait=True,
            of=[ShopProduct.id, ShopProduct.title, ShopProduct.author, ShopProduct.description, 
                ShopProduct.date_of_creation, ShopProduct.cost]
        ).filter(ShopProduct.id == product_id).first()

        return jsonify({'product': {
                'id': product.id, 
                'title': product.title, 
                'author': product.author, 
                'description':product.description,
                'cost': product.cost
            }})
    except:
        return jsonify({'status': 'fail', 'text': f'Кажется какой-то негодяй заблокировал данные и ушел пить кофе.'})

@bp.route('/unlock/', methods=['POST'])
@jwt_required
def unlock():
    current_user_id = get_jwt_identity()
    try:
        DBSession.store[current_user_id].rollback()
        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'fail', 'text': f'Что-то пошло не так...'})
  

@bp.route('/edit/', methods=['POST'])
@jwt_required
def edit():
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    current_user_id = get_jwt_identity()
    try:
        product_id = int(request.json['product_id'])
        
        if len(request.json['new_title']) > 0 and len(request.json['new_author']) > 0 and \
            len(request.json['new_description']) > 0 and int(request.json['new_cost']) > 0:

            product = DBSession.store[current_user_id].query(ShopProduct).with_for_update(
                nowait=True, 
                of=[ShopProduct.id, ShopProduct.title, ShopProduct.author, ShopProduct.description, 
                    ShopProduct.date_of_creation, ShopProduct.cost]
            ).get(product_id)
            
            product.title = request.json['new_title']
            product.author = request.json['new_author']
            product.description = request.json['new_description']
            product.cost = int(request.json['new_cost'])
            product.date_of_creation = datetime.utcnow()
            
            DBSession.store[current_user_id].commit()
        else:
            return jsonify({'status': 'fail', 
                'text': f'Не получилось обновить товар {product.title}. Введите корректные значения.'})

        return jsonify({'status': 'success', 'text': f'Товар {product.title} был успешно обновлен.'})
    except:
        return jsonify({'status': 'fail', 'text': f'Не получилось обновить товар {product.title}.'})

@bp.route('/buy/', methods=['POST'])
@jwt_required
def buy():
    if not request.is_json:
        return jsonify({'status': 'fail', 'text': 'Что-то пошло не так...'})

    current_user_id = get_jwt_identity()
    try:
        user = DBSession.store[current_user_id].query(ShopUser).get(current_user_id)

        for item in user.cart_products:
            if str(item.date_of_creation) != str(request.json[f'{item.id}']['version']):
                return jsonify({'status': 'fail', 
                    'text': f'Данные товара {item.title} были изменены. Обновите страницу, чтобы увидеть обновленую версию.'})

            if (item.count_products == 0):
                return jsonify({'status': 'fail', 
                    'text': f'Товара {item.title} не осталось, попробуйте сделать заказ позднее либо удалите его из корзины.'})

            op = DBSession.store[current_user_id].query(Purchase).get((user.id, item.id,))
            if op is None:
                p = Purchase(shop_user_id=user.id, shop_product_id=item.id, count=1)
                DBSession.store[current_user_id].add(p)
            else:
                op.count += 1

            item.count_products -= 1

        user.cart_products = []
        DBSession.store[current_user_id].commit()



        return jsonify({'status': 'success', 'text': f'Спасибо за покупки, будем ждать вас снова!'})
    except:
        return jsonify({'status': 'fail', 'text': f'Не получилось совершить покупки.'})
