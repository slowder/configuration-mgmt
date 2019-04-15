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


