from django.test import TestCase, Client


class ModelTest(TestCase):
    fixtures = ['bigg_database/test_data']
    client = Client()

    def test_add_model(self):
        # TBD
        pass

    def test_add_metabolite(self):
        pk = 1
        res = self.client.post("/data_wrapper/add_metabolites", {"pk": pk})
        self.assertEqual(res, 'test')
