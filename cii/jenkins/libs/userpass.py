# Usage: This library allows you to extrapolate usernames and passwords from uploaded code
# Add this library to /usr/lib64/python2.7/

class userpass:

    def creds(self):
        creds = {'pulp':{'user': '<username>','passwd':'<password>','server':'<pulp.server.name>'},'foreman':{'user':'<foreman username>','passwd':'<foreman passwd>','server':'<foreman.server.name>'},'git':{'user':'<git user>','server':'<git.server.with.user.ssh.keys>'},'ssh':{'user':'root','passwd':'<ssh root password>'}}
        return creds

