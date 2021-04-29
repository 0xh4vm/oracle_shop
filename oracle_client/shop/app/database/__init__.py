from app import db, jwt, oracle_schema, views
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.dialects.oracle import RAW, NUMBER, VARCHAR2, TIMESTAMP
import sqlalchemy_views
from sqlalchemy import Table, text, DDL, event
from random import choice
import string


class View(Table):
    is_view = True

class CreateView(sqlalchemy_views.CreateView):
    def __init__(self, view):
        super().__init__(view.__view__, view.__definition__, or_replace=True)

class Role(db.Model):
    __tablename__ = "role"

    id = db.Column(NUMBER(11), db.Sequence('role_id_seq', start=1, increment=1), primary_key=True)
    title = db.Column(VARCHAR2(128), nullable=False)

class EncKey(db.Model):
    __tablename__ = "enc_key"
    __table_args__ = (db.UniqueConstraint('key', name='enc_key_uix_1'), )

    id = db.Column(NUMBER(11), db.Sequence('enc_key_id_seq', start=1, increment=1), primary_key=True)
    key = db.Column(RAW(16), nullable=False)

    def __init__(self):
        self.key = self.get_key()

    def get_key(self, length=16):
        letters = string.ascii_letters
        return ''.join(choice(letters) for i in range(length)).encode()

class ShopUserView:
    __view__ = View(
        'shop_user_view', db.MetaData(), 
        db.Column('id', NUMBER(11), db.Sequence('shop_user_id_seq', start=1, increment=1), primary_key=True),
        db.Column('first_name', VARCHAR2(128), nullable=False, default=''),
        db.Column('last_name', VARCHAR2(128), nullable=False, default=''),
        db.Column('login', VARCHAR2(128), nullable=False),
        db.Column('email', RAW(128), nullable=False),
        db.Column('password', VARCHAR2(128), nullable=False),
        db.Column('image', VARCHAR2(128)),
        db.Column('role_id', NUMBER(11), db.ForeignKey(f'{oracle_schema}.role.id', ondelete="CASCADE")),
        db.Column('enc_key_id', NUMBER(11), db.ForeignKey(f'{oracle_schema}.enc_key.id', ondelete="CASCADE")),
        implicit_returning=False
    )

    __definition__ = text("""SELECT ID, FIRST_NAME, LAST_NAME, LOGIN,
       CASE
            WHEN SYS_CONTEXT('USERENV', 'CLIENT_IDENTIFIER') = ID 
                THEN UTL_RAW.CAST_TO_VARCHAR2(
                    DBMS_CRYPTO.DECRYPT(EMAIL, 4358, 
                        (SELECT KEY FROM C##SHOP_USER.ENC_KEY 
                        WHERE ID = SYS_CONTEXT('USERENV', 'CLIENT_IDENTIFIER'))))
            WHEN SYS_CONTEXT('USERENV', 'CLIENT_IDENTIFIER') != ID THEN 'CAN NOT READ!'
       END AS EMAIL, 
       PASSWORD, IMAGE, ROLE_ID, ENC_KEY_ID
    FROM C##SHOP_USER.SHOP_USER""")

class ShopUser(db.Model):
    __tablename__ = "shop_user"

    id = db.Column(NUMBER(11), db.Sequence('shop_user_id_seq', start=1, increment=1), primary_key=True)
    first_name = db.Column(VARCHAR2(128), nullable=False, default='')
    last_name = db.Column(VARCHAR2(128), nullable=False, default='')
    # email = db.Column(VARCHAR2(128), nullable=False)
    login = db.Column(VARCHAR2(128), nullable=False)
    email = db.Column(RAW(128), nullable=False)
    password = db.Column(VARCHAR2(128), nullable=False)
    image = db.Column(VARCHAR2(128))
    role_id = db.Column(NUMBER(11), db.ForeignKey(f'{oracle_schema}.role.id', ondelete="CASCADE"))
    enc_key_id = db.Column(NUMBER(11), db.ForeignKey(f'{oracle_schema}.enc_key.id', ondelete="CASCADE"))

    role = db.relationship('Role')
    enc_key = db.relationship('EncKey')
    purchase = db.relationship('Purchase')
    # products = db.relationship('ShopProduct', backref=db.backref('seller'))

    def __init__(self, login, email, password, role_id, enc_key_id, image=None, first_name=None, last_name=None):
        self.first_name = first_name
        self.last_name = last_name
        self.login = login
        self.email = email
        self.password = generate_password_hash(password)
        self.image = image
        self.role_id = role_id
        self.enc_key_id = enc_key_id
 
    def add(self):
        db.session.execute(ShopUserView.__view__.insert().values(first_name=self.first_name, 
            last_name=self.last_name, enc_key_id=self.enc_key_id, email=self.email,
            password=self.password, role_id=self.role_id, login=self.login))
        db.session.commit()

    def update(self):
        pass
    
    def delete(self):
        pass

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def check_login(self):
        shop_user = ShopUser.query.with_entities(ShopUser.login).filter_by(login=self.login).first()
        return True if shop_user is None else False

    @staticmethod
    @jwt.user_claims_loader
    def add_claims(shop_user):
        return {
            #'email': decrypt(shop_user.email,
            'nickname': f'{shop_user.first_name} {shop_user.last_name}',
            'role': shop_user.role.title
        }

    @staticmethod
    @jwt.user_identity_loader
    def add_identity(shop_user):
        return shop_user.id

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(NUMBER(11), db.Sequence('category_id_seq', start=1, increment=1), primary_key=True)
    name = db.Column(VARCHAR2(128), nullable=False)

shop_cart = db.Table("shop_cart",
    db.Column('shop_user_id', 
        NUMBER(11), db.ForeignKey(f'{oracle_schema}.shop_user.id', ondelete="CASCADE"), 
        primary_key=True),
    db.Column('shop_product_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_product.id', ondelete="CASCADE"), 
        primary_key=True)        
)

shop_product_like = db.Table('shop_product_like',
    db.Column('shop_user_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_user.id', ondelete="CASCADE"), 
        primary_key=True),
    db.Column('shop_product_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_product.id', ondelete="CASCADE"), 
        primary_key=True)
)

shop_product_dislike = db.Table('shop_product_dislike',
    db.Column('shop_user_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_user.id', ondelete="CASCADE"), 
        primary_key=True),
    db.Column('shop_product_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_product.id', ondelete="CASCADE"), 
        primary_key=True)
)

shop_product_category = db.Table('shop_product_category',
    db.Column('shop_product_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_product.id', ondelete="CASCADE"), 
        primary_key=True),
    db.Column('category_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.category.id', ondelete="CASCADE"), 
        primary_key=True)
)

shop_product_seller = db.Table('shop_product_seller',
    db.Column('shop_product_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_product.id', ondelete="CASCADE"), 
        primary_key=True),
    db.Column('shop_user_id', NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_user.id', ondelete="CASCADE"), 
        primary_key=True)
)

class ShopProduct(db.Model):
    __tablename__ = "shop_product"
    __table_args__ = (db.CheckConstraint('cost > 200', name='cost_check_1'),)

    id = db.Column(NUMBER(11), db.Sequence('shop_product_id_seq', start=1, increment=1), primary_key=True)
    title = db.Column(VARCHAR2(128), nullable=False)
    author = db.Column(VARCHAR2(128), nullable=False)
    description = db.Column(VARCHAR2(1024), nullable=False, default='')
    date_of_creation = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    cost = db.Column(NUMBER(6), nullable=False)
    image = db.Column(VARCHAR2(128))
    count_products = db.Column(db.Integer, nullable=False, default=1)
    # seller_id = db.Column(NUMBER(11), db.ForeignKey(f'{oracle_schema}.shop_user.id', ondelete="CASCADE"))

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    categories = db.relationship('Category', secondary=shop_product_category, 
        backref=db.backref('products'))
    likes = db.relationship('ShopUser', secondary=shop_product_like, 
        backref=db.backref('likes_products'))
    dislikes = db.relationship('ShopUser', secondary=shop_product_dislike, 
        backref=db.backref('dislikes_products'))
    shop_cart = db.relationship('ShopUser', secondary=shop_cart, 
        backref=db.backref('cart_products'))
    sellers = db.relationship('ShopUser', secondary=shop_product_seller, 
        backref=db.backref('products'))
    # seller = db.relationship('ShopUser')

class Purchase(db.Model):
    __tablename__ = "purchase"

    shop_user_id = db.Column(NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_user.id', ondelete="CASCADE"), 
        primary_key=True)
    shop_product_id = db.Column(NUMBER(11), 
        db.ForeignKey(f'{oracle_schema}.shop_product.id'), 
        primary_key=True)    
    count = db.Column(NUMBER(3), nullable=False, default=1)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
