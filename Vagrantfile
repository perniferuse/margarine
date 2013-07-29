# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "puppet/manifests"
    puppet.manifest_file = "site.pp"
    puppet.module_path = "puppet/modules"
  end

  config.vm.define "tinge" do |tinge|
    tinge.vm.network :private_network, ip: "192.168.57.10"
    tinge.vm.synced_folder ".", "/margarine"
    tinge.vm.hostname = "tinge.example.com"
  end

  config.vm.define "blend" do |blend|
    blend.vm.network :private_network, ip: "192.168.57.11"
    blend.vm.synced_folder ".", "/margarine"
    blend.vm.hostname = "blend.example.com"
  end

  config.vm.define "spread" do |spread|
    spread.vm.network :private_network, ip: "192.168.57.12"
    spread.vm.synced_folder ".", "/margarine"
    spread.vm.hostname = "spread.example.com"
  end

  config.vm.define "rabbit" do |rabbit|
    rabbit.vm.network :private_network, ip: "192.168.57.13"

    config.vm.provision "shell", inline: "apt-get install -y rabbitmq-server"
  end
end
