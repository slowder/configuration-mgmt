import yaml
from sys import argv
from object_types import ManagedFile, ManagedPackage, ManagedService, Dummy, TestExample


VALID_TYPES = {
    'file': ManagedFile,
    'dummy': Dummy,
    'package': ManagedPackage,
    'test': TestExample,
    'service': ManagedService
}

def validate(config):
    """Verify config object is a valid object, not type specific."""
    if 'type' not in config:
        raise(Exception("Configuration '{}' must have a 'type' parameter.".format(_obj_name)))
    if config['type'] not in VALID_TYPES:
        raise(Exception("Configuration objects must be one of the following types: {}".format(str(VALID_TYPES))))

def dispatch(objects, test_mode=False):
    """Check for changes in each manager."""
    changes = {}
    for config in objects:
        manager = VALID_TYPES[config['type']](config)
        #print("Checking {}".format(config['_obj_name']))
        changes_required = manager.changes_required(changes=changes)
        print("{} changes required: {}".format(config['_obj_name'], changes_required))
        if changes_required:
            changes[config['_obj_name']] = True
        if not test_mode:
            manager.apply()

if __name__ == '__main__':
    with open(argv[1]) as f:
        objects = [obj.update({'_obj_name': _obj_name}) or obj for _obj_name,obj in yaml.load(f).items()]
    
    for obj in objects:
        validate(obj)
    dispatch(objects, test_mode=False)


