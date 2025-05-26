import os
from dotenv import load_dotenv, set_key

# Function to write a new environment variable to the .env file
def manage_env_variable(var_name, new_value, env_file='.env'):
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write(f'{var_name}=False\n')

    set_key(env_file, var_name, new_value)

    load_dotenv(env_file)
