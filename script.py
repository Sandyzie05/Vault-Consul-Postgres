# import requests

# url = "http://127.0.0.1:8200/v1/database/config/postgre"

# payload = "{\n  \t   \"plugin_name\": \"postgresql-database-plugin\",\n    \"allowed_roles\": \"readonly\",\n    \"connection_url\": \"postgres://postgres:postgres@172.21.0.3:5432/postgres?sslmode=disable\"\n}"
# headers = {
#     'X-Vault-Token': "b9ca7a04-cc95-5c87-6632-2d1c11d461c0",
#     'Content-Type': "application/json",
#     'cache-control': "no-cache"
#     }

# response = requests.request("POST", url, data=payload, headers=headers)

# print(response.text)

import hvac
import psycopg2

# Environment Variables
VAULT_URL = 'http://localhost:8002'
VAULT_TOKEN ='b9ca7a04-cc95-5c87-6632-2d1c11d461c0'
pg_username = 'postgres'
pg_password = 'postgres'
db_name = 'postgres'
pg_hostname = '172.21.0.3'
role_name = 'readonly'
plugin_name = 'postgresql-database-plugin'
sslmode = 'disable'
config_name = 'postgrespython'
policy_name = 'pythonapp'
conn_url = 'postgres://postgres:postgres@172.21.0.3:5432/postgres?sslmode=disable'

client = hvac.Client(url='http://127.0.0.1:8200',token='b9ca7a04-cc95-5c87-6632-2d1c11d461c0')

auth_methods = client.sys.list_auth_methods()
# print('The following auth methods are enabled: {auth_methods_list}'.format(
#     auth_methods_list=', '.join(auth_methods['data'].keys()),
# ))
client.write('database/config/postgres', plugin_name='postgresql-database-plugin', allowed_roles='readonly', lease='24h', connection_url='postgres://postgres:postgres@172.21.0.3:5432/postgres?sslmode=disable')
print(client.read('database/config/postgres'))

def create_role_policy_token(role_name,policy_name):
    readonly = open('./readonly.sql','r')
    readonly_sql = readonly.read()
    print(readonly_sql)
    client.write('database/roles/'+role_name, db_name=db_name, creation_statements=readonly_sql, default_ttl='1h', max_ttl='24h')
    policy = open('./apps-policy.hcl','r')
    policy_hcl = policy.read()
    # print(type(policy_hcl))
    # Get credentials from the database secret engine
    client.sys.create_or_update_policy(
        name=policy_name,
        policy=policy_hcl,
    )
    token = client.create_token(policies=[policy_name], lease='1h')
    retrieve_username_password(token['auth']['client_token'])
    
def retrieve_username_password(client_token):
    # client = connect2vault(client_token)
    client = hvac.Client(url='http://127.0.0.1:8200',token=client_token)
    userdetail = client.read('database/creds/readonly')
    username = userdetail['data']['username']
    password = userdetail['data']['password']
    print(username)
    print(password)
    connect(username,password)
    
def connect(username,password):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
#         params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host=pg_hostname,database=db_name, user=username, password=password)
      
        # create a cursor
        cur = conn.cursor()
        
   # execute a statement
        print('PostgreSQL database version:')
        cur.execute('SELECT version()')
 
        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)
       
       # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


create_role_policy_token(role_name,policy_name)
    

 
