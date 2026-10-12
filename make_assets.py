import base64

with open('girl_illustration.png', 'rb') as f:
    girl_b64 = base64.b64encode(f.read()).decode()

with open('card_ai_illustration.png', 'rb') as f:
    card_b64 = base64.b64encode(f.read()).decode()

with open('new_assets_b64.py', 'w', encoding='utf-8') as f:
    f.write(f'GIRL_ILLUSTRATION_B64 = "{girl_b64}"\n')
    f.write(f'CARD_AI_ILLUSTRATION_B64 = "{card_b64}"\n')

print("new_assets_b64.py generated successfully")
