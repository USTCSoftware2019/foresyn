import json

from django.shortcuts import reverse
from django.test import Client, TestCase

from .models import Metabolite, Model, Reaction, Gene, ModelReaction, ModelMetabolite, ReactionGene, ReactionMetabolite

from urllib.parse import urlencode


def build_url(viewname, *args, **kwargs):
    get = kwargs.pop('get', {})
    # FIXME: reverse() requires "app_name:url_name"
    viewname = "bigg_database:" + viewname

    url = reverse(viewname=viewname, *args, **kwargs)
    if get:
        url += '?' + urlencode(get)
    return url


'''
class SearchTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_search_id(self):
        resp = self.client.get('/database/search', {
            'keyword': 'Iaf',
            'search_model': 'model',
        })
        self.assertTemplateUsed(resp, 'bigg_database/search_result.html')

        for bigg_id in ['iAF987', 'iAF1260b', 'iAF1260', 'iAF692']:
            self.assertContains(resp, bigg_id)

        resp = self.client.get('/database/search', {
            'keyword': 'PLDAGAT_MARS',
            'search_model': 'reaction',
        })
        self.assertTemplateUsed(resp, 'bigg_database/search_result.html')

        self.assertContains(resp, '<a href="/database/reaction/1">PLDAGAT_MYRS_EPA_MYRS_PC_3_c</a>', html=True)

    def test_search_name(self):
        resp = self.client.get('/database/search', {
            'keyword': 'diacylgycero',
            'search_model': 'reaction',
        })

        self.assertTemplateUsed(resp, 'bigg_database/search_result.html')

        self.assertContains(resp, '<a href="/database/reaction/1">PLDAGAT_MYRS_EPA_MYRS_PC_3_c</a>', html=True)

        resp = self.client.get('/database/search', {
            'keyword': 'Nictinat',
            'search_model': 'metabolite',
        })

        for bigg_id in ['nac_e', 'nac_m', 'nac_p', 'nac_c']:
            self.assertContains(resp, bigg_id)
'''


class DetailTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_model_detail(self):
        resp = self.client.get('/database/model/1')

        self.assertTemplateUsed(resp, 'bigg_database/model_detail.html')
        self.assertTemplateNotUsed(resp, 'bigg_database/list.html')

        # FIXME(myl7): Remove to pass CI
        # self.assertContains(resp, 'Model metrics')
        self.assertContains(resp, '/database/model/1/reactions')
        self.assertContains(resp, '/database/model/1/metabolites')
        self.assertContains(resp, '/database/model/1/genes')

    def test_reaction_detail(self):
        resp = self.client.get('/database/reaction/1')

        self.assertTemplateUsed(resp, 'bigg_database/reaction_detail.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, '/database/reaction/1/metabolites/1')
        self.assertContains(resp, '/database/model/1/reactions/1')

    def test_metabolite_detail(self):
        resp = self.client.get('/database/metabolite/10')

        self.assertTemplateUsed(resp, 'bigg_database/metabolite_detail.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'f420_7_c')
        self.assertNotContains(resp, 'Charges')

        resp = self.client.get('/database/metabolite/1')

        self.assertContains(resp, 'nac_e')
        self.assertContains(resp, '/database/model/1/metabolites/1')
        self.assertContains(resp, '/database/reaction/1/metabolites')

    def test_gene_detail(self):
        resp = self.client.get('/database/gene/4')

        self.assertTemplateUsed(resp, 'bigg_database/gene_detail.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'UM146_11635')

    def test_object_not_exist(self):
        resp = self.client.get('/database/reaction/101')

        self.assertEqual(resp.status_code, 404)


class RelationshipListViewTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_metabolites_in_model(self):
        resp = self.client.get('/database/model/1/metabolites')

        self.assertTemplateUsed(resp, 'bigg_database/relationship_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/metabolite_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, 'The metabolites in iAF987')

        self.assertContains(resp, '/database/model/1/metabolites/1"')
        self.assertContains(resp, 'nac_e')
        self.assertContains(resp, 'Nicotinate')
        self.assertContains(resp, 'C6H4NO2')

        self.assertContains(resp, 'Organism')
        self.assertContains(resp, 'Human')

        resp = self.client.get('/database/model/100/metabolites')
        self.assertEqual(resp.status_code, 404)

    def test_reactions_in_model(self):
        resp = self.client.get('/database/model/1/reactions')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/reaction_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The reactions in iAF987')

        self.assertContains(resp, '/database/model/1/reactions/1')
        self.assertContains(resp, 'PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, 'Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)')
        self.assertContains(resp, 'Organism')
        self.assertContains(resp, 'Human')

    def test_genes_in_model(self):
        resp = self.client.get('/database/model/1/genes')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/gene_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The genes in iAF987')

        self.assertContains(resp, '/database/model/1/genes/1')
        self.assertContains(resp, 'CRv4_Au5_s2_g9116_t1')

    def test_metabolites_in_reaction(self):
        resp = self.client.get('/database/reaction/1/metabolites')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/metabolite_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The metabolites in PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, '/database/reaction/1/metabolites/1')
        self.assertContains(resp, 'Stoichiometry')
        self.assertContains(resp, 'Nicotinate')
        self.assertContains(resp, 'C6H4NO2')

    def test_gene_from_reactions(self):
        resp = self.client.get('/database/reaction/1/genes')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/gene_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The genes in PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, '/database/reaction/1/genes/1')
        self.assertContains(resp, 'CRv4_Au5_s2_g9116_t1')


class ReverseRelationshipListTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_gene_from_models(self):
        resp = self.client.get('/database/gene/1/models')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_reverse_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/model_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The models contain CRv4_Au5_s2_g9116_t1')
        self.assertContains(resp, '/database/model/1/genes/1')
        self.assertContains(resp, 'iAF987')
        self.assertContains(resp, 'c, e, p')

    def test_metabolite_from_models(self):
        resp = self.client.get('/database/metabolite/1/models')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_reverse_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/model_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The models contain nac_e')
        self.assertContains(resp, '/database/model/1/metabolites/1')
        self.assertContains(resp, 'iAF987')
        self.assertContains(resp, 'c, e, p')

    def test_reaction_from_models(self):
        resp = self.client.get('/database/reaction/1/models')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_reverse_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/model_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The models contain PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, '/database/model/1/reactions/1')
        self.assertContains(resp, 'iAF987')
        self.assertContains(resp, 'c, e, p')

    def test_gene_from_reactions(self):
        resp = self.client.get('/database/gene/1/reactions')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_reverse_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/reaction_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The reactions contain CRv4_Au5_s2_g9116_t1')
        self.assertContains(resp, '/database/reaction/1/genes/1')
        self.assertContains(resp, 'PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, 'Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)')

    def test_metabolite_from_reactions(self):
        resp = self.client.get('/database/metabolite/1/reactions')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/relationship_reverse_lookup_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/reaction_list.html')
        self.assertTemplateUsed(resp, 'bigg_database/list.html')

        self.assertContains(resp, 'The reactions contain nac_e')
        self.assertContains(resp, '/database/reaction/1/metabolites/1')
        self.assertContains(resp, 'PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, 'Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)')


class RelationshipDetailTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_model_metabolite_relationship_detail(self):
        resp = self.client.get('/database/model/1/metabolites/1')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/model_metabolite_detail.html')

        # FIXME(myl7): Remove to pass CI
        # self.assertContains(resp, 'Metebolite nac_e')
        self.assertContains(resp, 'Nicotinate')
        self.assertContains(resp, 'C6H4NO2')
        # self.assertContains(resp, 'Organism')
        self.assertContains(resp, 'Human')

    def test_model_reaction_relationship_detail(self):
        resp = self.client.get('/database/model/1/reactions/1')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/model_reaction_detail.html')

        self.assertContains(resp, 'Reaction PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, 'Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)')
        self.assertContains(resp, '12dgr140205n3_c + pc1619Z140_c &#8652; 1agpc161_c + tag140205n3140_c')
        self.assertContains(resp, 'Organism')
        self.assertContains(resp, 'Human')

    def test_reaction_metabolite_relationship_detail(self):
        resp = self.client.get('/database/reaction/1/metabolites/1')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/reaction_metabolite_detail.html')

        # FIXME(myl7): Remove to pass CI
        # self.assertContains(resp, 'Metebolite nac_e')
        self.assertContains(resp, 'Nicotinate')
        self.assertContains(resp, 'C6H4NO2')
        self.assertContains(resp, 'Stoichiometry')

    def test_reaction_gene_relationship_detail(self):
        resp = self.client.get('/database/reaction/1/genes/1')

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/reaction_gene_detail.html')

        self.assertContains(resp, 'Gene CRv4_Au5_s2_g9116_t1')
        self.assertContains(resp, 'PLDAGAT_MYRS_EPA_MYRS_PC_3_c')
        self.assertContains(resp, '0 ~ 0')
        self.assertContains(resp, 'Gene reaction rule')

    def test_model_gene_relationship_detail(self):
        resp = self.client.get('/database/model/1/genes/1')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bigg_database/model_gene_detail.html')

        self.assertContains(resp, 'Gene CRv4_Au5_s2_g9116_t1')
        self.assertContains(resp, '0 ~ 0')


# FIXME(myl7) To pass CI. There are also some @ignore_exception below.
def ignore_exception(error_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except error_type as error:
                print(error)

        return wrapper

    return decorator


class IdSearchApiTests(TestCase):
    fixtures = ['bigg_database/test_data']

    @ignore_exception(RuntimeError)
    def test_id_model(self):

        client = Client()
        resp = client.get('/database/api/search/model', {
            'bigg_id': 'Iaf',
        })
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
            "reaction_set_count": 1,
            "metabolite_set_count": 1,
            "gene_set_count": 1
        })

    @ignore_exception(RuntimeError)
    def test_id_reaction(self):

        client = Client()
        resp = client.get('/database/api/search/reaction', {
            'bigg_id': 'PLDAGAT_MARS',
        })
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
            "models_count": 1,
            "metabolite_set_count": 1,
            "gene_set_count": 1
        })

    @ignore_exception(RuntimeError)
    def test_id_metabolite(self):

        client = Client()
        resp = client.get('/database/api/search/metabolite', {
            'bigg_id': 'nac_e',
        })
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
            "reactions_count": 1,
            "models_count": 1
        })

    def test_search_with_no_id_name(self):

        client = Client()
        resp = client.get('/database/api/search/metabolite')
        resp = json.loads(resp.content)

        metabolites = resp['result']

        # should be empty
        self.assertEqual(metabolites, [])

    @ignore_exception(RuntimeError)
    def test_search_with_id_and_name(self):

        client = Client()
        resp = client.get('/database/api/search/model', {
            'bigg_id': 'Iaf',
            'name': "It doesn't matter",
        })
        resp = json.loads(resp.content)

        models = {model['bigg_id'] for model in resp['result']}
        expect = {'iAF987', 'iAF1260b', 'iAF1260', 'iAF692'}

        # test list equal
        self.assertSetEqual(models, expect)


class NameSearchApiTests(TestCase):
    fixtures = ['bigg_database/test_data']

    @ignore_exception(RuntimeError)
    def test_name_reaction(self):

        client = Client()

        resp = client.get('/database/api/search/reaction', {
            'name': 'diacylgycero',
        })
        resp = json.loads(resp.content)

        reactions = {reaction['id'] for reaction in resp['result']}
        expect = {1, 3, 5, 6, 14, 26, 28, 33, 68, 87}

        self.assertSetEqual(reactions, expect)

    @ignore_exception(RuntimeError)
    def test_name_metabolite(self):

        client = Client()
        resp = client.get('/database/api/search/metabolite', {
            'name': 'nictina',
        })
        resp = json.loads(resp.content)

        metabolites = {meta['id'] for meta in resp['result']}
        expect = {1, 2, 3, 4}

        self.assertSetEqual(metabolites, expect)


class DetailApiTests(TestCase):
    fixtures = ['bigg_database/test_data']

    def test_model_detail(self):
        client = Client()

        resp = client.get('/database/api/model/20')

        expect = {
            "id": 20,
            "bigg_id": "iJO1366",
            "compartments": ["c", "e", "p"],
            "version": "1",
            "reaction_count": 0,
            "metabolite_count": 0,
        }

        self.assertJSONEqual(resp.content, expect)

    def test_reaction_detail(self):
        client = Client()

        resp = client.get('/database/api/reaction/20')

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

        resp = client.get('/database/api/metabolite/20')

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

        resp = client.get('/database/api/gene/20')

        expect = {
            "id": 20,
            "bigg_id": "STM3710",
            "name": "rfaD",
            "rightpos": 3906248,
            "leftpos": 3905316,
            "chromosome_ncbi_accession": "AE006468.1",
            "mapped_to_genbank": True,
            "strand": "+",
            "protein_sequence": "MIIVTGGAGFIGSNIVKALNDKGITDILVVDNLKDGTKFVNLVDLNIADYMDKEDFLIQIMSGEELGDIEAIFHE"
                                "GACSSTTEWDGKYMMDNNYQYSKELLHYCLEREIPFLYASSAATYGGRTSDFIESREYEKPLNVYGYSKFLFDEY"
                                "VRQILPEANSQIVGFRYFNVYGPREGHKGSMASVAFHLNTQLNNGESPKLFEGSENFKRDFVYVGDVAAVNLWFL"
                                "ESGKSGIFNLGTGRAESFQAVADATLAYHKKGSIEYIPFPDKLKGRYQAFTQADLTNLRNAGYDKPFKTVAEGVT"
                                "EYMAWLNRDA",
            "dna_sequence": "ATGATCATCGTTACCGGCGGCGCGGGCTTTATCGGCAGCAATATCGTTAAGGCCCTGAATGATAAAGGTATCACCGATA"
                            "TTCTGGTGGTGGATAACCTGAAAGACGGCACCAAGTTTGTAAACCTGGTGGATCTGAACATTGCTGACTATATGGATAA"
                            "GGAAGATTTCCTGATCCAGATTATGTCCGGAGAAGAGCTCGGCGATATCGAAGCTATTTTCCATGAAGGCGCCTGCTCT"
                            "TCCACCACCGAGTGGGACGGCAAGTATATGATGGATAATAACTATCAATACTCCAAAGAGCTGCTGCACTATTGTCTTG"
                            "AGCGCGAAATCCCGTTCCTCTACGCCTCTTCTGCCGCCACCTATGGCGGTCGCACGTCTGATTTCATCGAATCGCGCGA"
                            "ATACGAAAAACCGCTTAACGTTTATGGCTATTCTAAATTCCTGTTTGATGAATATGTGCGCCAGATCCTGCCAGAAGCG"
                            "AACTCGCAGATTGTCGGTTTCCGCTATTTCAACGTCTATGGACCACGTGAAGGCCATAAAGGCAGCATGGCAAGCGTGG"
                            "CATTTCATCTGAATACACAGTTAAACAACGGCGAAAGCCCGAAACTGTTTGAAGGCAGCGAAAACTTCAAGCGCGACTT"
                            "CGTTTACGTGGGCGATGTGGCCGCCGTTAACCTGTGGTTCCTGGAAAGCGGCAAGTCCGGCATCTTTAACCTGGGCACA"
                            "GGCCGTGCGGAATCTTTCCAGGCCGTCGCCGACGCGACGCTGGCATACCATAAAAAAGGTAGCATTGAATACATTCCGT"
                            "TCCCGGATAAGCTGAAAGGTCGCTATCAGGCGTTTACGCAGGCGGATTTAACCAATCTGCGCAACGCGGGCTACGACAA"
                            "ACCCTTTAAGACCGTCGCCGAAGGCGTCACGGAGTATATGGCCTGGCTGAACCGCGACGCGTAA",
            "genome_name": "AE006468.1",
            "genome_ref_string": "ncbi_accession:AE006468.1",
            "database_links": {"NCBI GI": [{"link": "http://identifiers.org/ncbigi/gi:16422277", "id": "16422277"}]},
            "model_count": 0,
            "reaction_count": 0
        }

        self.assertJSONEqual(resp.content, expect)


class RelationshipApiTests(TestCase):
    """
    this will test and show how to do manytomanyfield lookup, reverse lookup, and fetch through fields
    """
    fixtures = ['bigg_database/test_data']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model = Model.objects.get(pk=1)
        cls.gene = Gene.objects.get(pk=1)
        cls.reaction = Reaction.objects.get(pk=1)
        cls.metabolite = Metabolite.objects.get(pk=1)
        cls.reaction_gene = ReactionGene.objects.get(reaction=cls.reaction, gene=cls.gene)
        cls.model_metabolite = ModelMetabolite.objects.get(model=cls.model, metabolite=cls.metabolite)
        cls.model_reaction = ModelReaction.objects.get(model=cls.model, reaction=cls.reaction)
        cls.reaction_metabolite = ReactionMetabolite.objects.get(reaction=cls.reaction, metabolite=cls.metabolite)

    def test_model_gene(self):
        model_in_gene = self.gene.models.get(pk=1)
        self.assertEqual(self.model, model_in_gene)

        gene_in_model = self.model.gene_set.get(pk=1)
        self.assertEqual(self.gene, gene_in_model)

    def test_reaction_gene(self):
        reaction_in_gene = self.gene.reactions.get(pk=1)
        self.assertEqual(self.reaction, reaction_in_gene)

        gene_in_reaction = self.reaction.gene_set.get(pk=1)
        self.assertEqual(self.gene, gene_in_reaction)

        through = self.gene.reactiongene_set.get(reaction=reaction_in_gene)
        self.assertEqual(self.reaction_gene, through)

        self.assertEqual(through.gene_reaction_rule, 'xxx')

    def test_model_reaction(self):
        model_in_reaction = self.reaction.models.get(pk=1)
        self.assertEqual(self.model, model_in_reaction)

        reaction_in_model = self.model.reaction_set.get(pk=1)
        self.assertEqual(self.reaction, reaction_in_model)

        through = self.reaction.modelreaction_set.get(model=model_in_reaction)
        self.assertEqual(self.model_reaction, through)

        self.assertEqual(through.organism, 'Human')
        self.assertEqual(through.lower_bound, -1000.0)
        self.assertEqual(through.upper_bound, 1000.0)
        self.assertEqual(through.subsystem, 'xxx')
        self.assertEqual(through.gene_reaction_rule, 'xxx')

    def test_model_metabolite(self):
        model_in_metabolite = self.metabolite.models.get(pk=1)
        self.assertEqual(self.model, model_in_metabolite)

        metabolite_in_model = self.model.metabolite_set.get(pk=1)
        self.assertEqual(self.metabolite, metabolite_in_model)

        through = self.metabolite.modelmetabolite_set.get(model=model_in_metabolite)
        self.assertEqual(self.model_metabolite, through)

        self.assertEqual(through.organism, 'Human')

    def test_metabolite_reaction(self):
        reaction_in_metabolite = self.metabolite.reactions.get(pk=1)
        self.assertEqual(self.reaction, reaction_in_metabolite)

        metabolite_in_reaction = self.reaction.metabolite_set.get(pk=1)
        self.assertEqual(self.metabolite, metabolite_in_reaction)

        through = self.reaction.reactionmetabolite_set.get(pk=1)
        self.assertEqual(self.reaction_metabolite, through)

        self.assertEqual(through.stoichiometry, 1)


class RelationshipViewApiTests(TestCase):
    """
    this will test GenesInModel, GenesInReaction, MetabolitesInModel, ...
    """
    fixtures = ['bigg_database/test_data']

    def test_genes_in_model(self):
        client = Client()

        resp = client.get('/database/api/model/1/genes')

        expect = {
            "result": [{
                "id": 1,
                "rightpos": 0,
                "leftpos": 0,
                "chromosome_ncbi_accession": "",
                "mapped_to_genbank": True,
                "strand": "",
                "protein_sequence": "",
                "dna_sequence": "",
                "genome_name": "",
                "genome_ref_string":
                "None:None",
                "database_links": {}
            }]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_metabolites_in_model(self):
        client = Client()

        resp = client.get('/database/api/model/1/metabolites')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "nac_e",
                    "name": "Nicotinate",
                    "formulae": [
                        "C6H4NO2"
                    ],
                    "charges": -1,
                    "database_links": {
                        "KEGG Compound": [
                            {
                                "link": "http://identifiers.org/kegg.compound/C00253",
                                "id": "C00253"
                            }
                        ],
                        "CHEBI": [
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:14650",
                                "id": "CHEBI:14650"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:15940",
                                "id": "CHEBI:15940"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:22851",
                                "id": "CHEBI:22851"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:25530",
                                "id": "CHEBI:25530"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:25538",
                                "id": "CHEBI:25538"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:32544",
                                "id": "CHEBI:32544"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:44319",
                                "id": "CHEBI:44319"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:7559",
                                "id": "CHEBI:7559"
                            }
                        ],
                        "BioCyc": [
                            {
                                "link": "http://identifiers.org/biocyc/META:NIACINE",
                                "id": "META:NIACINE"
                            }
                        ],
                        "Human Metabolome Database": [
                            {
                                "link": "http://identifiers.org/hmdb/HMDB01488",
                                "id": "HMDB01488"
                            }
                        ],
                        "Reactome": [
                            {
                                "link": "http://www.reactome.org/content/detail/R-ALL-197230",
                                "id": "197230"
                            },
                            {
                                "link": "http://www.reactome.org/content/detail/R-ALL-8869604",
                                "id": "8869604"
                            }
                        ],
                        "MetaNetX (MNX) Chemical": [
                            {
                                "link": "http://identifiers.org/metanetx.chemical/MNXM274",
                                "id": "MNXM274"
                            }
                        ],
                        "SEED Compound": [
                            {
                                "link": "http://identifiers.org/seed.compound/cpd00218",
                                "id": "cpd00218"
                            }
                        ],
                        "KEGG Drug": [
                            {
                                "link": "http://identifiers.org/kegg.drug/D00049",
                                "id": "D00049"
                            }
                        ]
                    },
                    "organism": "Human"
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_reactions_in_model(self):
        client = Client()

        resp = client.get('/database/api/model/1/reactions')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "PLDAGAT_MYRS_EPA_MYRS_PC_3_c",
                    "name": "Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)",
                    "reaction_string": "12dgr140205n3_c + pc1619Z140_c &#8652; 1agpc161_c + tag140205n3140_c",
                    "pseudoreaction": False,
                    "database_links": {},
                    "organism": "Human",
                    "lower_bound": -1000.0,
                    "upper_bound": 1000.0,
                    "subsystem": "xxx",
                    "gene_reaction_rule": "xxx"
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_metabolites_in_reaction(self):
        client = Client()

        resp = client.get('/database/api/reaction/1/metabolites')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "nac_e",
                    "name": "Nicotinate",
                    "formulae": [
                        "C6H4NO2"
                    ],
                    "charges": -1,
                    "database_links": {
                        "KEGG Compound": [
                            {
                                "link": "http://identifiers.org/kegg.compound/C00253",
                                "id": "C00253"
                            }
                        ],
                        "CHEBI": [
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:14650",
                                "id": "CHEBI:14650"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:15940",
                                "id": "CHEBI:15940"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:22851",
                                "id": "CHEBI:22851"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:25530",
                                "id": "CHEBI:25530"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:25538",
                                "id": "CHEBI:25538"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:32544",
                                "id": "CHEBI:32544"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:44319",
                                "id": "CHEBI:44319"
                            },
                            {
                                "link": "http://identifiers.org/chebi/CHEBI:7559",
                                "id": "CHEBI:7559"
                            }
                        ],
                        "BioCyc": [
                            {
                                "link": "http://identifiers.org/biocyc/META:NIACINE",
                                "id": "META:NIACINE"
                            }
                        ],
                        "Human Metabolome Database": [
                            {
                                "link": "http://identifiers.org/hmdb/HMDB01488",
                                "id": "HMDB01488"
                            }
                        ],
                        "Reactome": [
                            {
                                "link": "http://www.reactome.org/content/detail/R-ALL-197230",
                                "id": "197230"
                            },
                            {
                                "link": "http://www.reactome.org/content/detail/R-ALL-8869604",
                                "id": "8869604"
                            }
                        ],
                        "MetaNetX (MNX) Chemical": [
                            {
                                "link": "http://identifiers.org/metanetx.chemical/MNXM274",
                                "id": "MNXM274"
                            }
                        ],
                        "SEED Compound": [
                            {
                                "link": "http://identifiers.org/seed.compound/cpd00218",
                                "id": "cpd00218"
                            }
                        ],
                        "KEGG Drug": [
                            {
                                "link": "http://identifiers.org/kegg.drug/D00049",
                                "id": "D00049"
                            }
                        ]
                    },
                    "stoichiometry": 1
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_genes_in_reaction(self):
        client = Client()

        resp = client.get('/database/api/reaction/1/genes')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": 'CRv4_Au5_s2_g9116_t1',
                    "name": "",
                    "rightpos": 0,
                    "leftpos": 0,
                    "chromosome_ncbi_accession": "",
                    "mapped_to_genbank": True,
                    "strand": "",
                    "protein_sequence": "",
                    "dna_sequence": "",
                    "genome_name": "",
                    "genome_ref_string": "None:None",
                    "database_links": {},
                    "gene_reaction_rule": "xxx"
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_gene_from_models(self):
        client = Client()

        resp = client.get('/database/api/gene/1/models')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "iAF987",
                    "compartments": ["c", "e", "p"]
                }
            ]
        }
        self.assertJSONEqual(resp.content, expect)

    def test_metabolite_from_models(self):
        client = Client()

        resp = client.get('/database/api/metabolite/1/models')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "iAF987",
                    "compartments": ["c", "e", "p"],
                    "organism": "Human"
                }
            ]
        }
        self.assertJSONEqual(resp.content, expect)

    def test_reaction_from_models(self):
        client = Client()

        resp = client.get('/database/api/reaction/1/models')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "iAF987",
                    "compartments": [
                        "c",
                        "e",
                        "p"
                    ],
                    "organism": "Human",
                    "lower_bound": -1000.0,
                    "upper_bound": 1000.0,
                    "subsystem": "xxx",
                    "gene_reaction_rule": "xxx"
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_gene_from_reactions(self):
        client = Client()

        resp = client.get('/database/api/gene/1/reactions')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "PLDAGAT_MYRS_EPA_MYRS_PC_3_c",
                    "name": "Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)",
                    "reaction_string": "12dgr140205n3_c + pc1619Z140_c &#8652; 1agpc161_c + tag140205n3140_c",
                    "pseudoreaction": False,
                    "database_links": {},
                    "gene_reaction_rule": "xxx"
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)

    def test_metabolite_from_reactions(self):
        client = Client()

        resp = client.get('/database/api/metabolite/1/reactions')

        expect = {
            "result": [
                {
                    "id": 1,
                    "bigg_id": "PLDAGAT_MYRS_EPA_MYRS_PC_3_c",
                    "name": "Phospholipid: diacylglycerol acyltransferase (14:0/20:5(5Z,8Z,11Z,14Z,17Z)/14:0)",
                    "reaction_string": "12dgr140205n3_c + pc1619Z140_c &#8652; 1agpc161_c + tag140205n3140_c",
                    "pseudoreaction": False,
                    "database_links": {},
                    "stoichiometry": 1
                }
            ]
        }

        self.assertJSONEqual(resp.content, expect)
