import os
import grp
import pwd
from pathlib import Path, PurePath
import stat
import sys
from subprocess import Popen, PIPE
import shutil

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

    def changes_required(self, changes={}) -> bool:
        """Determine whether applying this manager will cause a change."""
        return self.check_dependent_changes(changes)

    def check_dependent_changes(self, changes):
        if 'dependencies' in self.config:
            for dep in self.config['dependencies']:
                if dep in changes:
                    return True
        return False

    def apply(self) -> bool:
        """Apply this managed configuration to the system. Idempotent."""
        return True

class Dummy(ManagedBase):
    pass

class TestExample(ManagedBase):
    fields = ['test1', 'test2']

class ManagedFile(ManagedBase):
    fields = ['path', 'name', 'mode', 'owner', 'group', 'content']
    content_mismatch = False
    def changes_required(self, changes={}):
        found_change = False
        base_path = Path(self.config['path'])
        file_path = Path(PurePath(self.config['path']).joinpath(self.config['name']))
        if not base_path.is_dir():
            print('Directory {} does not exist'.format(self.config['path']))
            return True
        if not file_path.is_file():
            print('File "{}" does not exist.'.format(self.config['name']))
            return True
        with open(str(file_path), 'r') as f:
            c = f.read()
            if c != self.config['content']:
                print('Content mismatch in file "{}"'.format(self.config['name']))
                found_change = True
                self.content_mismatch = True

        stat_info = os.stat(str(file_path))
        mode = stat_info.st_mode
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        # Check mode
        file_mode = oct(stat.S_IMODE(mode))[2:]
        if file_mode != str(self.config['mode']):
            print('File mode incorrect. Current: {} Expected: {}'.format(file_mode, self.config['mode']))
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

    def apply(self):
        base_path = Path(self.config['path'])
        file_path = Path(PurePath(self.config['path']).joinpath(self.config['name']))
        if not base_path.is_dir():
            print("Making directories: {}".format(self.config['path']))
            os.makedirs(base_path, mode=int(str(self.config['mode']), 8), exist_ok=True)
            
        if not file_path.is_file() or self.content_mismatch:
            print("Writing file {}".format(self.config['name']))
            with open(str(file_path), 'w') as f:
                f.write(self.config['content'])
        
        shutil.chown(str(file_path), user=self.config['owner'], group=self.config['group'])
        print("setting {} to {}".format(str(file_path), str(self.config['mode'])))
        os.chmod(str(file_path), int(str(self.config['mode']),8))

class ManagedPackage(ManagedBase):
    fields = ['name', 'version']
    def changes_required(self, changes={}):
        found_change = False
        # sudo apt-get update
        Popen(['sudo', 'apt-get', 'update'], stdout=PIPE).communicate()
        with Popen(['dpkg', '-s', self.config['name']], stdout=PIPE) as proc:
            # sudo dpkg -s <name>
            # find "Status: install ok installed" or similar in output
            # find version in output, eg "Version: 2.4.29-1ubuntu4.6"
            output = proc.communicate()[0].decode(sys.stdout.encoding).split('\n')
            for line in output:
                if line.startswith('Status: '):
                    if 'installed' not in line:
                        print("{}: Package {} not installed.".format(self.config['_obj_name'], self.config['name']))
                        found_change = True
                elif line.startswith('Version: '):
                    version = line[9:]
                    if str(self.config['version']) not in line:
                        print("{}: Package {} wrong version. Current: {} Expected: {}".format(self.config['_obj_name'], self.config['name'], version, self.config['version']))
                        found_change = True
        return self.check_dependent_changes(changes) or found_change

    def apply(self):
        Popen(['sudo', 'apt-get', 'install', '-y', self.config['name']+'='+self.config['version'], ], stdout=PIPE).communicate()

class ManagedService(ManagedBase):
    fields = ['name', 'state']

    def validate(self):
        super(ManagedService, self).validate()
        valid_states = ['running', 'stopped']
        if self.config['state'] not in valid_states:
            raise(Exception("Field 'state' must be one of {}").format(valid_states))
    
    def changes_required(self, changes={}):
        found_change = False
        #"sudo service <name> status"
        #"systemctl status <name>"
        
        with Popen(['sudo', 'service', self.config['name'], 'status'], stdout=PIPE) as proc:
            # find 'Active: active (running)'
            output = proc.communicate()[0].decode(sys.stdout.encoding).split('\n')
            for line in output:
                if line.startswith('Active:'):
                    if 'active (running)' not in line and self.config['state'] == 'running':
                        found_change = True
                    elif '(stopped)' not in line and self.config['state'] == 'stopped':
                        found_change = True
            
        # Restart if desired state is 'running' and a dpendency changes
        self.restart_required = self.config['state'] == 'running' and self.check_dependent_changes(changes)
        return self.restart_required or found_change

    def apply(self):
        if self.restart_required:
            print("restarting {} {}".format(self.config['_obj_name'], self.config['name']))
            Popen(['sudo', 'service', self.config['name'], 'restart'], stdout=PIPE).communicate()
            return
        elif self.config['state'] == 'running':
            Popen(['sudo', 'service', self.config['name'], 'start'], stdout=PIPE).communicate()
        elif self.config['state'] == 'stopped':
            Popen(['sudo', 'service', self.config['name'], 'stop'], stdout=PIPE).communicate()
