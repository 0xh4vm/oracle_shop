from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.database import *
# from app.database.plsql import PlSql
from random import choice
import string


def add_keys():
    keys = [EncKey() for k in range(5)]

    db.session.add_all(keys)
    db.session.commit()
    return keys

def add_users(roles, keys):
    seller1 = ShopUser(first_name="Alex", last_name="Seller", enc_key_id=keys[0].id,
        email="seller@gmail.com".encode(), password="123", role_id=roles[0].id, 
        login="seller")
    seller1.add()
    seller2 = ShopUser(first_name="Alex", last_name="Seller2",  enc_key_id=keys[1].id,
        email="seller2@gmail.com".encode(), password="123", role_id=roles[0].id, 
        login="seller2")
    seller2.add()
    
    customer1 = ShopUser(first_name="Alex", last_name="Customer",  enc_key_id=keys[2].id,
        email="customer@gmail.com".encode(), password="123", role_id=roles[1].id, 
        login="customer")
    customer1.add()
    customer2 = ShopUser(first_name="Alex", last_name="Customer2",  enc_key_id=keys[3].id,
        email="customer2@gmail.com".encode(), password="123", role_id=roles[1].id, 
        login="customer2")
    customer2.add()

    manager = ShopUser(first_name="Alex", last_name="Manager",  enc_key_id=keys[4].id,
        email="manager@gmail.com".encode(), password="123", role_id=roles[2].id, 
        login="manager")
    manager.add()

    return seller1, seller2, customer1, customer2, manager

def add_roles():
    seller = Role(title="C##SELLER")
    customer = Role(title="C##CUSTOMER")
    manager = Role(title="C##MANAGER")

    db.session.add_all([seller, customer, manager])
    db.session.commit()

    return seller, customer, manager

# def add_role_associate(users, roles):
#     users[0].roles.append(roles[0])
#     users[1].roles.append(roles[0])

#     users[2].roles.append(roles[1])
#     users[3].roles.append(roles[1])

#     users[4].roles.append(roles[2])

#     return users

def add_shop_products(sellers):
    products = [
        # ShopProduct(title="Антихрупкость", author="Насим Николас Талеб",  
        #     description="Голос Талеба - голос философа и пророка. К нему нельзя не прислушиваться. Его идеи настолько мощны, оригинальны и правдивы, что их одних достаточно, чтобы изменить наше понимание структуры мира.",
        #     image='img/antifragile.png', seller_id=sellers[0].id, cost=1200),
        # ShopProduct(title="Черный лебедь", author="Насим Николас Талеб",  
        #     description="Голос Талеба - голос философа и пророка. К нему нельзя не прислушиваться. Его идеи настолько мощны, оригинальны и правдивы, что их одних достаточно, чтобы изменить наше понимание структуры мира.",
        #     image='img/blck_swan.jpg', seller_id=sellers[0].id, cost=1100),
        # ShopProduct(title="ХАКИНГ: искусство эксплойта", author="Джон Эриксон",  
        #     description="Мир без хакеров - это мир без любопытства и новаторских решений.",
        #     image='img/hacking.png', seller_id=sellers[1].id, cost=1900),
        ShopProduct(title="Антихрупкость", author="Насим Николас Талеб",  
            description="Голос Талеба - голос философа и пророка. К нему нельзя не прислушиваться. Его идеи настолько мощны, оригинальны и правдивы, что их одних достаточно, чтобы изменить наше понимание структуры мира.",
            image='img/antifragile.png', cost=1200, count_products=1),
        ShopProduct(title="Черный лебедь", author="Насим Николас Талеб",  
            description="Голос Талеба - голос философа и пророка. К нему нельзя не прислушиваться. Его идеи настолько мощны, оригинальны и правдивы, что их одних достаточно, чтобы изменить наше понимание структуры мира.",
            image='img/blck_swan.jpg',  cost=1100, count_products=2),
        ShopProduct(title="ХАКИНГ: искусство эксплойта", author="Джон Эриксон",  
            description="Мир без хакеров - это мир без любопытства и новаторских решений.",
            image='img/hacking.png',  cost=1900, count_products=3),
    ]

    products[0].sellers.append(sellers[0])
    products[0].sellers.append(sellers[1])
    products[1].sellers.append(sellers[0])
    products[2].sellers.append(sellers[1])
    return products


def add_category():
    db.session.add_all([
        Category(name="Философия"), Category(name="Технологии"), 
        Category(name="Программирование"), Category(name="Культура")
    ])
    db.session.commit()

def add_shop_product_categories(shop_products, categories):
    shop_products[0].categories.append(categories[0])
    shop_products[0].categories.append(categories[3])
    shop_products[1].categories.append(categories[0])
    shop_products[1].categories.append(categories[3])
    shop_products[2].categories.append(categories[1])
    shop_products[2].categories.append(categories[2])

    return shop_products

def add_product_likes(customers, shop_products):
    shop_products[0].likes.append(customers[0])
    shop_products[2].likes.append(customers[0])

    shop_products[1].likes.append(customers[1])
    shop_products[2].likes.append(customers[1])
    return shop_products

def add_product_dislikes(customers, shop_products):
    shop_products[0].dislikes.append(customers[1])
    shop_products[1].dislikes.append(customers[0])
    return shop_products

def add_purchase(customers, products):
    db.session.add_all([
        Purchase(shop_user_id=customers[0].id, shop_product_id=products[0].id, count=2),
        Purchase(shop_user_id=customers[0].id, shop_product_id=products[2].id, count=3),
        Purchase(shop_user_id=customers[1].id, shop_product_id=products[1].id, count=1),
    ])
    db.session.commit()


def initialization():
    add_roles()
    
    roles = Role.query.all()

    keys = add_keys()
    add_users(roles, keys)

    users = ShopUser.query.all()

    # 

    # users = add_role_associate(users, roles)

    products = add_shop_products([users[0], users[1]])

    customers = [users[2], users[3]]

    products = add_product_likes(customers, products)
    products = add_product_dislikes(customers,products)
    
    add_category()

    categories = Category.query.all()
    products = add_shop_product_categories(products, categories)
    
    #TODO
    for product in products:
        c = db.session.object_session(product)
        c.add(product)
        c.commit()

    add_purchase(customers, products)

if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config)
    # plsql = PlSql()

    db = SQLAlchemy(app)
    # db.session.execute(CreateView(ShopUserView))

    with app.app_context():
        initialization()