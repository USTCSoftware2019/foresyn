import json

from django.test import TestCase

from . import models as cobra_models


class CobraWrapperTest(TestCase):
    def test_model_build(self):
        self._create_model()

    def _create_model(self):
        """Example on cobra doc to build a model"""
        test_metabolite_0 = cobra_models.CobraMetabolite(
            identifier='ACP_c',
            formula='C11H21N2O7PRS',
            name='acyl-carrier-protein',
            compartment='c'
        )
        test_metabolite_1 = cobra_models.CobraMetabolite(
            identifier='3omrsACP_c',
            formula='C25H45N2O9PRS',
            name='3-Oxotetradecanoyl-acyl-carrier-protein',
            compartment='c'
        )
        test_metabolite_2 = cobra_models.CobraMetabolite(
            identifier='co2_c', formula='CO2', name='CO2', compartment='c'
        )
        test_metabolite_3 = cobra_models.CobraMetabolite(
            identifier='malACP_c',
            formula='C14H22N2O10PRS',
            name='Malonyl-acyl-carrier-protein',
            compartment='c'
        )
        test_metabolite_4 = cobra_models.CobraMetabolite(
            identifier='h_c', formula='H', name='H', compartment='c'
        )
        test_metabolite_5 = cobra_models.CobraMetabolite(
            identifier='ddcaACP_c',
            formula='C23H43N2O8PRS',
            name='Dodecanoyl-ACP-n-C120ACP',
            compartment='c'
        )
        test_metabolite_0.save()
        test_metabolite_1.save()
        test_metabolite_2.save()
        test_metabolite_3.save()
        test_metabolite_4.save()
        test_metabolite_5.save()
        test_reaction = cobra_models.CobraReaction(
            identifier='3OAS140',
            name='3 oxoacyl acyl carrier protein synthase n C140 ',
            subsystem='Cell Envelope Biosynthesis',
            lower_bound=0,
            upper_bound=1000,
            coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
            gene_reaction_rule='( STM2378 or STM1197 )'
        )
        test_reaction.save()
        test_reaction.metabolites.set([
            test_metabolite_0, test_metabolite_1, test_metabolite_2,
            test_metabolite_3, test_metabolite_4, test_metabolite_5
        ])
        test_reaction.save()
        test_model = cobra_models.CobraModel(
            identifier='example_model',
            objective='3OAS140'
        )
        test_model.save()
        test_model.reactions.set([test_reaction])
        test_model.save()
        return {
            'models': [test_model],
            'reactions': [test_reaction],
            'metabolites': [
                test_metabolite_0, test_metabolite_1, test_metabolite_2,
                test_metabolite_3, test_metabolite_4, test_metabolite_5
            ]
        }

    def test_cobra_url_post(self):
        """Still example on cobra doc to build a model, but using web API"""
        metabolite_0_response = self.client.post('/cobra/metabolites/', dict(
            identifier='ACP_c',
            formula='C11H21N2O7PRS',
            name='acyl-carrier-protein',
            compartment='c'
        ), content_type='application/json')
        self.assertEqual(metabolite_0_response.status_code, 201)
        metabolite_0_id = json.loads(metabolite_0_response.content)['id']
        metabolite_1_response = self.client.post('/cobra/metabolites/', dict(
            identifier='3omrsACP_c',
            formula='C25H45N2O9PRS',
            name='3-Oxotetradecanoyl-acyl-carrier-protein',
            compartment='c'
        ), content_type='application/json')
        self.assertEqual(metabolite_1_response.status_code, 201)
        metabolite_1_id = json.loads(metabolite_1_response.content)['id']
        metabolite_2_response = self.client.post('/cobra/metabolites/', dict(
            identifier='co2_c', formula='CO2', name='CO2', compartment='c'
        ), content_type='application/json')
        self.assertEqual(metabolite_2_response.status_code, 201)
        metabolite_2_id = json.loads(metabolite_2_response.content)['id']
        metabolite_3_response = self.client.post('/cobra/metabolites/', dict(
            identifier='malACP_c',
            formula='C14H22N2O10PRS',
            name='Malonyl-acyl-carrier-protein',
            compartment='c'
        ), content_type='application/json')
        self.assertEqual(metabolite_3_response.status_code, 201)
        metabolite_3_id = json.loads(metabolite_3_response.content)['id']
        metabolite_4_response = self.client.post('/cobra/metabolites/', dict(
            identifier='h_c', formula='H', name='H', compartment='c'
        ), content_type='application/json')
        self.assertEqual(metabolite_4_response.status_code, 201)
        metabolite_4_id = json.loads(metabolite_4_response.content)['id']
        metabolite_5_response = self.client.post('/cobra/metabolites/', dict(
            identifier='ddcaACP_c',
            formula='C23H43N2O8PRS',
            name='Dodecanoyl-ACP-n-C120ACP',
            compartment='c'
        ), content_type='application/json')
        self.assertEqual(metabolite_5_response.status_code, 201)
        metabolite_5_id = json.loads(metabolite_5_response.content)['id']
        reaction_response = self.client.post('/cobra/reactions/', dict(
            identifier='3OAS140',
            name='3 oxoacyl acyl carrier protein synthase n C140 ',
            subsystem='Cell Envelope Biosynthesis',
            lower_bound=0,
            upper_bound=1000,
            metabolites=[
                metabolite_0_id, metabolite_1_id, metabolite_2_id,
                metabolite_3_id, metabolite_4_id, metabolite_5_id
            ],
            coefficients=[-1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
            gene_reaction_rule='( STM2378 or STM1197 )'
        ), content_type='application/json')
        self.assertEqual(reaction_response.status_code, 201)
        reaction_id = json.loads(reaction_response.content)['id']
        model_response = self.client.post('/cobra/models/', dict(
            identifier='example_model',
            objective='3OAS140',
            reactions=[reaction_id]
        ), content_type='application/json')
        self.assertEqual(model_response.status_code, 201)
        model_id = json.loads(model_response.content)['id']
        model = cobra_models.CobraModel.objects.get(id=model_id)
        cobra_model = model.build()
        self.assertTrue(
            str(cobra_model.objective.expression) in [
                '-1.0*3OAS140_reverse_65ddc + 1.0*3OAS140',
                '1.0*3OAS140 - 1.0*3OAS140_reverse_65ddc'
            ]
        )
        self.assertEqual(str(cobra_model.objective.direction), 'max')

    def test_cobra_url_patch(self):
        info = self._create_model()
        model_response = self.client.patch('/cobra/models/', {
            'id': info['models'][0].id,
            'objective': 'test'
        }, content_type='application/json')
        self.assertEqual(model_response.status_code, 200)
        reaction_response = self.client.patch('/cobra/reactions/', {
            'id': info['reactions'][0].id,
            'coefficients': [1, 1, 1, 1, 1, 1]
        }, content_type='application/json')
        self.assertEqual(reaction_response.status_code, 200)
        metabolite_response = self.client.patch('/cobra/metabolites/', {
            'id': info['metabolites'][0].id,
            'name': 'test'
        }, content_type='application/json')
        self.assertEqual(metabolite_response.status_code, 200)

    def test_cobra_url_delete(self):
        info = self._create_model()
        model_response = self.client.delete('/cobra/models/', {
            'id': info['models'][0].id,
        }, content_type='application/json')
        self.assertEqual(model_response.status_code, 204)
        reaction_response = self.client.delete('/cobra/reactions/', {
            'id': info['reactions'][0].id,
        }, content_type='application/json')
        self.assertEqual(reaction_response.status_code, 204)
        metabolite_response = self.client.delete('/cobra/metabolites/', {
            'id': info['metabolites'][0].id,
        }, content_type='application/json')
        self.assertEqual(metabolite_response.status_code, 204)

    def test_cobra_url_get(self):
        info = self._create_model()
        model_response = self.client.get('/cobra/models/', dict(id=info['models'][0].id), content_type='application/json')
        self.assertEqual(model_response.status_code, 200)
        self.assertEqual(json.loads(model_response.content)['identifier'], 'example_model')
        models_response = self.client.get('/cobra/models/', content_type='application/json')
        self.assertEqual(models_response.status_code, 200)
        self.assertEqual(len(json.loads(models_response.content)['models']), 1)
        reaction_response = self.client.get(
            '/cobra/reactions/', dict(id=info['reactions'][0].id), content_type='application/json')
        self.assertEqual(reaction_response.status_code, 200)
        self.assertEqual(json.loads(reaction_response.content)['identifier'], '3OAS140')
        reactions_response = self.client.get('/cobra/reactions/', content_type='application/json')
        self.assertEqual(reactions_response.status_code, 200)
        self.assertEqual(len(json.loads(reactions_response.content)['reactions']), 1)
        metabolite_response = self.client.get(
            '/cobra/metabolites/', dict(id=info['metabolites'][0].id), content_type='application/json')
        self.assertEqual(metabolite_response.status_code, 200)
        self.assertEqual(json.loads(metabolite_response.content)['identifier'], 'ACP_c')
        metabolites_response = self.client.get('/cobra/metabolites/', content_type='application/json')
        self.assertEqual(metabolites_response.status_code, 200)
        self.assertEqual(len(json.loads(metabolites_response.content)['metabolites']), 6)
