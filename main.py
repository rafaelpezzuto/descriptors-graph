#!/usr/bin/python3
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
        self.relative_weight = 0.0
        self.simmetrical_relative_weight = 0.0


class Graph(object):
    def __init__(self):
        self.nodes = []
        self.edges = []

    def is_node_in_edges_list(self, node_code: str, k):
        for e in self.edges:
            if e.weight >= k:
                if e.source.id_medline == node_code or e.target.id_medline == node_code:
                    return True
        return False


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
        e.common_descriptors_names, number_of_distinct_descriptors, max_number_of_descriptors = self._get_common_descriptors_names(e)
        e.weight = len(e.common_descriptors_names)
        if e.weight > 0:
            e.relative_weight = e.weight / max_number_of_descriptors
            e.simmetrical_relative_weight = e.weight / number_of_distinct_descriptors
            self.edges.append(e)

    def _get_common_descriptors_names(self, edge: Edge):
        source_descriptors_names = {d for d in edge.source.descriptors_names}
        target_descriptors_names = {d for d in edge.target.descriptors_names}
        distinct_descriptors_names = source_descriptors_names.union(target_descriptors_names)
        return list(source_descriptors_names.intersection(target_descriptors_names)), len(distinct_descriptors_names), len(max(source_descriptors_names, target_descriptors_names))

    def save(self, path_graph: str, k: int, modo='por_ano'):
        result_file = open(path_graph, 'w')
        result_file.write('nodedef>name VARCHAR,year INTEGER,descriptors VARCHAR\n')
        n_nodes = 0
        n_edges = 0
        for n in self.nodes:
            if self.is_node_in_edges_list(n.id_medline, k):
                result_file.write(','.join([n.id_medline, str(n.year), '#'.join([d for d in n.descriptors_names])]))
                result_file.write('\n')
                n_nodes += 1

        result_file.write('edgedef>Source,Target,Weight DOUBLE,R DOUBLE,S DOUBLE,Label VARCHAR\n')
        for e in self.edges:
            if e.weight >= k:
                result_file.write(','.join([e.source.id_medline, e.target.id_medline, str(e.weight), str(e.relative_weight), str(e.simmetrical_relative_weight), '#'.join([e for e in e.common_descriptors_names])]))
                result_file.write('\n')
                n_edges += 1

        if modo == 'por_ano':
            print(str(self.nodes[0].year), str(n_nodes), str(n_edges))
        else:
            print(str(k), str(n_nodes), str(n_edges))


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
    K = int(sys.argv[1])
    POR_ANO = True

    BASE_FOLDER = '/home/rafael/Temp/rev-saude/'
    FILE_DESCRIPTORS = BASE_FOLDER + 'data/descriptors.tsv'
    FILE_INVALID_DESCRIPTORS = BASE_FOLDER + 'data/invalid_descriptors.tsv'
    FILE_RESULT_GRAPH = BASE_FOLDER + 'graph_w' + str(K) + '_'        
    FILE_LOG = BASE_FOLDER + 'data/removed_descriptors.tsv'

    descriptors = FileUtils.get_models_from_path_csv(FILE_DESCRIPTORS, sep='\t', model=Descriptor)
    invalid_descriptors = FileUtils.get_models_from_path_csv(FILE_INVALID_DESCRIPTORS, sep='\t', model=InvalidDescriptor)

    # add descritor with empty name
    invalid_descriptors.append(Descriptor(**{'names': ''}))

    descriptors = [d for d in descriptors if not DescriptorManager.filter_descriptor(d, invalid_descriptors, FILE_LOG)]

    if not POR_ANO:
        FILE_RESULT_GRAPH = FILE_RESULT_GRAPH[:-1] + '.gdf'
        articles = {}
        for d in descriptors:
            if d.id_medline not in articles:
                articles[d.id_medline] = [d]
            else:
                articles[d.id_medline].append(d)

        g = Graph()
        for a in articles:
            g.add_node(articles.get(a))

        for ind_i, i in enumerate(g.nodes):
            for ind_j, j in enumerate(g.nodes):
                if ind_j > ind_i:
                    g.add_edge(i, j)

        g.save(FILE_RESULT_GRAPH, K, modo="none")
    else:
        year2articles = {}
        for d in descriptors:
            if d.year not in year2articles:
                year2articles[d.year] = {d.id_medline: [d]}
            else:
                if d.id_medline not in year2articles[d.year]:
                    year2articles[d.year][d.id_medline] = [d]
                else:
                    year2articles[d.year][d.id_medline].append(d)
        print('há %d artigos' % len(year2articles))

        for year in year2articles:    
            gy = Graph()
            
            for id_medline in year2articles[year]:
                gy.add_node(year2articles.get(year).get(id_medline))

            for ind_i, i in enumerate(gy.nodes):
                for ind_j, j in enumerate(gy.nodes):
                    if ind_j > ind_i:
                        gy.add_edge(i, j)
            
            gy.save(FILE_RESULT_GRAPH + str(year) + '.gdf', K)
