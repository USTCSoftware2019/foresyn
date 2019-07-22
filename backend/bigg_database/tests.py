import json

from django.shortcuts import reverse
from django.test import Client, TestCase

from .models import Metabolite, Model, Reaction

from urllib.parse import urlencode


def build_url(viewname, *args, **kwargs):
    get = kwargs.pop('get', {})
    # FIXME: reverse() requires "app_name:url_name"
    viewname = "bigg_database:" + viewname

    url = reverse(viewname=viewname, *args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url


class IdSearchTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_id_model(self):

        client = Client()
        data = {
            "bigg_id": "iAF692"
        }
        resp = client.get(build_url('search_model', get=data))
        mod_ins = json.loads(resp.content)['content']

        self.assertEqual(mod_ins['compartments'], ["c", "e"])
        self.assertEqual(mod_ins['version'], "1")

        data = {
            "bigg_id": "iAPECO1_1312",
        }
        resp = client.get(build_url('search_model', get=data))
        mod_ins = json.loads(resp.content)

        self.assertEqual(mod_ins['compartments'], {"c", "e", "p"})
        self.assertEqual(mod_ins['version'], "1")

    def test_id_reaction(self):

        client = Client()
        data = {
            "bigg_id": "PLDAGAT_MYRS_EPA_MYRS_PC_3_c"
        }
        resp = client.get(build_url('search_reaction', get=data))
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['name'],
                         "Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)")
        self.assertEqual(reac_ins['reaction_string'],
                         "12dgr140205n3_c + pc1619Z140_c &#8652; 1agpc161_c + tag140205n3140_c")
        self.assertEqual(reac_ins['pseudoreaction'], False)

        data = {"bigg_id": "ACACT1m"}
        resp = client.get(build_url('search_reaction', get=data))
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['name'],
                         "Acetyl CoA C acetyltransferase  mitochondrial")
        self.assertEqual(reac_ins['reaction_string'],
                         "2.0 accoa_m &#8652; aacoa_m + coa_m")
        self.assertEqual(reac_ins['pseudoreaction'], False)

    def test_id_metabolite(self):

        client = Client()
        data = {"bigg_id": "nac_e"}
        resp = client.get(build_url('search_metabolite', get=data))
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['name'],
                         "Nicotinate")
        self.assertEqual(meta_ins['formulae'], ["C6H4NO2"])
        self.assertEqual(meta_ins['charges'], -1)

        data = {"bigg_id": "prephthcoa_c"}
        resp = client.get(build_url('search_metabolite', get=data))
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['name'],
                         "Phthiocerol precursor bound coenzyme A")
        self.assertEqual(meta_ins['formulae'],
                         ["C53H92N7O20P3S"])
        self.assertEqual(meta_ins['charges'], 0)


class NameSearchTests(TestCase):

    def test_name_reaction(self):

        client = Client()
        data = {"name": "1-alpha,24R,25-Vitamin D-hydroxylase (D2)"}
        resp = client.get(build_url('search_reaction', get=data))
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['bigg_id'], "1a_25VITD2Hm")
        self.assertEqual(reac_ins['reaction_string'],
                         "h_m + nadph_m + o2_m + 1a25dhvitd2_m &#8652; h2o_m + nadp_m + 1a2425thvitd2_m")
        self.assertEqual(reac_ins['pseudoreaction'], False)

        data = {
            "name": "1-Aminocyclopropane-1-carboxylate transport, mitochondria"
        }
        resp = client.get(build_url('search_reaction', get=data))
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['bigg_id'], "1ACPCtm")
        self.assertEqual(reac_ins['reaction_string'],
                         "1acpc_c &#8652; 1acpc_m")
        self.assertEqual(reac_ins['pseudoreaction'], False)

    def test_name_metabolite(self):

        client = Client()
        data = {
            "name": "Sulfate"
        }
        resp = client.get(build_url('search_metabolite', get=data))
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['bigg_id'], "so4")
        self.assertEqual(meta_ins['formulae'], ["SO4", "O4S"])
        self.assertEqual(meta_ins['charges'], -2)

        data = {"name": "1-14:0-2-lysophosphatidylcholine"}
        resp = client.post('search/metabolite/name', data)
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['bigg_id'], "1agpc140")
        self.assertEqual(meta_ins['formulae'], ["C22H46NO7P"])
        self.assertEqual(meta_ins['charges'], 0)
