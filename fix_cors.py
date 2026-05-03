with open('app/main.py', 'r', encoding='utf-8') as f:
    c = f.read()
c = c.replace(
    'allow_origins=["http://localhost:3000", "http://localhost:5173"]',
    'allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"]'
)
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(c)
print('OK: CORS actualizado')