from auth import hash_password, verify_password

print(hash_password('Zapominai'))

print(verify_password('Zapominai', '$2b$12$/9J.wBLX4TOpuwmebQgnzubnNkDVozwQCPEN2asSvHGi2vaLG1EQ2'))

print(verify_password('WrongPassword', '$2b$12$/9J.wBLX4TOpuwmebQgnzubnNkDVozwQCPEN2asSvHGi2vaLG1EQ2'))