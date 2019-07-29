#!/usr/bin/python3
import os


class GDFNode(object):
    def __init__(self, **kargs):
        self.name = kargs.get('name', '')
        self.label = kargs.get('label', '')
        self.year = kargs.get('year', '0')
        self.module = kargs.get('module', '0')
        self.coefficient = kargs.get('coefficient', '0.0')


class GDFManager(object):
    def __init__(self):
        self.nodes = []
        self.module_to_descriptors_freq = {}

    def count_descriptors(self):
        for node in self.nodes:
            if node.module not in self.module_to_descriptors_freq:
                self.module_to_descriptors_freq[node.module] = {}

            for descriptor in node.label.split('#'):
                if descriptor not in self.module_to_descriptors_freq[node.module]:
                    self.module_to_descriptors_freq[node.module][descriptor] = 1
                else:
                    self.module_to_descriptors_freq[node.module][descriptor] += 1

    def save_descriptors_count(self, path_descriptors_count: str):
        result_file = open(path_descriptors_count, 'w')
        result_file.write('CLASSE,FREQUENCIA:DESCRITOR\n')
        for module in sorted(self.module_to_descriptors_freq):
            result_file.write(module + ',')
            df = self.module_to_descriptors_freq.get(module)
            sdf = [(k, df[k]) for k in sorted(df, key=df.get, reverse=True)]
            for d, f in sdf:
                result_file.write(':'.join([str(f), d]))
                result_file.write(',')
            result_file.write('\n')
        result_file.close()


if __name__ == "__main__":
    # configuracoes basicas
    PATH_FOLDER_GDF = '/home/rafael/Temp/rev-saude/por_ano/t2/gdf_modules/'

    gdfs_paths = sorted([PATH_FOLDER_GDF + f for f in os.listdir(PATH_FOLDER_GDF) if f.endswith('.gdf')])

    for g in gdfs_paths:
        print('file %s' % g)
        arq_gdf = open(g)
        vertices = []
        temp_vertices = [n.strip() for n in arq_gdf]
        temp_vertices.pop(0)
        temp_vertices = [n for n in temp_vertices if len(n.split(',')) == 5]
        header_vertices = ['name', 'label', 'year', 'module', 'coefficient']
        for n in temp_vertices:
            attributes = n.split(',')
            dargs = {}
            for i, na in enumerate(attributes):
                dargs[header_vertices[i]] = attributes[i]
            v = GDFNode(**dargs)
            vertices.append(v)
        arq_gdf.close()
        
        gdf_manager = GDFManager()
        gdf_manager.nodes = vertices
        gdf_manager.count_descriptors()
        gdf_manager.save_descriptors_count(PATH_FOLDER_GDF + 'classes_' + g.split('/')[-1].split('.')[0] + '.csv')
    