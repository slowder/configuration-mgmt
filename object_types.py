
VALID_TYPES = {
    'file': ManagedFile,
    'dummy': Dummy,
    'package': ManagedPackage
}

Class TypeDefinition:
    """
    Define allowed/expected fields for configuration object types.
    """
    fields = ['_obj_name']
    def validate(self):
        for key in self.config.keys():
            if key not in self.fields and key != '_obj_name':
                raise("Unexpected field '{}' in type '{}'. Expected fields are {}".format(key, self.__class__, self.fields))
        for field in fields:
            if field not in self.config:
                raise("Missing expected field '{}' for type '{}'. Expected fields are {}".format(field, self.__class__, self.fields))


Class ManagedFile(TypeDefinition):
    pass
