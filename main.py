
import logging
import sys
sys.path.append('../agutils/')

from file_utils import FileUtils


class Node(object):
    def __init__(self):
        self.id_medline = ''
        self.year = -1
        self.descriptors_names = []


class Edge(object):
    def __init__(self):
        self.source = -1
        self.target = -1
        self.weight = 0


class Graph(object):
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, article: list):
        n = Node()
        n.id_medline = article[0].id_medline
        n.year = article[0].year
        n.descriptors_names = [a.names.replace(',', ';') for a in article]

        self.nodes.append(n)

    def add_edge(self, source: Node, target: Node):
        e = Edge()
        e.source = source
        e.target = target
        e.common_descriptors_names = self._get_common_descriptors_names(e)
        e.weight = len(e.common_descriptors_names)
        if e.weight > 0:
            self.edges.append(e)

    def _get_common_descriptors_names(self, edge: Edge):
        source_descriptors_names = {d for d in edge.source.descriptors_names}
        target_descriptors_names = {d for d in edge.target.descriptors_names}
        return list(source_descriptors_names.intersection(target_descriptors_names))

    def save(self, path_graph: str):
        result_file = open(path_graph, 'w')
        result_file.write('nodedef>name VARCHAR,year INTEGER,descriptors VARCHAR\n')
        for n in self.nodes:
            result_file.write(','.join([n.id_medline, str(n.year), '#'.join([d for d in n.descriptors_names])]))
            result_file.write('\n')

        result_file.write('edgedef>Source,Target,Weight DOUBLE,common_descriptors_names VARCHAR\n')
        for e in self.edges:
            result_file.write(','.join([e.source.id_medline, e.target.id_medline, str(e.weight), '#'.join([e for e in e.common_descriptors_names])]))
            result_file.write('\n')


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
    def filter_descriptor(descriptor: Descriptor, invalid_descriptors: list):
        if descriptor.names in [inv.names for inv in invalid_descriptors]:
            logging.basicConfig(filename='data/removed_descriptors.tsv', filemode='w', format='%(message)s')
            logging.warning(str(descriptor))
            return True
        else:
            return False


if __name__ == "__main__":
    FILE_DESCRIPTORS = 'data/descriptors.tsv'
    FILE_INVALID_DESCRIPTORS = 'data/invalid_descriptors.tsv'
    FILE_RESULT_GRAPH = 'graph.gdf'

    descriptors = FileUtils.get_models_from_path_csv(FILE_DESCRIPTORS, sep='\t', model=Descriptor)
    print('há %d descritores' % (len(descriptors)))
    invalid_descriptors = FileUtils.get_models_from_path_csv(FILE_INVALID_DESCRIPTORS, sep='\t', model=InvalidDescriptor)

    # add descritor with empty name
    invalid_descriptors.append(Descriptor(**{'names': ''}))

    descriptors = [d for d in descriptors if not DescriptorManager.filter_descriptor(d, invalid_descriptors)]
    print('há %d descritores, após remoção de inválidos' % len(descriptors))

    articles = {}
    for d in descriptors:
        if d.id_medline not in articles:
            articles[d.id_medline] = [d]
        else:
            articles[d.id_medline].append(d)
    print('há %d artigos' % len(articles))
    
    g = Graph()
    for a in articles:
        g.add_node(articles.get(a))

    for ind_i, i in enumerate(g.nodes):
        for ind_j, j in enumerate(g.nodes):
            if ind_j > ind_i:
                print('\ri: %d\tj: %d' % (ind_i + 1, ind_j + 1), end='')
                g.add_edge(i, j)
    
    g.save(FILE_RESULT_GRAPH)
