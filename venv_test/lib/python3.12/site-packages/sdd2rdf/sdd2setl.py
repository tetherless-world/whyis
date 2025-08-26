
from jinja2 import Environment, PackageLoader, select_autoescape

import pandas as pd
import argparse
import numpy as np
import re
from setlr import isempty as empty
from slugify import slugify
import io
import puremagic
import json
import fnmatch
import rdflib
import uuid

def isempty(value):
    if isinstance(value,str):
        return len(value) == 0
    else:
        return empty(value)
    
base_context = {
    "void" : "http://rdfs.org/ns/void#",
    "csvw" : "http://www.w3.org/ns/csvw#",
    "sio": "http://semanticscience.org/resource/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "prov": "http://www.w3.org/ns/prov#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "np" : "http://www.nanopub.org/nschema#",
    "Attribute" : { "@id" : "rdf:type", "@type" : "@id"},
    "Entity" : { "@id" : "rdf:type", "@type" : "@id"},
    "attributeOf" : { "@id" : "sio:isAttributeOf", "@type" : "@id", "@reverse" : "sio:hasAttribute" },
    "Entity" : { "@id" : "rdf:type", "@type" : "@id"},
    "inRelationTo" : { "@id" : "sio:inRelationTo", "@type" : "@id"},
    "Role" : { "@id" : "sio:hasRole", "@type" : "@id"},
    "Time" : { "@id" : "sio:existsAt", "@type" : "@id"},
    "Unit" : { "@id" : "sio:hasUnit", "@type" : "@id"},
    "Value" : { "@id" : "sio:hasValue"},
    "hasStart" : { "@id" : "sio:hasStartTime"},
    "hasEnd" : { "@id" : "sio:hasEndTime"},
    "TimeInterval" : {"@id" : "sio:TimeInterval"},
    "wasDerivedFrom" : { "@id" : "prov:wasDerivedFrom", "@type" : "@id"},
    "wasGeneratedBy" : { "@id" : "prov:wasGeneratedBy", "@type" : "@id"},
    "a" : {"@id": "rdf:type"}
}



class SemanticDataDictionary:
    columns = None
    codebook = None
    resource_codebook = None
    context = None
    codemap = None
    timeline = None
    infosheet = None
    sdd_format = None
    sheets = None
    data = None
    data_type = None

    def __init__(self, sdd_path, prefix, data_type):
        self.sdd_path = sdd_path
        self.prefix = prefix
        self.data_type = data_type
        self.load()

    def _expand_codebook(self):
        codebook = dict(self.codebook)
        for key, value in self.codebook.items():
            for column in self.columns.keys():
                if key[0] != column and fnmatch.fnmatch(column, key[0]):
                    codebook[(column,key[1])] = value
        self.codebook = codebook

        resource_codebook = dict(self.resource_codebook)
        for key, value in self.resource_codebook.items():
            for column in self.columns.keys():
                if key != column and fnmatch.fnmatch(column, key):
                    resource_codebook[column] = value
        self.resource_codebook = resource_codebook

    def load(self):
        infosheet = self._get_table()
        self.infosheet = dict([(row.Attribute, row.Value)
                               for i, row in infosheet.iterrows()
                               if not isempty(row.Value)])

        codemap = self._get_table('Code Mapping')

        self.codemap = dict([(row.code, row.uri)
                               for i, row in codemap.iterrows()
                               if not isempty(row.uri)])

        codebook = self._get_table('Codebook')
        codebook = codebook.fillna('')
        self.codebook = dict([((row.Column, row.Code),
                                self._split_and_map(row.Class))
                               for i, row in codebook.iterrows()
                               if not isempty(row.Class)])
        self.resource_codebook = {}
        for i, row in codebook.iterrows():
            if not isempty(row.Resource):
                if row.Column not in self.resource_codebook:
                    self.resource_codebook[row.Column] = {}
                self.resource_codebook[row.Column][row.Code] = self.codemap.get(row.Resource,row.Resource)

        self.context = {}
        self.context.update(base_context)
        self.context['@base'] = self.prefix
        if 'Prefixes' in self.infosheet:
            prefixes = self._get_table('Prefixes')
            prefix_dict = dict([(str(row.prefix), row.url if row.url[0] != '{' else json.loads(row.url))
                                for i, row in prefixes.iterrows()
                                if not isempty(row.prefix) and not isempty(row.url)])
            self.prefixes = dict([(prefix, rdflib.Namespace(url))
                                  for (prefix, url) in prefix_dict.items()])
            self.context.update(prefix_dict)

        dm = self._get_table('Dictionary Mapping')
        self.columns = dict([(col.Column, col.dropna().to_dict())
                             for i, col in dm.iterrows()
                             if not isempty(col['Column'])])
        for key, col in self.columns.items():
            col['Column'] = col['Column'].strip()
        timeline = self._get_table('Timeline')
        for i, t in timeline.iterrows():
            if isempty(t.Name):
                continue
            if t.Name in self.columns:
                self.columns[t.Name].update(t.to_dict())
            else:
                self.columns[t.Name] = t.to_dict()
                self.columns[t.Name]['Column'] = t.Name
        self.column_templates = {}
        self.value_templates = {}
        for key, col in self.columns.items():
            col['children'] = []
        for key, col in self.columns.items():
            for annotation in ['Unit','Format','Role','Relation']:
                if annotation in col and not isempty(col[annotation]):
                    col[annotation] = self.codemap.get(col[annotation],col[annotation])
            for annotation in ['attributeOf','wasDerivedFrom','wasGeneratedBy', 'inRelationTo']:
                if annotation in col:
                    col[annotation] = self._split(col[annotation])
            for annotation in ['Attribute','Entity','Type']:
                if annotation in col and not isempty(col[annotation]):
                    col[annotation] = self._split_and_map(col[annotation])
#            et = element_templates[self.data_type]
#             column_id = slugify(col['Column'],separator="_")
#             parent = col.get('SelectorParent','__tree_root__')
#             if parent != '__tree_root__':
#                 self.columns[parent]['children'].append(col)
#                 col['parent_column'] = self.columns[parent]
#             selector = col.get('Selector', None)
# #            if parent is None:
# #                col['iterator'] = '[row]'
# #            else:
#             if 'Selector' in col:
#                 col['iterator'] = et['iterate_template']%(parent, selector)
#             else:
#                 col['iterator'] = et['iterate_template']
#             self.value_templates[column_id] = et['value_template']%col['Column']
#             self.column_templates[column_id] = et['column_template']%col['Column']
#             col['value_access'] = et['value'] % col['Column']
#            if not col['Column'].startswith('??') and not col['Column'].startswith('__'):
            self.value_templates[slugify(col['Column'],separator="_")] = "{{row.get('%s')}}"%col['Column']
            self.column_templates[slugify(col['Column'],separator="_")] = "{{slugify(str(row.get('%s')),separator='_',lowercase=False)}}"%col['Column']
            if not col['Column'].startswith('??'):
                col['@value'] = '{%s}'%slugify(col['Column'],separator="_")
            if 'Format' in col and not isempty(col['Format']):
                value_type = col['Format'].split("^^")
                if len(value_type) == 1:
                    col['@type'] = value_type[0]
                elif len(value_type) == 2:
                    col['@type'] = value_type[1]
                    if len(value_type[0]) > 0:
                        col['@value'] = value_type[0]
        # self.root_columns = [c for c in self.columns.values() if 'SelectorParent' not in c]
        # self.root_columns = [{
        #     'Column': '__tree_root__',
        #     'iterator': '[row]',
        #     'children': self.root_columns
        # }]
        # for col in self.root_columns + list(self.columns.values()):
        #     # create a @with statement to set the local scope for this subtree.
        #     if len(col['children']) > 0:
        #         col['leaves'] = []
        #         col['branches'] = []
        #         assignments = []
        #         variables = []
        #         for child in col['children']:
        #             if len(child['children']) > 0:
        #                 col['branches'].append(child)
        #             else:
        #                 col['leaves'].append(child)
        #                 if not child['Column'].startswith('??'):
        #                     variables.append("%s" % child['Column'])
        #                     assignments.append('%s[0] if len(%s) > 0 else None, ' % (child['iterator'].replace('\\','\\\\'), child['iterator'].replace('\\','\\\\')))
        #         col['with'] = ['('] + assignments + [') as ', ', '.join(variables)]
        #     del col['children']
        #         #print(col.get('Column',"root"))
        #         #print(col['with'])
        #         #print(col['leaves'])
        #         #print(col['branches'])

        # #print(json.dumps(self.root_columns, indent=4))

        self._expand_codebook()

        for col in self.columns.values():
            default = slugify(col['Column'],separator="_")+'_{i}'
            template = col.get('Template', '')
            #print(col['Column'], template)
            #if isempty(template):
            #    template = slugify(col['Column'],separator="_")+'_{i}'

            #template = re.sub(r'(:<=\{).*(:=\})',lambda x:str(slugify(x.group(0),separator="_")),template)
            #formatted_template = template.format(i='{{name}}',**self.column_templates)
            # if col['Column'] in self.resource_codebook:
            #     formatted_template = ''.join([
            #         "{% if '",
            #         col['Column'],
            #         "' in resource_codebook %}{{resource_codebook['",
            #         col['Column'],
            #         "'][",
            #         col['value_access'],
            #         "]}}{% else %}",
            #         formatted_template,
            #         "{% endif %}"])
            col['uri_template'] = template #formatted_template

            if '@value' in col:
                col['@value'] = col['@value'].format(i='{{name}}',**self.value_templates)

        self.column_types = dict([(col['Column'], col['Entity']) for col in self.columns.values()])

    loaders = {
        "text/csv" : pd.read_csv,
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': pd.read_excel,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': pd.read_excel
    }

    def _get_table(self, entry=None):
        if entry is not None:
            path = self.infosheet[entry]
            if path.startswith('#'):
                sheetname = path.split('#')[1]
                location = self.sdd_path
                local = True
            else:
                sheetname = None
                location = path
                local = False
        else:
            path = None
            location = self.sdd_path
            local = True
            sheetname = "InfoSheet"

        kwargs = {'dtype':str , 'keep_default_na' : False, 'na_values': ['']}
        if sheetname is not None:
            kwargs['sheet_name'] = sheetname

        if isinstance(location, io.IOBase):
            if self.data is None:
                self.data = location.read()
                formats = puremagic.from_string(self.data[:2048], mime=True)
                if len(formats) > 0:
                    self.sdd_format = formats
                else:
                    self.sdd_format = 'text/csv'
                #print("SDD is ",self.sdd_format)
            return self.loaders[self.sdd_format](io.BytesIO(self.data), **kwargs)
        else:
            if local:
                return pd.read_excel(location, **kwargs)
            else:
                return pd.read_csv(location, **kwargs)

    def _split(self, value):
        if value is None or isempty(value):
            return []
        result = re.split(r'\s*[,;&]\s*', value)
        return result

    def _split_and_map(self, value):
        if isempty(value):
            return []
        return [self.codemap.get(x,x) for x in self._split(value)]

# element_templates = {
#     'setl:XML': {
#         # How are we going to handle nested iteration?
#         'value_template' : "{{%s}}",
#         'value' : "%s",
#         'iterate_template' : "%s.xpath('%s')",
#         'column_template' : "{{slugify(str(%s),separator='_',lowercase=False)}}"
#     },
#     "setl:Excel" : {
#         'value_template' : "{{row.get('%s')}}",
#         'value' : "row.get('%s')",
#         'iterate_template' : "[row]",
#         'column_template' : "{{slugify(str(row.get('%s')),separator='_',lowercase=False)}}"
#     },
#     "csvw:Table" : {
#         'value_template' : "{{row.get('%s')}}",
#         'value' : "row.get('%s')",
#         'iterate_template' : "[row]",
#         'column_template' : "{{slugify(str(row.get('%s')),separator='_',lowercase=False)}}"
#     }
# }

file_types = {
    "text/csv" : "csvw:Table",
    "csv" : "csvw:Table",
#    "application/xml" : 'setl:XML',
#    'text/xml': 'setl:XML',
#    'xml' : 'setl:XML',
    "excel" : "setl:Excel",
    'application/vnd.ms-excel': "setl:Excel",
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': "setl:Excel",
}

def resolve(template, column_name, column_types, row, i, context, columns):
    if template is None or len(template.strip()) == 0:
        return uuid.uuid4().hex
    safe_values = dict([(key, slugify(str(value),separator='_',lowercase=False) )
                for key, value in row.to_dict().items()])
    result = template.format(i=i, uuid=uuid, **safe_values)
    return result

def sdd2setl(semantic_data_dictionary, prefix, datafile,
             format='csv', delimiter=',', sheetname=None,
             output=None, dataset_uri=None,
             resolver="sdd2rdf.resolve"):
    if dataset_uri is None:
        dataset_uri = prefix+'dataset'
    if format != 'csv':
        delimiter = None
    sdd = SemanticDataDictionary(semantic_data_dictionary,prefix, data_type=file_types[format])
    env = Environment(loader=PackageLoader('sdd2rdf', 'templates'))
    template = env.get_template('sdd_setl_template.jinja')
    output = template.render(sdd=sdd,
                             prefix=prefix,
                             data=datafile,
                             data_type=file_types[format],
                             delimiter=delimiter,
                             sheetname=sheetname,
                             data_out = output,
                             str=str,
                             dataset=dataset_uri,
                             isempty=isempty,
                             resolver=resolver)
    return output

def sdd2setl_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("semantic_data_dictionary")
    parser.add_argument("prefix")
    parser.add_argument("data_file")
    parser.add_argument("setl_output")
    parser.add_argument('-o', "--output")
    parser.add_argument('-f', "--format",default='csv', choices=['csv','excel'])
    parser.add_argument('-d', "--delimiter", default=',')
    parser.add_argument('-s', '--sheetname')
    parser.add_argument("--dataset_uri")
    parser.add_argument("--resolver")

    args = parser.parse_args()
    output = sdd2setl(args.semantic_data_dictionary,
                      args.prefix,
                      args.data_file,
                      args.format,
                      args.delimiter,
                      args.sheetname,
                      args.output,
                      args.resolver)
    with open(args.setl_output, 'wb') as o:
        o.write(output.encode('utf8'))
