import time
import pytest
from fe.access import auth
from fe import conf


class TestCredit:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.auth = auth.Auth(conf.URL)
        # 注册用户
        self.user_id = "test_credit_{}".format(time.time())
        self.password = "password_" + self.user_id
        self.terminal = "terminal_" + self.user_id
        code = self.auth.register(self.user_id, self.password)
        assert code == 200
        self.points_to_deduct = 5  # 测试扣除的信用分数
        yield

    # 测试是否能成功更新信用分
    def test_deduct_credit_success(self):
        code = self.auth.update_credit(self.user_id, self.points_to_deduct)
        assert code == 200

        # 测试当信用分不足时的情况

    def test_insufficient_credit(self):
        # 将信用分设置为0
        code = self.auth.set_credit_score(self.user_id, 0)
        assert code == 200

        # 测试扣分操作应返回信用分不足的错误
        code = self.auth.update_credit(self.user_id, self.points_to_deduct)
        assert code != 200



