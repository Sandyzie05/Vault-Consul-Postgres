import hvac  # Vault python package
import psycopg2  # postgres python package
import pdb  # python debugger package
import requests  # python requests package


# Environment Variables could be used as protected keys in CI/CD pipelines.
VAULT_URL = 'http://127.0.0.1:8200'
VAULT_TOKEN = 'b9ca7a04-cc95-5c87-6632-2d1c11d461c0'
pg_username = 'postgres'
pg_password = 'postgres'
db_name = 'postgres'
pg_hostname = '172.21.0.3'
role_name = 'readonly'
plugin_name = 'postgresql-database-plugin'
ssl_mode = 'disable'
config_name = 'postgres'
policy_name = 'pythonapp'
# conn_url = 'postgres://postgres:postgres@172.21.0.3:5432/postgres?ssl_mode=disable'
conn_url = 'postgres://' + pg_username + ':' + pg_password + '@' + pg_hostname + ':5432/' +config_name + '?sslmode=' + ssl_mode
config_path = 'database/config/' + config_name
consul_host = 'http://127.0.0.1:8500'
consul_kv_key = 'seal-config'
consul_kv_path = 'vault/core/' + consul_kv_key
consul_url = consul_host + '/v1/kv/' + consul_kv_path

# pdb.set_trace()


def connect_with_vault(vu, vt):
    client = hvac.Client(url=vu, token=vt)
    return client


def enable_postgres_security_engine(cp):
    client = connect_with_vault(VAULT_URL, VAULT_TOKEN)
    # pdb.set_trace()
    client.write(cp, plugin_name=plugin_name, allowed_roles=role_name, lease='24h', connection_url=conn_url)
    print(client.read(cp))
    create_role_policy_token(role_name, policy_name, client)


def create_role_policy_token(rn, pn, c):
    readonly = open('./readonly.sql', 'r')
    readonly_sql = readonly.read()
    # print(readonly_sql)
    c.write('database/roles/' + rn, db_name=db_name, creation_statements=readonly_sql, default_ttl='1h', max_ttl='24h')
    policy = open('./apps-policy.hcl', 'r')
    policy_hcl = policy.read()
    # print(type(policy_hcl))
    # Get credentials from the database secret engine
    c.sys.create_or_update_policy(
        name=pn,
        policy=policy_hcl,
    )
    token = c.create_token(policies=[pn], lease='1h')
    retrieve_username_password(token['auth']['client_token'])


def retrieve_username_password(token):
    client2 = connect_with_vault(VAULT_URL, token)
    # client = hvac.Client(url='http://127.0.0.1:8200',token=client_token)
    user_detail = client2.read('database/creds/readonly')
    username = user_detail['data']['username']
    password = user_detail['data']['password']
    print(username)
    print(password)
    connect(username, password)


def connect(un, passw):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        #  params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host=pg_hostname,database=db_name, user=un, password=passw)
      
        # create a cursor
        cur = conn.cursor()
        
        # execute a statement
        print('PostgreSQL database version:')
        # create_table_query = '''CREATE TABLE mobile
        #           (ID INT PRIMARY KEY     NOT NULL,
        #           MODEL           TEXT    NOT NULL,
        #           PRICE         REAL); '''

        read_table = 'select * from testtable;'
        # cur.execute('SELECT version()')
        # cur.execute(create_table_query)
        cur.execute(read_table)
 
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


def connect_to_consul():

    payload = ""
    headers = {'cache-control': 'no-cache'}

    response = requests.request("GET", consul_url, data=payload, headers=headers)

    print("Value for Key '{}': {}".format(consul_kv_key, response.text))


enable_postgres_security_engine(config_path)
connect_to_consul()
# create_role_policy_token(role_name,policy_name)
