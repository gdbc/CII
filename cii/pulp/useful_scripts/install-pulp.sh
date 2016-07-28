#!/bin/bash

# A hard and fast way to install a pulp server, this should be puppetized

yum install httpd mongodb-server qpid-cpp-server qpid-cpp-server-store pulp-server python-qpid python-qpid-qmf  pulp-puppet-plugins pulp-rpm-plugins qpid-cpp-client gofer  qpid-dispatch-tools.x86_64  qpid-tools.noarch pulp-admin-client pulp-admin-client pulp-rpm-admin-extensions pulp-consumer-client pulp-agent pulp-puppet-consumer-extensions pulp-puppet-handlers pulp-rpm-consumer-extensions pulp-rpm-handlers pulp-rpm-yumplugins python-gofer-qpid python-requests -y



systemctl enable mongod
systemctl start mongod

if ! grep ^auth /etc/qpid/qpidd.conf &> /dev/null;then
echo "auth=no" > /etc/qpid/qpidd.conf
fi

systemctl enable qpidd
systemctl start qpidd

systemctl enable httpd
systemctl start httpd

systemctl enable pulp_workers
systemctl start pulp_workers

systemctl enable pulp_celerybeat
systemctl start pulp_celerybeat

systemctl enable pulp_resource_manager
systemctl start pulp_resource_manager

systemctl enable goferd
systemctl start goferd


sudo -u apache pulp-manage-db

yum install pulp-admin-client pulp-rpm-admin-extensions -y

if ! grep ^host /etc/pulp/admin/admin.conf &> /dev/null;then
sed -i "s/\[server\]/\[server\]\nhost: `hostname`\nverify_ssl: False\n/" /etc/pulp/admin/admin.conf
fi

sed -i "s/\[main\]/\[main\]\nverify_ssl: False\n/" /etc/pulp/repo_auth.conf
systemctl restart httpd

echo "Note: Add hostname to /etc/hosts or this breaks!"
