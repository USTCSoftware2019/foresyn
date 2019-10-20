from .models import Regulation
from django.core.exceptions import ObjectDoesNotExist
from tt import BooleanExpression
from abc import ABCMeta, abstractmethod


class GeneRegulation:
    """
    An interface to do pre-treatment on cobra_model before doing FBA.
    iMC1010 Regulation of Gene Expression is used for this.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def gene_regulation(self, cobra_model, shadow_price: dict):
        for gene in cobra_model.genes:
            try:
                regulation = Regulation.objects.get(bNum=gene.id)
            except ObjectDoesNotExist:
                continue
            if not self.__check(regulation, cobra_model, shadow_price):
                gene.knock_out()

    @staticmethod
    def __check(self, regulation, cobra_model, shadow_price):
        exp = BooleanExpression(regulation.rule)
        tokens = exp.symbols
        value = []
        for i in tokens:
            if i.find('less_than') != -1:
                if shadow_price[i[0:i.find('less_than')]] < 0:
                    value.append(True)
                else:
                    value.append(False)
            elif i.find('more_than') != -1:
                if shadow_price[i[0:i.find('more_than')]] > 0:
                    value.append(True)
                else:
                    value.append(False)
            else:
                if self.__check_gene(cobra_model, i):
                    value.append(True)
                else:
                    value.append(False)
        return exp.evaluate(**dict(zip(tokens, value)))

    @staticmethod
    def __check_gene(cobra_model, gene):
        try:
            gene_bnum = Regulation.objects.get(name=gene).bNum
        except ObjectDoesNotExist:
            return False
        try:
            cobra_model.genes.get_by_id(gene_bnum)
        except KeyError:
            return False
        return True
