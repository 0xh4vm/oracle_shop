# from app import db
# from sqlalchemy import DDL, event
# from app.database import *
# from sqlalchemy.orm import mapper


# class PlSql():
#     def __init__(self):
#         set_identifier_user = DDL("""CREATE OR REPLACE FUNCTION set_identifier_user(
#             p_user_id IN NUMBER
#         )
#             RETURN VARCHAR2
#         IS
#             l_return_val VARCHAR2(2000);
#         BEGIN
#             DBMS_SESSION.set_identifier(p_user_id);
#             SELECT SYS_CONTEXT('userenv', 'client_identifier') AS client_identifier INTO l_return_val FROM dual;
#             RETURN l_return_val;
#         END""")

#         clear_identifier_user = DDL("""CREATE OR REPLACE FUNCTION clear_identifier_user
#             RETURN VARCHAR2
#         IS
#             l_return_val VARCHAR2(2000);
#         BEGIN
#             DBMS_SESSION.clear_identifier;
#             SELECT SYS_CONTEXT('userenv', 'client_identifier') AS client_identifier INTO l_return_val FROM dual;
#             RETURN l_return_val;
#         END""")

#         shop_product_func = DDL("""CREATE OR REPLACE FUNCTION shop_product_func (
#         p_schema_name   IN   VARCHAR2,
#         p_object_name   IN   VARCHAR2
#         )
#         RETURN VARCHAR2
#         IS
#             l_role_active   VARCHAR2 (2000);
#             l_user_id       VARCHAR2 (2000);
#             l_return_val    VARCHAR2 (2000);
#         BEGIN
#             l_return_val := '1 = 1';
#             SELECT SYS_CONTEXT('userenv','client_identifier') INTO l_user_id FROM DUAL;
#             SELECT ROLE.TITLE INTO l_role_active FROM ROLE, SHOP_USER
#                 WHERE ROLE.ID = SHOP_USER.ROLE_ID 
#                 AND SHOP_USER.ID = l_user_id;
            
#             IF (l_role_active = 'C##SELLER')
#             THEN 
#                 l_return_val := 'SELLER_ID = ' || l_user_id;
#             END IF;

#             RETURN l_return_val;
#         END shop_product_func""")

#         purchase_func = DDL("""CREATE OR REPLACE FUNCTION purchase_func (
#         p_schema_name   IN   VARCHAR2,
#         p_object_name   IN   VARCHAR2
#         )
#         RETURN VARCHAR2
#         IS
#             l_role_active   VARCHAR2 (2000);
#             l_user_id       VARCHAR2 (2000);
#             l_return_val    VARCHAR2 (2000);
#         BEGIN
#             SELECT SYS_CONTEXT('userenv','client_identifier') INTO l_user_id FROM DUAL;
#             SELECT ROLE.TITLE INTO l_role_active FROM ROLE, SHOP_USER
#                 WHERE ROLE.ID = SHOP_USER.ROLE_ID 
#                 AND SHOP_USER.ID = l_user_id;

#             SELECT CASE l_role_active
#                 WHEN 'C##CUSTOMER' THEN  'SHOP_USER_ID = ' || l_user_id
#                 WHEN 'C##SELLER' THEN 'SHOP_PRODUCT_ID IN (SELECT ID FROM SHOP_PRODUCT WHERE SELLER_ID = '|| l_user_id ||')'
#                 ELSE '1 = 1'
#             END INTO l_return_val FROM DUAL;

#             RETURN l_return_val;
#         END purchase_func""")

#         select_count_shop_product_func = DDL("""CREATE OR REPLACE FUNCTION select_count_shop_product_func 
#         RETURN VARCHAR2
#         IS
#             l_start_time    TIMESTAMP;
#             l_end_time      TIMESTAMP;
#             l_count         VARCHAR2 (2000);
#             l_return_val    VARCHAR2 (2000);
#         BEGIN
#             l_start_time := systimestamp;

#             SELECT COUNT(*) INTO l_count FROM C##SHOP_USER.SHOP_PRODUCT WHERE COST > '200';

#             l_end_time := systimestamp;
#             l_return_val := '' || (l_end_time - l_start_time);
#             RETURN l_return_val;
#         END select_count_shop_product_func""")

#         insert_shop_product_func = DDL("""CREATE OR REPLACE FUNCTION insert_shop_product_func (
#             p_title IN   VARCHAR2,
#             p_author IN   VARCHAR2,
#             p_description IN   VARCHAR2, 
#             p_cost IN NUMBER
#         )
#         RETURN VARCHAR2
#         IS
#             l_start_time    TIMESTAMP;
#             l_end_time      TIMESTAMP;
#             l_user_id       VARCHAR2 (2000);
#             l_return_val    VARCHAR2 (2000);
#             PRAGMA AUTONOMOUS_TRANSACTION;
#         BEGIN
#             SELECT SYS_CONTEXT('userenv','client_identifier') INTO l_user_id FROM DUAL;
            
#             l_start_time := systimestamp;

#             INSERT INTO C##SHOP_USER.SHOP_PRODUCT (id, title, author, description, date_of_creation, 
#                 cost, image, seller_id) VALUES (c##shop_user.shop_product_id_seq.nextval, p_title, p_author, 
#                 p_description, '29-NOV-20', p_cost, '', l_user_id);

#             l_end_time := systimestamp;
#             COMMIT;

#             l_return_val := '' || (l_end_time - l_start_time);
#             RETURN l_return_val;

#             EXCEPTION WHEN OTHERS
#             THEN
#             ROLLBACK;
#             RETURN '';
#         END insert_shop_product_func""")

#         t_delete_cascade_purchase = DDL("""CREATE OR REPLACE TRIGGER delete_cascade_purchase
#         BEFORE DELETE
#             ON C##SHOP_USER.SHOP_PRODUCT
#             REFERENCING OLD AS OLD
#             FOR EACH ROW
#         BEGIN
#             DELETE FROM C##SHOP_USER.PURCHASE WHERE SHOP_PRODUCT_ID = :OLD.ID;
#         END""")
#         event.listen(ShopProduct, 'init', t_delete_cascade_purchase.execute_if(dialect='oracle'), once=True)

#         t_insert_into_shop_user = DDL("""CREATE OR REPLACE TRIGGER INSERT_INTO_SHOP_USER 
#             INSTEAD OF INSERT ON C##SHOP_USER.SHOP_USER_VIEW
#             FOR EACH ROW
#         DECLARE 
#             l_encrypted_email RAW(2000);
#             l_enc_key RAW(2000);
#         BEGIN
#             SELECT KEY INTO l_enc_key FROM C##SHOP_USER.ENC_KEY WHERE ID = :NEW.ENC_KEY_ID;
#             l_encrypted_email := DBMS_CRYPTO.ENCRYPT(:NEW.EMAIL, 4358, l_enc_key);
            
#             INSERT INTO C##SHOP_USER.SHOP_USER(ID, FIRST_NAME, LAST_NAME, LOGIN, EMAIL, PASSWORD, IMAGE, ROLE_ID, ENC_KEY_ID) 
#                 VALUES(:NEW.ID, :NEW.FIRST_NAME, :NEW.LAST_NAME, :NEW.LOGIN, l_encrypted_email, :NEW.PASSWORD, 
#                 :NEW.IMAGE, :NEW.ROLE_ID, :NEW.ENC_KEY_ID);
#         EXCEPTION 
#             WHEN NO_DATA_FOUND 
#             THEN RAISE_APPLICATION_ERROR(-20001,'NOT FOUND THE ENCRYPTION KEY FOR THIS CLIENT');
#         END""")
#         event.listen(ShopUser, 'init', t_insert_into_shop_user.execute_if(dialect='oracle'), once=True)

#         t_update_shop_user = DDL("""CREATE OR REPLACE TRIGGER UPDATE_SHOP_USER 
#             INSTEAD OF UPDATE ON C##SHOP_USER.SHOP_USER_VIEW
#             FOR EACH ROW
#         DECLARE
#             l_encrypted_email RAW(2000);
#             l_enc_key RAW(2000);
#         BEGIN
#             IF :OLD.ID != SYS_CONTEXT('userenv', 'client_identifier')
#             THEN
#                 RAISE_APPLICATION_ERROR(-20002,'ONLY THE USER CAN MODIFY THEIR DATA');
#             END IF;

#             SELECT KEY INTO l_enc_key FROM C##SHOP_USER.ENC_KEY WHERE ID = :NEW.ENC_KEY_ID;
#             l_encrypted_email := DBMS_CRYPTO.ENCRYPT(UTL_I18N.STRING_TO_RAW(:NEW.EMAIL), 4358, l_enc_key);
            
#             UPDATE C##SHOP_USER.SHOP_USER SET 
#                 ID = :NEW.ID,
#                 FIRST_NAME = :NEW.FIRST_NAME,
#                 LAST_NAME = :NEW.LAST_NAME,
#                 LOGIN = :NEW.LOGIN,
#                 EMAIL = l_encrypted_email,
#                 PASSWORD = :NEW.PASSWORD,
#                 IMAGE = :NEW.IMAGE, 
#                 ROLE_ID = :NEW.ROLE_ID,
#                 ENC_KEY_ID = :NEW.ENC_KEY_ID
#             WHERE ID = :OLD.ID;
            
#         EXCEPTION 
#             WHEN NO_DATA_FOUND 
#             THEN RAISE_APPLICATION_ERROR(-20001,'NOT FOUND THE ENCRYPTION KEY FOR THIS CLIENT');
#         END""")
#         event.listen(ShopUser, 'init', t_insert_into_shop_user.execute_if(dialect='oracle'), once=True)
