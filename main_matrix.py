#!/usr/bin/python3
import logging
import sys
sys.path.append('../agutils/')

from file_utils import FileUtils


class Descriptor(object):

    def __init__(self, **kargs):
        self.id_medline = kargs.get('ID_Medline', '').lower()
        self.year = int(kargs.get('Ano', -1))
        self.names = kargs.get('Descritores', kargs.get('Descritor', '')).lower()

    def __str__(self):
        return '\t'.join([self.id_medline, str(self.year), self.names])


class InvalidDescriptor(Descriptor):

    def __init__(self, **kargs):
        self.freq = kargs.get('Freq', -1)
        super().__init__(**kargs)


class DescriptorManager(object):

    @staticmethod
    def filter_descriptor(descriptor: Descriptor, invalid_descriptors: list, filename: str):
        if descriptor.names in [inv.names for inv in invalid_descriptors]:
            logging.basicConfig(filename=filename, filemode='w', format='%(message)s')
            logging.warning(str(descriptor))
            return True
        else:
            return False


if __name__ == "__main__":

    # configuracoes basicas
    BASE_FOLDER = '/home/rafael/Temp/rev-saude/'
    FILE_DESCRIPTORS = BASE_FOLDER + 'data/descriptors_no_edat.tsv'
    FILE_INVALID_DESCRIPTORS = BASE_FOLDER + 'data/invalid_descriptors.tsv'
    FILE_LOG = BASE_FOLDER + 'data/removed_descriptors.tsv'

    # le descritores
    descriptors = FileUtils.get_models_from_path_csv(FILE_DESCRIPTORS, sep='\t', model=Descriptor)

    # le descritores invalidos
    invalid_descriptors = FileUtils.get_models_from_path_csv(FILE_INVALID_DESCRIPTORS, sep='\t', model=InvalidDescriptor)

    # adiciona a lista de descritores invalidos descritor invalido com nome vazio
    invalid_descriptors.append(Descriptor(**{'names': ''}))

    # elimina descritores invalidos da lista de descritores
    descriptors = [d for d in descriptors if not DescriptorManager.filter_descriptor(d, invalid_descriptors, FILE_LOG)]

    # separa artigos por ano
    year2articles = {}
    for d in descriptors:
        if d.year not in year2articles:
            year2articles[d.year] = {d.id_medline: [d]}
        else:
            if d.id_medline not in year2articles[d.year]:
                year2articles[d.year][d.id_medline] = [d]
            else:
                year2articles[d.year][d.id_medline].append(d)
    
    # coleta descritores distintos
    distinct_descriptors = set()
    for year, articles in year2articles.items():
        for article_id, descriptors in articles.items():
            descriptors_names = [d.names for d in descriptors]
            distinct_descriptors.update(descriptors_names)

    # cria dicionario descritor: posicao na matriz
    distinct_descriptors_dict = {}
    for d in sorted(distinct_descriptors):
        distinct_descriptors_dict[d] = len(distinct_descriptors_dict)
        
    # monta matriz para cada artigo, por ano
    for year, articles in year2articles.items():
        result_file = open(BASE_FOLDER + str(year) + '.csv', 'w')
        for article_id, descriptors in articles.items():
            descriptors_names = sorted([d.names for d in descriptors])
            descriptors_positions = [distinct_descriptors_dict[name] for name in descriptors_names]

            # escreve cabecalho
            result_file.write('id,')
            for k in descriptors_names:
                result_file.write(k + ',')
            result_file.write(article_id + ',')

            # escreve valor do descritor
            for k in range(3439):
                if k in descriptors_positions:
                    result_file.write('1')
                else:
                    result_file.write('0')
                if k != 3438:
                    result_file.write(',')
                else:
                    result_file.write('\n')
        result_file.close()
