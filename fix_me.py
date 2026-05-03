with open('app/api/v1/endpoints/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'user = db.query(User).filter(User.id == payload.get("sub")).first()',
    'from uuid import UUID\n    user_id = payload.get("sub")\n    user = db.query(User).filter(User.id == UUID(user_id)).first()'
)

with open('app/api/v1/endpoints/auth.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('OK: auth.py corregido')