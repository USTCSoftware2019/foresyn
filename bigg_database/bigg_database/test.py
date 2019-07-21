import json
from django.test import TestCase,Client
from .models import Model,Reaction,Metabolite

class ModelTests(TestCase):

    def test_id_model(self):

        self.client = Client()
        data = {
        "bigg_id":"iAF692"}
        resp = self.client.post('',data) #未填写url
        mod_ins = json.loads(resp.content)

        self.assertEqual(mod_ins['compartments'],
        {"c":"cytosol","e":"extracellular space"})
        self.assertEqual(mod_ins['version'],"1")


        data = {
        "bigg_id":"iAPECO1_1312"}
        resp = self.client.post('',data) #未填写url
        mod_ins = json.loads(resp.content)

        self.assertEqual(mod_ins['compartments'],
        {"c":"cytosol",
        "e":"extracellular space",
        "p":"periplasm"})
        self.assertEqual(mod_ins['version'],"1")

    def test_id_reaction(TestCase):

        data = {
        "bigg_id":"1a25DHVITD3TRn"}
        resp = self.client.post('',data) #未填写url
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['name'],
        "Tanslocation of 1-alpha,25-Dihydroxyvitamin D3 to nucleus")
        self.assertEqual(reac_ins['reaction_string'],
        "1a25dhvitd3_c &#8652; 1a25dhvitd3_n")
        self.assertEqual(reac_ins['pseudoreaction'],
        false)


        data = {
        "bigg_id":"1AGPEAT1819Z1835Z9Z12Z"}
        resp = self.client.post('',data) #未填写url
        reac_ins = json.loads(resp.content)

        self.assertEqual(reac_ins['name'],
        "1-acylglycerophosphoethanolamine O-acyltransferase (18:1(9Z)/18:3(5Z,12Z,15Z))")
        self.assertEqual(reac_ins['reaction_string'],
        "1agpe1819Z_c + pacoa_c &#8652; coa_c + pe1819Z1835Z9Z12Z_c")
        self.assertEqual(reac_ins['pseudoreaction'],
        false)

    def test_id_metabolite(TestCase):

        data = {
        "bigg_id":"1a2425thvitd3"}
        resp = self.client.post('',data) #未填写url
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['name'],
        "1-alpha,24R,25-Trihydroxyvitamin D3")
        self.assertEqual(meta_ins['formulae'],
        ["C27H44O4"])
        self.assertEqual(meta_ins['charges'],
        [0])


        data = {
        "bigg_id":"1agpc_SC"}
        resp = self.client.post('',data) #未填写url
        meta_ins = json.loads(resp.content)

        self.assertEqual(meta_ins['name'],
        "1 Acyl sn glycerol 3 phosphocholine  yeast specific C2420H4922N100O700P100")
        self.assertEqual(meta_ins['formulae'],
        ["C2420H4922N100O700P100"])
        self.assertEqual(meta_ins['charges'],
        [0])

