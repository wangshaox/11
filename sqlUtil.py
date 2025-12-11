import pymysql
from pymysql.cursors import DictCursor # 导入 DictCursor，使查询结果以字典形式返回

class MySQLDBUtil:
    """
    MySQL 数据库操作工具类
    使用上下文管理器自动管理连接和游标。
    """
    
    def __init__(self, host, user, password, db, port=3306, charset='utf8mb4'):
        """
        初始化数据库连接参数。
        """
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset
        self._conn = None
        self._cursor = None

    def __enter__(self):
        """
        进入上下文时，建立数据库连接和游标。
        """
        try:
            self._conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db,
                port=self.port,
                charset=self.charset,
                cursorclass=DictCursor # 使用字典游标
            )
            self._cursor = self._conn.cursor()
            return self

        except pymysql.MySQLError as e:
            print(f"数据库连接失败: {e}")
            raise # 抛出异常，让使用者知道连接失败

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        退出上下文时，关闭游标和连接。
        """
        if self._cursor:
            self._cursor.close()
        if self._conn:
            # 如果没有发生异常，则提交事务
            if exc_type is None:
                self._conn.commit()
            else:
                # 发生异常，回滚事务
                self._conn.rollback()
            self._conn.close()

    def execute_query(self, sql, params=None, fetch_all=True):
        """
        执行查询 (SELECT) 操作。
        """
        try:
            self._cursor.execute(sql, params)
            if fetch_all:
                return self._cursor.fetchall()
            else:
                return self._cursor.fetchone()
        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return None

    def execute_insert_one(self, sql, params):
        """
        执行单条插入 (INSERT) 或更新 (UPDATE/DELETE) 操作。
        返回受影响的行数。
        """
        try:
            rows = self._cursor.execute(sql, params)
            return rows
        except pymysql.MySQLError as e:
            print(f"插入/更新失败: {e}")
            raise # 重新抛出异常，触发 __exit__ 中的回滚

    def execute_insert_many(self, sql, params_list):
        """
        执行批量插入 (INSERT) 操作。
        params_list 是参数元组的列表。
        返回受影响的行数。
        """
        try:
            rows = self._cursor.executemany(sql, params_list)
            return rows
        except pymysql.MySQLError as e:
            print(f"批量插入失败: {e}")
            raise # 重新抛出异常，触发 __exit__ 中的回滚