# ansible-snapd-module
Module for ansible to setup packages with snapd

## Instalation

* Make sure file `snap.py` is accessable as [ansible module](http://docs.ansible.com/ansible/dev_guide/developing_modules.html#module-paths)

Alternatively you can put it in `library` directory with your playbook

```go
|- playbook.yml
|- library
   |- snap.py
```

## Usage

```yaml
- name: update snap cache
  snap:
    upgrade: yes

- name: snap
  snap:
    name: "{{ item }}"
    state: absent
  with_items:
    - hello-world
    - hello-world
```
