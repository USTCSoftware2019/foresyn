import os
import subprocess

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from backend.settings import BASE_DIR
from cobra_wrapper.models import CobraModel, CobraReaction, CobraMetabolite


def main():
    try:
        os.remove(os.path.join(BASE_DIR, 'db.sqlite3'))
    except FileNotFoundError:
        pass
    subprocess.run([os.path.join(BASE_DIR, 'manage.py'), 'migrate'])

    user = User.objects.create_superuser('test', '', 'test123456')

    metabolites = [
        CobraMetabolite.objects.create(
            cobra_id='ACP_c',
            formula='C11H21N2O7PRS',
            name='acyl-carrier-protein',
            compartment='c',
            charge='1',
            owner=user
        ),
        CobraMetabolite.objects.create(
            cobra_id='3omrsACP_c',
            formula='C25H45N2O9PRS',
            name='3-Oxotetradecanoyl-acyl-carrier-protein',
            compartment='c',
            charge='1',
            owner=user
        ),
        CobraMetabolite.objects.create(
            cobra_id='co2_c',
            formula='CO2',
            name='CO2',
            compartment='c',
            charge='1',
            owner=user
        ),
        CobraMetabolite.objects.create(
            cobra_id='malACP_c',
            formula='C14H22N2O10PRS',
            name='Malonyl-acyl-carrier-protein',
            compartment='c',
            charge='1',
            owner=user
        ),
        CobraMetabolite.objects.create(
            cobra_id='h_c',
            formula='H',
            name='H',
            compartment='c',
            charge='1',
            owner=user
        ),
        CobraMetabolite.objects.create(
            cobra_id='ddcaACP_c',
            formula='C23H43N2O8PRS',
            name='Dodecanoyl-ACP-n-C120ACP',
            compartment='c',
            charge='1',
            owner=user
        )
    ]

    reaction = CobraReaction.objects.create(
        cobra_id='3OAS140',
        name='3 oxoacyl acyl carrier protein synthase n C140 ',
        subsystem='Cell Envelope Biosynthesis',
        lower_bound=0,
        upper_bound=1000,
        coefficients='-1.0 -1.0 -1.0 1.0 1.0 1.0',
        gene_reaction_rule='( STM2378 or STM1197 )',
        owner=user
    )
    reaction.metabolites.set(metabolites)

    model = CobraModel.objects.create(
        cobra_id='example_model',
        name='test',
        objective='3OAS140',
        owner=user
    )
    model.reactions.set([reaction])


class Command(BaseCommand):
    help = 'Init test database for GUI test'

    def handle(self, **kwargs):
        main()
