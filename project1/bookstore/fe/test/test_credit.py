# import time
# import pytest
# from fe.access import auth
# from fe import conf
#
#
# class TestCredit:
#     @pytest.fixture(autouse=True)
#     def pre_run_initialization(self):
#         self.auth = auth.Auth(conf.URL)
#         # 注册用户
#         self.user_id = "test_credit_{}".format(time.time())
#         self.password = "password_" + self.user_id
#         self.terminal = "terminal_" + self.user_id
#         code = self.auth.register(self.user_id, self.password)
#         assert code == 200
#         yield
#
#     def test_initial_credit(self):
#         # 假设有个方法可以获取用户信息，包括信用分
#         code, user_info = self.auth.get_user_info(self.user_id)
#         assert code == 200
#         assert user_info['credit'] == 100  # 检查初始信用分是否为100
#
#     def test_set_credit_score(self):
#         # 假设set_credit_score在auth中有相应实现
#         code, message = self.auth.set_credit_score(self.user_id, 150)
#         assert code == 200
#         assert message == "Credit score updated successfully."
#
#         # 再次获取用户信息并验证
#         code, user_info = self.auth.get_user_info(self.user_id)
#         assert code == 200
#         assert user_info['credit'] == 150  # 检查信用分是否已更新