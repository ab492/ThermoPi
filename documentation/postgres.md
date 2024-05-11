# Postgres Helper

### How to install

`sudo apt update`
`sudo apt install postgresql`
`sudo systemctl start postgresql // Start service`   
`sudo systemctl enable postgresql // Enable service on launch`    

### Helper commands

Switch to postgres admin user: `sudo -i -u postgres`
Exit postgres user: `exit`
Enter psql prompt: `psql` or `psql -U developer -d thermodb`  or `psql -U postgres` 
Connect to database: `\c thermodb`
Describe tables: `\dt`
Describe specific table (i.e. temperature_logs): `\d temperature_logs`
Exit psql prompt: `\q`

### Creating a peer user

By default this user peer authentication, where the database user needs to match the name of the current account user.

For example, from the sudo account I ran:

`sudo su - postgres`
`psql` 

Then ran the following to create the peer user:

`CREATE DATABASE thermodb;`

`CREATE USER thermodev WITH PASSWORD 'some_password';` (including `'`)

`GRANT ALL PRIVILEGES ON DATABASE thermodb TO thermodev;`