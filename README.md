# Vault-Consul-Postgres

The aim of the project is to achieve the following:

Using docker:
- Stand up a Postgres 10 or 11 database.
- Stand up a single node Vault cluster backed by a single node Consul host.
- Write a python 3 application that will:
- Connect to vault to create dynamic secrets.
- Using those secrets connect to the database and retrieve some data
- Connect to Consul's KV backend to retrieve some data.

Steps:
1. The docker-compose.yml has all the config to build postgre, vault and consul containers. In this deployment vault is using    consul as its backend. 

2. To learn more about Postgre, vault and consul check the following links:
vaultproject.io/
consul.io/
https://www.postgresql.org/

3. How to execute docker-compose?
 In the root directory of the project, run 'docker-compose up -d --build'
 
4. The above command would build and deploy the docker containers. To check if the containers are up, run: 'docker ps -a'

5. Once the containers are up, open the url's to check if vault and consul are accessible. For example: open http://localhost:8002 in your browser and see if the UI is accessible.

6. Now run 'docker exec -it vault_container_name bash' to run a bash prompt inside the vault instance. Before vault starts to accept services, we need to initialize and unseal vault. Run 'vault operator init'. This command will provide 5 keys and 1 root token. Copy the information securely and keep it handy.

7. Run 'vault operator unseal' and enter the keys copied from the last step. Use the command for 3 times with 3 different keys to Unseal vault. Now, login using 'vault login' command and use the token from the last step as password.

8. Enable database secret engine using the command 'vault secrets enable database' as we are going to use the python script to generate dynamic secrets to access postgres db.

9. Now modify the scripts.py python script based on your environement and run it from the root directory of the project as it is utilizing conf files in the same directory.

10. The python program will generate the output to validate the aim of the project.
