Vagrant.configure(2) do |config|
  (1..5).each do |index|
      config.vm.define "trusty_#{index}" do |machine|
          machine.vm.box = "ubuntu/trusty64"
          machine.vm.network "private_network", ip: "10.50.50.#{10+index}"
      end
  end
end
