import yaml
import json
import cfnsphinx.cfn_build as cfnbuild
from cfnsphinx.helper import Helper


class Ref(yaml.YAMLObject):
    yaml_tag = '!Ref'
    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):

        path = "Resource"
        name = []
        path = path+"."+node.value
        return ":ref:`Reference to {} <{}>`".format(node.value, path)


class FindInMap(yaml.YAMLObject):
    yaml_tag = '!FindInMap'

    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):

        path = "Mapping"
        name = []
        for item in node.value:
            name.append(item.value)
            path = path+"."+item.value
        return ":ref:`{} <{}>`".format(" --> ".join(name), path)


class Join(yaml.YAMLObject):
    yaml_tag = '!Join'
    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class GetAtt(yaml.YAMLObject):
    yaml_tag = '!GetAtt'
    def __init__(self, val):
        self.val = val

    @classmethod
    def from_yaml(cls, loader, node):
        return cls(node.value)


class CfnExporter:

    def format(self, yml, nesting, prevkey=""):
        res = ""
        if type(yml) is type([]):
            for el in yml:
                if type(el) is type(""):
                    res = res + "* " + el + "\n" + (" " * nesting)
                else:
                    res = res + "* " + self.format(el, nesting + 1) + "\n" + (" " * nesting)
        elif type(yml) is type({}):
            res = res + "\n"# + (" " * (nesting))
            for k, v in yml.items():

                if prevkey:
                    current_key = "{}--{}".format(prevkey, k)
                    res = res + ".. _{}: \n \n ".format(current_key)
                else:
                    current_key = False

                res = res + " " * (nesting) + k + "\n" + (" " * (nesting + 2)) + self.format(v, nesting + 2, current_key) + "\n" + (" " * nesting)
        else: #string, int, float?
            return str(yml)

        return res

    def from_data(self, yml, document):
        reslis = []

        stack_name = document+"stack-"
        name = document
        reslis.append("{}\n{}\n{}\n\n".format("=" * len(name),
                                              name, "=" * len(name)))

        if 'Parameters' in yml:
            name = "Parameters"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Parameters'].items():
                name = key
                typ = val['Type']

                vals = ['Description', 'Default', 'AllowedValues',
                        'ConstraintDescription']

                reslis.append(".. cfn:parameter:: {}".format(name))
                reslis.append("    :type: {}\n".format(typ))
                for v in vals:
                    if v in val:
                        reslis.append("    :{}: {}\n".format(v.lower(), val[v]))

                reslis.append("")

        if 'Mappings' in yml:
            name = "Mappings"

            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Mappings'].items():
                name = key
                typ = 'Mapping'
                reslis.append(".. cfn:mapping:: {}\n".format(name))
                reslis.append((" " * 6) + self.format(val, 6))

                reslis.append("")

        if 'Conditions' in yml:
            name = "Conditions"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Conditions'].items():
                name = key
                typ = 'Condition'

                reslis.append(".. cfn:condition:: {}\n".format(name))
                reslis.append((" " * 6) + self.format(val, 6))

                reslis.append("")

        if 'Resources' in yml:
            name = "Resources"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Resources'].items():
                name = key
                typ = val['Type']
                if "Properties" in val:
                    prop = val['Properties']

                    vals = ['Description', 'Default', 'AllowedValues',
                            'ConstraintDescription']

                    reslis.append(".. cfn:resource:: {}".format(name))
                    reslis.append("   :type: {}".format(typ))
                    for v in vals:



                        if v in val:
                            reslis.append("    :{}:\n".format(v.lower()))
                            reslis.append((" " * 5) + self.format(val[v], 5), False)

                    for k, v in prop.items():

                        if k.lower().strip() == "tags":
                            reslis.append("    :{}:\n".format(k))
                            reslis.append(Helper.tagsToTable(v, headline=True))
                        else:
                            reslis.append("    :{}:\n".format(k))
                            reslis.append((" " * 5) + self.format(v, 5, False))
                    reslis.append("")

        if 'Outputs' in yml:
            name = "Outputs"
            reslis.append("{}\n{}\n{}\n\n".format("*" * len(name),
                                                  name, "*" * len(name)))

            for key, val in yml['Outputs'].items():
                name = key

                keylis = ['Description', 'Value']

                reslis.append(".. cfn:output:: {}\n".format(name))
                for lookup in keylis:
                    if lookup in val:
                        reslis.append("     :{}: {}".format(lookup, (" " * 6) + self.format(val[lookup], 6)))

                reslis.append("")

        return '\n'.join(reslis)


class CfnParserYaml:
    @classmethod
    def parse(cls, inputstring, document):
        y = yaml.load(inputstring, Loader=yaml.FullLoader)
        exporter = CfnExporter()
        rest = exporter.from_data(y, document)

        return rest


class CfnParserJson:
    @classmethod
    def parse(cls, inputstring, document):
        y = json.loads(inputstring)
        exporter = CfnExporter()
        rest = exporter.from_data(y, document)

        return rest
