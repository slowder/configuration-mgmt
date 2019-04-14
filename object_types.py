import os
import grp
import pwd
from pathlib import Path, PurePath
import stat

class ManagedBase:
    """
    Define allowed/expected fields for configuration object types.
    """
    _special_fields = ['_obj_name', 'type', 'dependencies']  # special fields that exist in all configuraiton objects.
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

    def changes_required(self) -> bool:
        """Determine whether applying this manager will cause a change."""
        return False

    def apply(self) -> bool:
        """Apply this managed configuration to the system. Idempotent."""
        return True

class Dummy(ManagedBase):
    pass

class TestExample(ManagedBase):
    fields = ['test1', 'test2']

class ManagedFile(ManagedBase):
    fields = ['path', 'name', 'permissions', 'owner', 'group', 'content']

    def changes_required(self):
        found_change = False
        base_path = Path(self.config['path'])
        file_path = Path(PurePath(self.config['path']).joinpath(self.config['name']))
        if not base_path.is_dir():
            print('Directory does not exist')
            return True
        if not file_path.is_file():
            print('File does not exist.')
            return True
        with open(file_path, 'r') as f:
            c = f.read()
            if c != self.config['content']:
                print('Content mismatch')
                found_change = True

        stat_info = os.stat(file_path)
        mode = stat_info.st_mode
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        # Check permissions
        file_mode = oct(stat.S_IMODE(mode))[2:]
        if file_mode != self.config['permissions']:
            print('File mode incorrect. Current: {} Expected: {}'.format(file_mode, self.config['permissions']))
            found_change = True

        # Check owner and group
        owner = pwd.getpwuid(uid)[0]
        group = grp.getgrgid(gid)[0]
        if owner != self.config['owner']:
            print("Owner incorrect. Current: {}, Expected: {}".format(owner, self.config['owner']))
            found_change = True
        if group != self.config['group']:
            print("Group incorrect. Current: {}, Expected: {}".format(group, self.config['group']))
            found_change = True
        return found_change


class ManagedPackage(ManagedBase):
    fields = ['name', 'version']
    def changes_required(self):
        # sudo apt-get update
        # sudo dpkg -s <name>
        # find "Status: install ok installed" or similar in output
        # find version in output, eg "Version: 2.4.29-1ubuntu4.6"
        pass

class ManagedService(ManagedBase):
    fields = ['name', 'state']

    def validate(self):
        super(ManagedService, self).validate()
        valid_states = ['running', 'stopped']
        if self.config['state'] not in valid_states:
            raise(Exception("Field 'state' must be one of {}").format(valid_states))
    
    def changes_required(self):
        "sudo service <name> status"
        "systemctl status <name>"
