from django.test import TestCase

from . import models as cobra_models


class CobraWrapperTest(TestCase):
    def test_model_build(self):
        """Example on cobra doc to build a model"""
        test_metabolite_0 = cobra_models.CobraMetabolite(
            base='ACP_c',
            formula='C11H21N2O7PRS',
            name='acyl-carrier-protein',
            compartment='c'
        )
        test_metabolite_1 = cobra_models.CobraMetabolite(
            base='3omrsACP_c',
            formula='C25H45N2O9PRS',
            name='3-Oxotetradecanoyl-acyl-carrier-protein',
            compartment='c'
        )
        test_metabolite_2 = cobra_models.CobraMetabolite(
            base='co2_c', formula='CO2', name='CO2', compartment='c'
        )
        test_metabolite_3 = cobra_models.CobraMetabolite(
            base='malACP_c',
            formula='C14H22N2O10PRS',
            name='Malonyl-acyl-carrier-protein',
            compartment='c'
        )
        test_metabolite_4 = cobra_models.CobraMetabolite(
            base='h_c', formula='H', name='H', compartment='c'
        )
        test_metabolite_5 = cobra_models.CobraMetabolite(
            base='ddcaACP_c',
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
            base='3OAS140',
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
            base='example_model',
            objective='3OAS140'
        )
        test_model.save()
        test_model.reactions.set([test_reaction])
        test_model.save()
        test_cobra_model = test_model.build()
        self.assertTrue(
            str(test_cobra_model.objective.expression) in [
                '-1.0*3OAS140_reverse_65ddc + 1.0*3OAS140',
                '1.0*3OAS140 - 1.0*3OAS140_reverse_65ddc'
            ]
        )
        self.assertEqual(str(test_cobra_model.objective.direction), 'max')
