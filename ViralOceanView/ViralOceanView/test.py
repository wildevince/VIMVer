import os

Temp_DIR = os.path.dirname(os.path.abspath(__file__))
print(Temp_DIR)

print(os.path.join(Temp_DIR, 'templates'))