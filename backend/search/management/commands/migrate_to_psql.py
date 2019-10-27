from django.core.management.base import BaseCommand

from backend.psql import DBSession, engine
from bigg_database.management.commands.progressbar import print_progressbar
from bigg_database.models import Gene as mysqlGene
from bigg_database.models import Metabolite as mysqlMetabolite
from bigg_database.models import Model as mysqlModel
from bigg_database.models import Reaction as mysqlReaction
from biobricks.models import Biobrick as mysqlBiobrick
from search.models import Gene as psqlGene
from search.models import Metabolite as psqlMetabolite
from search.models import Model as psqlModel
from search.models import Reaction as psqlReaction
from search.models import Biobrick as psqlBiobrick


def main():
    session = DBSession()
    print('Migrating Model')
    current_process = 0
    total_count = mysqlModel.objects.count()

    for obj in mysqlModel.objects.all():
        print_progressbar(current_process, total_count)
        new_obj = psqlModel(django_orm_id=obj.id, bigg_id=obj.bigg_id)
        session.add(new_obj)
        current_process += 1
    print_progressbar(total_count, total_count)

    corresponding_model_map = {
        mysqlGene: psqlGene,
        mysqlMetabolite: psqlMetabolite,
        mysqlReaction: psqlReaction
    }

    for model_cls in [mysqlReaction, mysqlMetabolite, mysqlGene]:
        print('Migrating', model_cls._meta.verbose_name)
        current_process = 0
        total_count = model_cls.objects.count()
        corresponding_model = corresponding_model_map[model_cls]
        for obj in model_cls.objects.all():
            print_progressbar(current_process, total_count)
            new_obj = corresponding_model(django_orm_id=obj.id, bigg_id=obj.bigg_id, name=obj.name)
            session.add(new_obj)
            current_process += 1
        print_progressbar(total_count, total_count)

    print('Migrating Biobrick')
    current_process = 0
    total_count = mysqlBiobrick.objects.count()
    for obj in mysqlBiobrick.objects.all():
        print_progressbar(current_process, total_count)
        new_obj = psqlBiobrick(django_orm_id=obj.id, partname=obj.part_name, description=obj.description, keywords=obj.keywords)
        session.add(new_obj)
        current_process += 1
    print_progressbar(total_count, total_count)

    session.commit()
    session.close()


class Command(BaseCommand):
    help = 'Copy bigg_id and name from MySQL to PostgreSQL'

    def handle(self, **kwargs):
        main()
