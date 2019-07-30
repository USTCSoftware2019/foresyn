from django.test import TestCase, Client
from django.contrib.auth.models import User


class ModelTest(TestCase):
    fixtures = ['bigg_database/test_data',]

    def _create_user_and_login(self):
        user_info = {'username': 'test', 'password': '12345678'}
        user = User.objects.create_user(**user_info)
        self.client = Client()
        self.client.login(**user_info)
        return user

    def test_add_model(self):
        # TBD
        pass

    # def test_add_reactions(self):
    #     self._create_user_and_login()
    #     pk = 1
    #     res = self.client.post("/data_wrapper/add_reactions/", {"pk": pk}).status_code
    #     self.assertEqual(res, 200)

    def test_add_metabolite(self):
        self._create_user_and_login()
        pk = 1
        res = self.client.post("/data/add_metabolites/", {"pk": pk}).status_code
        self.assertEqual(res, 200)

    # def test_add_metabolite_without_login(self):
    #     self.client = Client()
    #     pk = 1
    #     res = self.client.post("/data_wrapper/add_metabolites/", {"pk": pk}).status_code
    #     self.assertEqual(res, 401)
