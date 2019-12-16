from django.core.management.base import BaseCommand
import xlrd

from biobricks.models import Biobrick


def main(biobrick_path):
    book = xlrd.open_workbook(biobrick_path)
    sheet = book.sheet_by_index(0)
    for row_index in range(1, 20):  # sheet.nrows):
        part_name = sheet.cell(row_index, 0).value
        description = sheet.cell(row_index, 1).value
        keywords = sheet.cell(row_index, 2).value
        uses = sheet.cell(row_index, 3).value

        Biobrick.objects.create(part_name=part_name,
                                description=description,
                                keywords=keywords,
                                uses=uses)


class Command(BaseCommand):
    help = 'Parse biobrick from csv'

    def add_arguments(self, parser):
        parser.add_argument('biobrick_path', type=str)

    def handle(self, **kwargs):
        main(kwargs['biobrick_path'])
