# configuration-mgmt

A simple configuration management tool written from scratch.

* Configuration is controlled by YAML file.
* Idempotent
* Supports Debian packages thorugh Apt, text files, and services
* Simple dependency support restarts services when dependent objects change

Example Ubuntu14.04 local server setup:
```
sudo bootstrap.sh
sudo python3 apply.py server1404.yaml
```
Example Ubuntu14.04 remote server setup:
```
ssh -t USER@SERVER "sudo apt install python3-pip; sudo pip3 install pyyaml"
ssh -t USER@SERVER "wget https://github.com/slowder/configuration-mgmt/archive/0.7.tar.gz; tar -zxvf 0.7.tar.gz"
ssh -t USER@SERVER "sudo python3 configuration-mgmt-0.7/apply.py configuration-mgmt-0.7/server1404.yaml; curl localhost"
```
Example Ubuntu14.04 remote setup with *MULTIPLE SERVERS* and *ALL IN ONE LINE*:
```
for s in USER@SERVER USER@SERVER; do ssh -t $s "sudo apt install -y python3-pip; sudo pip3 install pyyaml; wget https://github.com/slowder/configuration-mgmt/archive/0.7.tar.gz; tar -zxvf 0.7.tar.gz; sudo python3 configuration-mgmt-0.7/apply.py configuration-mgmt-0.7/server1404.yaml; curl localhost"; done
```

Code Documentation:
The file `object_types.py` defines the various styles of configuration objects and their fields. Subclass the `ManagedBase` class to create your own type. Set required field names in the `fields` list, then override the `changes_required` and `apply` methods to define your behavior.

Example YAML configuration:
```
package_apache2:
    type: package
    name: apache2
    version: 2.4.7-1ubuntu4.22

php_index_file:
    type: file
    path: /var/www/html/
    name: index.php
    owner: root
    group: root
    mode: 755
    content: |
        <?php

        header("Content-Type: text/plain");

        echo "Hello, world!\n";

```
