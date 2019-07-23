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
            "bigg_id": "Iaf"
        }
        resp = client.get(build_url('search_model', get=data))
        resp = json.loads(resp.content)

        models = {model['bigg_id'] for model in resp['result']}
        expect = {'iAF987', 'iAF1260b', 'iAF1260', 'iAF692'}

        # test list equal
        self.assertSetEqual(models, expect)

        model_ins = next(model for model in resp['result'] if model['id'] == 1)
        # test elements information
        self.assertDictEqual(model_ins, {
            "id": 1,
            "bigg_id": "iAF987",
            "compartments": ["c", "e", "p"],
            "reaction_set_count": 0,
            "metabolite_set_count": 0,
            "gene_set_count": 0
        })

    def test_id_reaction(self):

        client = Client()
        data = {
            "bigg_id": "PLDAGAT_MARS"
        }
        resp = client.get(build_url('search_reaction', get=data))
        resp = json.loads(resp.content)

        reactions = {reaction['bigg_id'] for reaction in resp['result']}
        expect = {'PLDAGAT_MYRS_EPA_MYRS_PC_3_c'}

        # test list equal
        self.assertSetEqual(reactions, expect)

        reaction_ins = next(reaction for reaction in resp['result'] if reaction['id'] == 1)

        # test elements information
        self.assertDictEqual(reaction_ins, {
            "id": 1,
            "bigg_id": "PLDAGAT_MYRS_EPA_MYRS_PC_3_c",
            "name": "Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)",
            "reaction_string": "12dgr140205n3_c + pc1619Z140_c &#8652; 1agpc161_c + tag140205n3140_c",
            "pseudoreaction": False,
            "database_links": {},
            "models_count": 0,
            "metabolite_set_count": 0,
            "gene_set_count": 0
        })

    def test_id_metabolite(self):

        client = Client()
        data = {"bigg_id": "nac_e"}
        resp = client.get(build_url('search_metabolite', get=data))
        resp = json.loads(resp.content)

        metabolites = {meta['bigg_id'] for meta in resp['result']}
        expect = {'nac_e', 'nac_m', 'nac_p', 'nac_c'}

        # test list equal
        self.assertSetEqual(metabolites, expect)

        meta_ins = next(meta for meta in resp['result'] if meta['id'] == 1)

        # test elements information
        self.assertDictEqual(meta_ins, {
            "id": 1,
            "bigg_id": "nac_e",
            "name": "Nicotinate",
            "formulae": ["C6H4NO2"],
            "charges": -1,
            "database_links": {
                "KEGG Compound": [{"link": "http://identifiers.org/kegg.compound/C00253", "id": "C00253"}],
                "CHEBI": [{"link": "http://identifiers.org/chebi/CHEBI:14650", "id": "CHEBI:14650"},
                          {"link": "http://identifiers.org/chebi/CHEBI:15940", "id": "CHEBI:15940"},
                          {"link": "http://identifiers.org/chebi/CHEBI:22851", "id": "CHEBI:22851"},
                          {"link": "http://identifiers.org/chebi/CHEBI:25530", "id": "CHEBI:25530"},
                          {"link": "http://identifiers.org/chebi/CHEBI:25538", "id": "CHEBI:25538"},
                          {"link": "http://identifiers.org/chebi/CHEBI:32544", "id": "CHEBI:32544"},
                          {"link": "http://identifiers.org/chebi/CHEBI:44319", "id": "CHEBI:44319"},
                          {"link": "http://identifiers.org/chebi/CHEBI:7559", "id": "CHEBI:7559"}],
                "BioCyc": [{"link": "http://identifiers.org/biocyc/META:NIACINE", "id": "META:NIACINE"}],
                "Human Metabolome Database": [{"link": "http://identifiers.org/hmdb/HMDB01488", "id": "HMDB01488"}],
                "Reactome": [{"link": "http://www.reactome.org/content/detail/R-ALL-197230", "id": "197230"},
                             {"link": "http://www.reactome.org/content/detail/R-ALL-8869604", "id": "8869604"}],
                "MetaNetX (MNX) Chemical": [
                    {"link": "http://identifiers.org/metanetx.chemical/MNXM274", "id": "MNXM274"}],
                "SEED Compound": [{"link": "http://identifiers.org/seed.compound/cpd00218", "id": "cpd00218"}],
                "KEGG Drug": [{"link": "http://identifiers.org/kegg.drug/D00049", "id": "D00049"}]},
            "reactions_count": 0,
            "models_count": 0
        })

    def test_search_with_no_id_name(self):

        client = Client()
        resp = client.get(build_url('search_metabolite'))
        resp = json.loads(resp.content)

        metabolites = resp['result']

        # should be empty
        self.assertEqual(metabolites, [])

    def test_search_with_id_and_name(self):

        client = Client()
        data = {
            'bigg_id': 'Iaf',
            'name': "It doesn't matter",
        }
        resp = client.get(build_url('search_model', get=data))
        resp = json.loads(resp.content)

        models = {model['bigg_id'] for model in resp['result']}
        expect = {'iAF987', 'iAF1260b', 'iAF1260', 'iAF692'}

        # test list equal
        self.assertSetEqual(models, expect)


class NameSearchTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_name_reaction(self):

        client = Client()
        data = {"name": "diacylgycero"}  # typo: diacylglycerol -> diacylgycero, this is deliberate

        resp = client.get(build_url('search_reaction', get=data))
        resp = json.loads(resp.content)

        reactions = {reaction['id'] for reaction in resp['result']}
        expect = {1, 3, 5, 6, 14, 26, 28, 33, 68, 87}

        self.assertSetEqual(reactions, expect)

    def test_name_metabolite(self):

        client = Client()
        data = {
            "name": "nictina"  # typo: nicotina -> nictina
        }
        resp = client.get(build_url('search_metabolite', get=data))
        resp = json.loads(resp.content)

        metabolites = {meta['id'] for meta in resp['result']}
        expect = {1, 2, 3, 4}

        self.assertSetEqual(metabolites, expect)


class DetailTests(TestCase):
    fixtures = ['bigg_database/test_data', 'bigg_database/test_gene_data']

    def test_model_detail(self):
        client = Client()

        resp = client.get(reverse('bigg_database:model_detail', args=(20,)))

        expect = {
            "id": 20,
            "bigg_id": "iJO1366",
            "compartments": ["c", "e", "p"],
            "version": "1",
            "reaction_count": 0,
            "metabolite_count": 0
        }

        self.assertJSONEqual(resp.content, expect)

    def test_reaction_detail(self):
        client = Client()

        resp = client.get(reverse('bigg_database:reaction_detail', args=(20,)))

        expect = {
            "id": 20,
            "bigg_id": "LCAT36e",
            "name": "Lecithin-Cholesterol Acyltransferase, "
                    "Formation of 1-Docosatetraenoylglycerophosphocholine (Delta 7, 10, 13, 16)",
            "reaction_string": "chsterol_e + pchol_hs_e &#8652; xolest2_hs_e + pcholn224_hs_e",
            "pseudoreaction": False,
            "database_links": {},
            "model_count": 0,
            "metabolite_count": 0
        }

        self.assertJSONEqual(resp.content, expect)

    def test_metabolite_detail(self):
        client = Client()

        resp = client.get(reverse('bigg_database:metabolite_detail', args=(20,)))

        expect = {
            "id": 20,
            "bigg_id": "cs_b_deg1_l",
            "name": "Chondroitin sulfate B / dermatan sulfate (IdoA2S-GalNAc4S), degradation product 1",
            "formulae": ["C45H67N2O46S3"],
            "charges": -5,
            "database_links": {"MetaNetX (MNX) Chemical": [
                {"link": "http://identifiers.org/metanetx.chemical/MNXM10941", "id": "MNXM10941"}
            ]},
            "reaction_count": 0,
            "model_count": 0
        }

        self.assertJSONEqual(resp.content, expect)

    def test_gene_detail(self):
        client = Client()

        resp = client.get(reverse('bigg_database:gene_detail', args=(20,)))

        expect = {
            "id": 20,
            "rightpos": 3906248,
            "leftpos": 3905316, 
            "chromosome_ncbi_accession": "AE006468.1", 
            "mapped_to_genbank": True, 
            "strand": "+", 
            "protein_sequence": "MIIVTGGAGFIGSNIVKALNDKGITDILVVDNLKDGTKFVNLVDLNIADYMDKEDFLIQIMSGEELGDIEAIFHE"
                "GACSSTTEWDGKYMMDNNYQYSKELLHYCLEREIPFLYASSAATYGGRTSDFIESREYEKPLNVYGYSKFLFDEYVRQILPEANSQIVGFR"
                "YFNVYGPREGHKGSMASVAFHLNTQLNNGESPKLFEGSENFKRDFVYVGDVAAVNLWFLESGKSGIFNLGTGRAESFQAVADATLAYHKKG"
                "SIEYIPFPDKLKGRYQAFTQADLTNLRNAGYDKPFKTVAEGVTEYMAWLNRDA",
            "dna_sequence": "ATGATCATCGTTACCGGCGGCGCGGGCTTTATCGGCAGCAATATCGTTAAGGCCCTGAATGATAAAGGTATCACCGATA"
                "TTCTGGTGGTGGATAACCTGAAAGACGGCACCAAGTTTGTAAACCTGGTGGATCTGAACATTGCTGACTATATGGATAAGGAAGATTTCCT"
                "GATCCAGATTATGTCCGGAGAAGAGCTCGGCGATATCGAAGCTATTTTCCATGAAGGCGCCTGCTCTTCCACCACCGAGTGGGACGGCAAG"
                "TATATGATGGATAATAACTATCAATACTCCAAAGAGCTGCTGCACTATTGTCTTGAGCGCGAAATCCCGTTCCTCTACGCCTCTTCTGCCG"
                "CCACCTATGGCGGTCGCACGTCTGATTTCATCGAATCGCGCGAATACGAAAAACCGCTTAACGTTTATGGCTATTCTAAATTCCTGTTTGA"
                "TGAATATGTGCGCCAGATCCTGCCAGAAGCGAACTCGCAGATTGTCGGTTTCCGCTATTTCAACGTCTATGGACCACGTGAAGGCCATAAA"
                "GGCAGCATGGCAAGCGTGGCATTTCATCTGAATACACAGTTAAACAACGGCGAAAGCCCGAAACTGTTTGAAGGCAGCGAAAACTTCAAGC"
                "GCGACTTCGTTTACGTGGGCGATGTGGCCGCCGTTAACCTGTGGTTCCTGGAAAGCGGCAAGTCCGGCATCTTTAACCTGGGCACAGGCCG"
                "TGCGGAATCTTTCCAGGCCGTCGCCGACGCGACGCTGGCATACCATAAAAAAGGTAGCATTGAATACATTCCGTTCCCGGATAAGCTGAAA"
                "GGTCGCTATCAGGCGTTTACGCAGGCGGATTTAACCAATCTGCGCAACGCGGGCTACGACAAACCCTTTAAGACCGTCGCCGAAGGCGTCA"
                "CGGAGTATATGGCCTGGCTGAACCGCGACGCGTAA", 
            "genome_name": "AE006468.1", 
            "genome_ref_string": "ncbi_accession:AE006468.1", 
            "database_links": {"NCBI GI": [{"link": "http://identifiers.org/ncbigi/gi:16422277", "id": "16422277"}]}, 
            "model_count": 0, 
            "reaction_count": 0
        }

        self.assertJSONEqual(resp.content, expect)
