# Security

## Unprivileged Account
I've created an unprivileged account on the Raspberry Pi (`developer`) for my main work to occur. This account with own the repo and any `sudo` changes will need to be performed via the admin account. 

## Machine GitHub Account
I've chosen to create a new GitHub user (`thermopidev`) to be used solely for the purposes of pulling/pushing to the `ThermoPi` repo. Since my main GitHub account is the owner of the `ThermoPi` repo, I wanted to ensure that if anyone were to access the Raspberry Pi they wouldn't have access to any of my other repositories. The Raspberry Pi connects to `thermopidev`'s GitHub account via SSH.

## SSH Private Key Password
I've added a password to my private SSH key (stored in 1Password), which is a little more annoying to use but means that if someone where to gain access to my key they would need the password to do anything meaningful with it.


