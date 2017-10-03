# Install Satoru

Satoru installations are currently supported on Ubuntu >= 14.04. 
Satoru is installed using Puppet, which means that the install.pp script can be customized for advanced Puppet users, and for enterprise configurations.

## Install into an Ubuntu system

This is useful for deploying production knowledge graphs, or for developers who already have a machine (virtual or otherwise) that is ready to run Satoru.

```
bash < <(curl -skL https://raw.githubusercontent.com/tetherless-world/satoru/master/install.sh)
```

## Install into a vagrant virtual machine 

This is useful for developers who want to isolate their development environment so that builds are repeatable, and for developers of multiple knowledge graphs.

You will need to install vagrant and virtualbox.

```
mkdir satoru-vm && cd satoru-vm
curl -skL https://raw.githubusercontent.com/tetherless-world/satoru/master/Vagrantfile > Vagrantfile
curl -skL https://raw.githubusercontent.com/tetherless-world/satoru/master/install.sh > install.sh
vagrant up
```

## Administrative Tasks

To peform the following administrative tasks, you need to connect to the VM (if you're not running directly):

```
vagrant ssh
```

Once you are in the server, you need to change to the satoru user, go to the satoru app directory, and activate the python virtual environment:

```
sudo su - satoru
cd /apps/satoru
source venv/bin/activate
```

### Add a User

Registration is available on the website for users, but it's easy to add a user to the knowledge graph from the command line. 
Use `--roles=admin` to make the user an administrator.

```
python manage.py createuser -e <email> \
    -p <password (can change later)> \
    -f <First Name> \
    -l <Last Name -u <user handle> \
    --roles=admin
```

### Modify a User

You can change the roles a user has from the command line as well, but you'll need their user handle. 
For instance, you can add a user to a role like this:

```
python manage.py updateuser -u <user handle> --add_roles=admin
```

You can remove them from a role like this:

```
python manage.py updateuser -u <user handle> --remove_roles=admin
```

Changing a password is also simple:

```
python manage.py updateuser -u <user handle> -p <new password>
```

### Loading Knowledge

Knowledge can be added to Satoru using a command as well. This can be used to inject states that trigger larger-scale knowledge ingestion using [SETLr](https://github.com/tetherless-world/setlr/wiki/SETLr-Tutorial), or can simply add manually curated knowledge. 
If the RDF format supports named graphs, and the graphs are nanopublications, the nanopublications will be added as-is.
If there are no explicit nanopublications, or if the RDF format is triples-only, each graph (including the default one), is treated as a separate nanopublication assertion.
The PublicationInfo will contain some minimal provenance about the load, and each assertion will be the graphs contained in the file.

```
python manage.py load -i <input file> -f <turtle|trig|json-ld|xml|nquads|nt|rdfa>
```

## [Next: Customizing Satoru](configuration)
