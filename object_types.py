

class TypeDefinition:
    """
    Define allowed/expected fields for configuration object types.
    """
    _special_fields = ['_obj_name', 'type']  # _obj_name and type are special fields that exist in all configuraiton objects.
    fields = []

    def __init__(self, obj):
        self.config = obj
        self.validate()

    def validate(self):
        """Type-specific validation"""
        for key in self.config.keys():
            if key not in self.fields and key not in self._special_fields:
                raise(Exception("Unexpected field '{}' for type '{}' in object '{}'. Expected fields are {}".format(key, self.__class__.__name__, self.config['_obj_name'], self.fields)))
        for field in self.fields:
            if field not in self.config:
                raise(Exception("Missing expected field '{}' for type '{}' in object '{}'. Expected fields are {}".format(field, self.__class__.__name__, self.config['_obj_name'], self.fields)))

class Dummy(TypeDefinition):
    pass

class TestExample(TypeDefinition):
    fields = ['test1', 'test2']

class ManagedFile(TypeDefinition):
    fields = ['path', 'name', 'permissions', 'owner', 'group', 'content']

class ManagedPackage(TypeDefinition):
    pass

