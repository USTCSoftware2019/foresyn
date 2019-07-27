import json

from django.test import TestCase, Client
from django.contrib.auth.models import User

from .models import CobraModel, CobraReaction, CobraMetabolite
from .urls import ENABLE_API


class CObraWrapperViewTests(TestCase):
    pass


if ENABLE_API:
    class CobraWrapperApiTests(TestCase):
        def _create_user_and_login(self):
            user_info = {'username': 'test', 'password': 'testtest123'}
            user = User.objects.create_user(**user_info)
            self.client = Client()
            self.client.login(**user_info)
            return user

        def _create_models(self, user):
            """Examples in cobra doc to build a model"""
            metabolites = [
                CobraMetabolite(
                    cobra_id='ACP_c',
                    formula='C11H21N2O7PRS',
                    name='acyl-carrier-protein',
                    compartment='c',
                    owner=user
                ),
                CobraMetabolite(
                    cobra_id='3omrsACP_c',
                    formula='C25H45N2O9PRS',
                    name='3-Oxotetradecanoyl-acyl-carrier-protein',
                    compartment='c',
                    owner=user
                ),
                CobraMetabolite(
                    cobra_id='co2_c',
                    formula='CO2',
                    name='CO2',
                    compartment='c',
                    owner=user
                ),
                CobraMetabolite(
                    cobra_id='malACP_c',
                    formula='C14H22N2O10PRS',
                    name='Malonyl-acyl-carrier-protein',
                    compartment='c',
                    owner=user
                ),
                CobraMetabolite(
                    cobra_id='h_c',
                    formula='H',
                    name='H',
                    compartment='c',
                    owner=user
                ),
                CobraMetabolite(
                    cobra_id='ddcaACP_c',
                    formula='C23H43N2O8PRS',
                    name='Dodecanoyl-ACP-n-C120ACP',
                    compartment='c',
                    owner=user
                )
            ]
            for metabolite in metabolites:
                metabolite.save()

            reaction = CobraReaction.objects.create(
                cobra_id='3OAS140',
                name='3 oxoacyl acyl carrier protein synthase n C140 ',
                subsystem='Cell Envelope Biosynthesis',
                lower_bound=0,
                upper_bound=1000,
                coefficients=[-1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                gene_reaction_rule='( STM2378 or STM1197 )',
                owner=user
            )
            reaction.metabolites.set(metabolites)

            model = CobraModel.objects.create(
                cobra_id='example_model',
                objective='3OAS140',
                owner=user
            )
            model.reactions.set([reaction])

            return {
                'models': [model],
                'reactions': [reaction],
                'metabolites': metabolites
            }

        def test_set_post_and_get_ok(self):
            self._create_user_and_login()

            metabolite_0_response = self.client.post('/cobra/api/metabolites/', dict(
                cobra_id='ACP_c',
                formula='C11H21N2O7PRS',
                name='acyl-carrier-protein',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_0_response.status_code, 201)
            metabolite_0_id = json.loads(metabolite_0_response.content)['id']
            metabolite_1_response = self.client.post('/cobra/api/metabolites/', dict(
                cobra_id='3omrsACP_c',
                formula='C25H45N2O9PRS',
                name='3-Oxotetradecanoyl-acyl-carrier-protein',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_1_response.status_code, 201)
            metabolite_1_id = json.loads(metabolite_1_response.content)['id']
            metabolite_2_response = self.client.post('/cobra/api/metabolites/', dict(
                cobra_id='co2_c',
                formula='CO2',
                name='CO2',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_2_response.status_code, 201)
            metabolite_2_id = json.loads(metabolite_2_response.content)['id']
            metabolite_3_response = self.client.post('/cobra/api/metabolites/', dict(
                cobra_id='malACP_c',
                formula='C14H22N2O10PRS',
                name='Malonyl-acyl-carrier-protein',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_3_response.status_code, 201)
            metabolite_3_id = json.loads(metabolite_3_response.content)['id']
            metabolite_4_response = self.client.post('/cobra/api/metabolites/', dict(
                cobra_id='h_c',
                formula='H',
                name='H',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_4_response.status_code, 201)
            metabolite_4_id = json.loads(metabolite_4_response.content)['id']
            metabolite_5_response = self.client.post('/cobra/api/metabolites/', dict(
                cobra_id='ddcaACP_c',
                formula='C23H43N2O8PRS',
                name='Dodecanoyl-ACP-n-C120ACP',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_5_response.status_code, 201)
            metabolite_5_id = json.loads(metabolite_5_response.content)['id']
            metabolite_set_response = self.client.get('/cobra/api/metabolites/', content_type='application/json')
            self.assertEqual(len(json.loads(metabolite_set_response.content)['all']), 6)

            reaction_response = self.client.post('/cobra/api/reactions/', dict(
                cobra_id='3OAS140',
                name='3 oxoacyl acyl carrier protein synthase n C140 ',
                subsystem='Cell Envelope Biosynthesis',
                lower_bound=0,
                upper_bound=1000,
                metabolites=[
                    metabolite_0_id, metabolite_1_id, metabolite_2_id, metabolite_3_id, metabolite_4_id,
                    metabolite_5_id
                ],
                coefficients=[-1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                gene_reaction_rule='( STM2378 or STM1197 )'
            ), content_type='application/json')
            self.assertEqual(reaction_response.status_code, 201)
            reaction_id = json.loads(reaction_response.content)['id']
            reaction_set_response = self.client.get('/cobra/api/reactions/', content_type='application/json')
            self.assertEqual(len(json.loads(reaction_set_response.content)['all']), 1)

            model_response = self.client.post('/cobra/api/models/', dict(
                cobra_id='example_model',
                objective='3OAS140',
                reactions=[reaction_id]
            ), content_type='application/json')
            self.assertEqual(model_response.status_code, 201)
            model_id = json.loads(model_response.content)['id']
            model = CobraModel.objects.get(id=model_id)
            cobra_model = model.build()
            self.assertTrue(
                str(cobra_model.objective.expression) in [
                    '-1.0*3OAS140_reverse_65ddc + 1.0*3OAS140',
                    '1.0*3OAS140 - 1.0*3OAS140_reverse_65ddc'
                ]
            )
            self.assertEqual(str(cobra_model.objective.direction), 'max')
            model_set_response = self.client.get('/cobra/api/models/', content_type='application/json')
            self.assertEqual(len(json.loads(model_set_response.content)['all']), 1)

        def test_set_post_failure(self):
            self._create_user_and_login()

            metabolite_response = self.client.post('/cobra/api/metabolites/', dict(
                formula='C11H21N2O7PRS',
                name='acyl-carrier-protein',
                compartment='c'
            ), content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 400)
            self.assertEqual(list(json.loads(metabolite_response.content)['content'].keys()), ['cobra_id'])

            reaction_response = self.client.post('/cobra/api/reactions/', dict(
                name='3 oxoacyl acyl carrier protein synthase n C140 ',
                subsystem='Cell Envelope Biosynthesis',
                lower_bound=0,
                upper_bound=1000,
                coefficients=[-1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                gene_reaction_rule='( STM2378 or STM1197 )'
            ), content_type='application/json')
            self.assertEqual(reaction_response.status_code, 400)
            self.assertEqual(list(json.loads(reaction_response.content)['content'].keys()), ['cobra_id'])

            model_response = self.client.post('/cobra/api/models/', dict(
                objective='3OAS140',
            ), content_type='application/json')
            self.assertEqual(model_response.status_code, 400)
            self.assertEqual(list(json.loads(model_response.content)['content'].keys()), ['cobra_id'])

        def test_object_patch_ok(self):
            user = self._create_user_and_login()
            info = self._create_models(user)

            model_response = self.client.patch('/cobra/api/models/{}/'.format(info['models'][0].id), {
                'objective': 'test'
            }, content_type='application/json')
            self.assertEqual(model_response.status_code, 200)

            reaction_response = self.client.patch('/cobra/api/reactions/{}/'.format(info['reactions'][0].id), {
                'coefficients': [1, 1, 1, 1, 1, 1]
            }, content_type='application/json')
            self.assertEqual(reaction_response.status_code, 200)

            metabolite_response = self.client.patch('/cobra/api/metabolites/{}/'.format(info['metabolites'][0].id), {
                'name': 'test'
            }, content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 200)

        def test_object_patch_failure(self):
            user = self._create_user_and_login()
            info = self._create_models(user)

            model_response = self.client.patch('/cobra/api/models/{}/'.format('7777777'), {
                'objective': 'test'
            }, content_type='application/json')
            self.assertEqual(model_response.status_code, 404)
            model_response = self.client.patch('/cobra/api/models/{}/'.format(info['models'][0].id), {
                'objective': 'test' * 13
            }, content_type='application/json')
            self.assertEqual(model_response.status_code, 400)
            self.assertEqual(json.loads(model_response.content)['type'], 'validation_error')

            reaction_response = self.client.patch('/cobra/api/reactions/{}/'.format('7777777'), {
                'coefficients': [1, 1, 1, 1, 1, 1]
            }, content_type='application/json')
            self.assertEqual(reaction_response.status_code, 404)
            reaction_response = self.client.patch('/cobra/api/reactions/{}/'.format(info['reactions'][0].id), {
                'coefficients': {}
            }, content_type='application/json')
            self.assertEqual(reaction_response.status_code, 400)
            self.assertEqual(json.loads(reaction_response.content)['type'], 'validation_error')

            metabolite_response = self.client.patch('/cobra/api/metabolites/{}/'.format('7777777'), {
                'name': 'test'
            }, content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 404)
            metabolite_response = self.client.patch('/cobra/api/metabolites/{}/'.format(info['metabolites'][0].id), {
                'name': 'test' * 13
            }, content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 400)
            self.assertEqual(json.loads(metabolite_response.content)['type'], 'validation_error')

        def test_object_delete_ok(self):
            user = self._create_user_and_login()
            info = self._create_models(user)

            model_response = self.client.delete(
                '/cobra/api/models/{}/'.format(info['models'][0].id), content_type='application/json')
            self.assertEqual(model_response.status_code, 204)

            reaction_response = self.client.delete(
                '/cobra/api/reactions/{}/'.format(info['reactions'][0].id), content_type='application/json')
            self.assertEqual(reaction_response.status_code, 204)

            metabolite_response = self.client.delete(
                '/cobra/api/metabolites/{}/'.format(info['metabolites'][0].id), content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 204)

        def test_object_delete_failure(self):
            user = self._create_user_and_login()
            self._create_models(user)

            model_response = self.client.delete(
                '/cobra/api/models/{}/'.format('7777777'), content_type='application/json')
            self.assertEqual(model_response.status_code, 404)

            reaction_response = self.client.delete(
                '/cobra/api/reactions/{}/'.format('7777777'), content_type='application/json')
            self.assertEqual(reaction_response.status_code, 404)

            metabolite_response = self.client.delete(
                '/cobra/api/metabolites/{}/'.format('7777777'), content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 404)

        def test_object_get_ok(self):
            user = self._create_user_and_login()
            info = self._create_models(user)

            model_response = self.client.get(
                '/cobra/api/models/{}/'.format(info['models'][0].id), content_type='application/json')
            self.assertEqual(model_response.status_code, 200)
            self.assertEqual(json.loads(model_response.content)['cobra_id'], 'example_model')

            reaction_response = self.client.get(
                '/cobra/api/reactions/{}/'.format(info['reactions'][0].id), content_type='application/json')
            self.assertEqual(reaction_response.status_code, 200)
            self.assertEqual(json.loads(reaction_response.content)['cobra_id'], '3OAS140')

            metabolite_response = self.client.get(
                '/cobra/api/metabolites/{}/'.format(info['metabolites'][0].id), content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 200)
            self.assertEqual(json.loads(metabolite_response.content)['cobra_id'], 'ACP_c')

        def test_object_get_failure(self):
            user = self._create_user_and_login()
            self._create_models(user)

            model_response = self.client.get(
                '/cobra/api/models/{}/'.format('7777777'), content_type='application/json')
            self.assertEqual(model_response.status_code, 404)

            reaction_response = self.client.get(
                '/cobra/api/reactions/{}/'.format('7777777'), content_type='application/json')
            self.assertEqual(reaction_response.status_code, 404)

            metabolite_response = self.client.get(
                '/cobra/api/metabolites/{}/'.format('7777777'), content_type='application/json')
            self.assertEqual(metabolite_response.status_code, 404)

        def test_object_computation_post_ok(self):
            user = self._create_user_and_login()
            info = self._create_models(user)

            fba_response = self.client.post(
                '/cobra/api/models/{}/fba/'.format(info['models'][0].id), {}, content_type='application/json')
            self.assertEqual(json.loads(fba_response.content), {
                "objective_value": 0.0,
                "status": "optimal",
                "fluxes": {"3OAS140": 0.0},
                "shadow_prices": {
                    "ACP_c": -1.0, "3omrsACP_c": 0.0, "co2_c": 0.0, "malACP_c": 0.0, "h_c": 0.0, "ddcaACP_c": 0.0
                }
            })

            fva_response = self.client.post('/cobra/api/models/{}/fva/'.format(info['models'][0].id), {
                'reaction_list': [info['reactions'][0].id]
            }, content_type='application/json')
            self.assertEqual(
                json.loads(fva_response.content), {"minimum": {"3OAS140": 0.0}, "maximum": {"3OAS140": 0.0}})

        def test_object_computation_post_failure(self):
            user = self._create_user_and_login()
            info = self._create_models(user)

            fba_response = self.client.post(
                '/cobra/api/models/{}/fba/'.format('7777777'), {}, content_type='application/json')
            self.assertEqual(fba_response.status_code, 404)

            fva_response = self.client.post('/cobra/api/models/{}/fva/'.format('7777777'), {
                'reaction_list': [info['reactions'][0].id]
            }, content_type='application/json')
            self.assertEqual(fva_response.status_code, 404)
            fva_response = self.client.post('/cobra/api/models/{}/fva/'.format(info['models'][0].id), {
                'reaction_list': ['7777777']
            }, content_type='application/json')
            self.assertEqual(fva_response.status_code, 400)
            self.assertEqual(json.loads(fva_response.content)['type'], 'validation_error')

            test_response = self.client.post(
                '/cobra/api/models/{}/test/'.format(info['models'][0].id), {}, content_type='application/json')
            self.assertEqual(test_response.status_code, 404)

        def test_not_login_get_or_post(self):
            self.client = Client()

            get_model = self.client.get('/cobra/api/models/', content_type='application/json')
            self.assertEqual(get_model.status_code, 403)
            post_model = self.client.post('/cobra/api/models/', content_type='application/json')
            self.assertEqual(post_model.status_code, 403)

            get_reaction = self.client.get('/cobra/api/reactions/', content_type='application/json')
            self.assertEqual(get_reaction.status_code, 403)
            post_reaction = self.client.post('/cobra/api/reactions/', content_type='application/json')
            self.assertEqual(post_reaction.status_code, 403)

            get_metabolite = self.client.get('/cobra/api/metabolites/', content_type='application/json')
            self.assertEqual(get_metabolite.status_code, 403)
            post_metabolite = self.client.post('/cobra/api/metabolites/', content_type='application/json')
            self.assertEqual(post_metabolite.status_code, 403)
