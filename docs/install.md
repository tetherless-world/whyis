# Install Satoru

Satoru installations are currently supported on Ubuntu >= 14.04. Satoru is installed using Puppet, which means that the install.pp script can be customized for advanced Puppet users, and for enterprise configurations.

## Install into an Ubuntu system

This is useful for deploying production knowledge graphs, or for developers who already have a machine (virtual or otherwise) that is ready to run Satoru.

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/satoru/master/install.sh)
```

Visit `http://<hostname>/register` to add an initial user.

## Install into a vagrant virtual machine 

This is useful for developers who want to isolate their development environment so that builds are repeatable, and for developers of multiple knowledge graphs.

You will need to install vagrant and virtualbox.

```
mkdir satoru-vm && cd satoru-vm
curl -skL https://raw.githubusercontent.com/tetherless-world/satoru/master/Vagrantfile > Vagrantfile
curl -skL https://raw.githubusercontent.com/tetherless-world/satoru/master/install.sh > install.sh
vagrant up
```

Visit `http://192.168.33.36/register` to add an initial user.

## Customizing Satoru

Not all knowledge graphs have the same needs. That's why a configuration section will be forthcoming at some point.
