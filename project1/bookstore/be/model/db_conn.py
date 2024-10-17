from be.model import store


class DBConn:
    def __init__(self):
        # print("arrive at db_conn init")
        # 获取 MongoDB 客户端连接
        self.conn = store.get_db_conn()

        if self.conn is not None:
            # print("Successfully connected to the database")
            self.users_collection = self.conn['users']
            self.stores_collection = self.conn['stores']
            self.orders_collection = self.conn['orders']
        else:
            print("Failed to connect to the database")


    # SQL-version
    # def user_id_exist(self, user_id):
        # 
        # cursor = self.conn.execute(
        #     "SELECT user_id FROM user WHERE user_id = ?;", (user_id,)
        # )
        # row = cursor.fetchone()
        # if row is None:
        #     return False
        # else:
        #     return True

    # def book_id_exist(self, store_id, book_id):
    #     cursor = self.conn.execute(
    #         "SELECT book_id FROM store WHERE store_id = ? AND book_id = ?;",
    #         (store_id, book_id),
    #     )
    #     row = cursor.fetchone()
    #     if row is None:
    #         return False
    #     else:
    #         return True

    # def store_id_exist(self, store_id):
    #     cursor = self.conn.execute(
    #         "SELECT store_id FROM user_store WHERE store_id = ?;", (store_id,)
    #     )
    #     row = cursor.fetchone()
    #     if row is None:
    #         return False
    #     else:
    #         return True

    # MongoDB-version
    def user_id_exist(self, user_id):
        # 在 users 集合中查找 user_id
        if self.users_collection.find_one({"user_id": user_id}) is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        # 在 stores 集合中查找 store_id 和 book_id
        if self.stores_collection.find_one({"store_id": store_id, "inventory.book_id": book_id}) is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        # 在 user_store 集合中查找 store_id
        if self.users_collection.find_one({"stores.store_id": store_id}) is None:
            return False
        else:
            return True