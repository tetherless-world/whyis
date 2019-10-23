# Install Whyis

The Whyis installer is layered, which allows for maximum flexibility. Each layer is runnable by itself, resulting in a functional Whyis.

If you do not have Ubuntu 16.04, please use VirtualBox, VMWare, or another virtualization tool to create a VM with Ubuntu 16.04 installed. Whyis requires at least 4 GB of memory and 30GB of disk space.

- **Layer 2: Shell Script** If you already have a virtual machine provisioned, or want to directly install Whyis onto an Ubuntu 16.04 server directly, you can use the Layer 2 shell script. It is a simple script, `install.sh`, that installs Puppet and the needed modules, and then runs the Layer 1 Puppet script.
- **Layer 1: Puppet** [Puppet](https://puppet.com/) is a flexible devops tool that automates the configuration and provisioning of servers, both virtual and physical. The script `puppet/manifests/install.pp` can be used directly by current Puppet users that want to incorporate Whyis deployment into their existing Puppet infrastructure.

** Whyis installations are currently supported on Ubuntu 16.04. **


## Layer 2: Install into an Ubuntu 16.04 system

This is useful for deploying production knowledge graphs, or for developers who already have a machine (virtual or otherwise) that is ready to run Whyis. Currently, we only support installing on Ubuntu 16.04.

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/release/install.sh)
```

To install using the development branch of Whyis, use the master install script:

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/whyis/master/install.sh)
```
## How to Create an Ubuntu 16.04 Virtual Machine with Virtualbox

### Download ISO file

Download the ISO file for Ubuntu Server 16.04 from: https://www.ubuntu.com/download/server.

### Create a new Ubuntu Virtual Machine

From VM VirtualBox Manager, Select "New" to create a new VM.

In the following window, name your VM and select Type Linux and Version Ubuntu.

Choose the desired memory and space settings, and complete the VM creation.

### Load the ISO
Before starting the newly created VM, right click the VM and go to its Settings.

Under Storage, select Controller IDE and specify your ISO file. Press Ok to save the settings.

Now, when you start the VM, it should install a new Ubuntu desktop. You can now just follow the instructions for installing Whyis onto a Ubuntu system.

## [Next: Using the Whyis command-line interface](commands)
