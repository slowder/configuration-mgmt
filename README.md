# configuration-mgmt

A really simple configuration management tool written from scratch.

* Configuration is controlled by YAML file.
* Idempotent
* Supports Debian packages thorugh Apt, text files, and services
* Simple dependency support restarts services when dependent objects change

Example local server setup:
`sudo python3 apply.py server.yaml`
