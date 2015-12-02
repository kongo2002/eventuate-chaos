
VAGRANTFILE_API_VERSION = "2"
BOX_NAME = ENV['BOX_NAME'] || "ubuntu/trusty64"
script = <<SCRIPT
#!/bin/bash -e

if [ ! -f /etc/default/docker ]; then
  echo "/etc/default/docker not found -- is docker installed?" >&2
  exit 1
fi

# get setuptools
apt-get update
apt-get install python-setuptools

# get blockade
if [ -d "/blockade" ]; then
    cd /blockade
    git fetch origin
    git reset --hard origin/master
else
    git clone https://github.com/kongo2002/blockade.git /blockade
fi

# build blockade
cd /blockade
python setup.py develop

SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = BOX_NAME

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--name", "eventuate-chaos", "--memory", "4096", "--cpus", "2"]
  end

  config.vm.provision "docker"
  config.vm.provision "shell", inline: script
end

# vim: set ft=ruby:
