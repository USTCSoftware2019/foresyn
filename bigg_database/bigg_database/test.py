import json
from django.test import TestCase,Client
from .models import Model,Reaction,Metabolite

class IdSearchTests(TestCase):

    def test_id_model(self):

        client = Client()
        data = {
        "bigg_id":"iAF692"}
        resp = client.post('search/model/id',data) 
        print(resp.content)
        mod_ins = json.loads(resp.content)['content']

        self.assertEqual(mod_ins['compartments'],
        {"c":"cytosol","e":"extracellular space"})
        self.assertEqual(mod_ins['version'],"1")


        data = {
        "bigg_id":"iAPECO1_1312"}
        resp = client.post('search/model/id',data) 
        mod_ins = json.loads(resp.content)

        self.assertEqual(mod_ins['compartments'],
        {"c":"cytosol",
        "e":"extracellular space",
        "p":"periplasm"})
        self.assertEqual(mod_ins['version'],"1")

    def test_id_reaction(TestCase):

        client = Client()
        data = {
        "bigg_id":"1a25DHVITD3TRn"}
        resp = client.post('search/reaction/id',data) 
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['name'],
        "Tanslocation of 1-alpha,25-Dihydroxyvitamin D3 to nucleus")
        self.assertEqual(reac_ins['reaction_string'],
        "1a25dhvitd3_c &#8652; 1a25dhvitd3_n")
        self.assertEqual(reac_ins['pseudoreaction'],
        false)


        data = {
        "bigg_id":"1AGPEAT1819Z1835Z9Z12Z"}
        resp = client.post('search/reaction/id',data) 
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['name'],
        "1-acylglycerophosphoethanolamine O-acyltransferase (18:1(9Z)/18:3(5Z,12Z,15Z))")
        self.assertEqual(reac_ins['reaction_string'],
        "1agpe1819Z_c + pacoa_c &#8652; coa_c + pe1819Z1835Z9Z12Z_c")
        self.assertEqual(reac_ins['pseudoreaction'],
        false)

    def test_id_metabolite(TestCase):

        client = Client()
        data = {
        "bigg_id":"1a2425thvitd3"}
        resp = client.post('search/metabolite/id',data) 
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['name'],
        "1-alpha,24R,25-Trihydroxyvitamin D3")
        self.assertEqual(meta_ins['formulae'],
        ["C27H44O4"])
        self.assertEqual(meta_ins['charges'],
        [0])


        data = {
        "bigg_id":"1agpc_SC"}
        resp = client.post('search/metabolite/id',data) 
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['name'],
        "1 Acyl sn glycerol 3 phosphocholine  yeast specific C2420H4922N100O700P100")
        self.assertEqual(meta_ins['formulae'],
        ["C2420H4922N100O700P100"])
        self.assertEqual(meta_ins['charges'],
        [0])

class NameSearchTests(TestCase):

    def test_name_reaction(TestCase):

        client = Client()
        data = {
        "name":"1-alpha,24R,25-Vitamin D-hydroxylase (D2)"}
        resp = client.post('search/reaction/name',data) 
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['bigg_id'],
        "1a_25VITD2Hm")
        self.assertEqual(reac_ins['reaction_string'],
        "h_m + nadph_m + o2_m + 1a25dhvitd2_m &#8652; h2o_m + nadp_m + 1a2425thvitd2_m")
        self.assertEqual(reac_ins['pseudoreaction'],
        false)


        data = {
        "name":"1-Aminocyclopropane-1-carboxylate transport, mitochondria"}
        resp = client.post('search/reaction/name',data) 
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['bigg_id'],
        "1ACPCtm")
        self.assertEqual(reac_ins['reaction_string'],
        "1acpc_c &#8652; 1acpc_m")
        self.assertEqual(reac_ins['pseudoreaction'],
        false)

    def test_name_metabolite(TestCase):

        client = Client()
        data = {
        "name":"Sulfate"}
        resp = client.post('search/metabolite/name',data) 
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['bigg_id'],
        "so4")
        self.assertEqual(meta_ins['formulae'],
            [
            "SO4",
            "O4S"])
        self.assertEqual(meta_ins['charges'],
        [-2])


        data = {
        "name":"1-14:0-2-lysophosphatidylcholine"}
        resp = client.post('search/metabolite/name',data) 
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['bigg_id'],
        "1agpc140")
        self.assertEqual(meta_ins['formulae'],
        ["C22H46NO7P"])
        self.assertEqual(meta_ins['charges'],
        [0])