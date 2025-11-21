import ast
import sys

try:
    with open(r'cogs\snusbase_osint.py', 'r', encoding='utf-8') as f:
        code = f.read()
    ast.parse(code)
    print("✅ Syntaxe correcte")
except SyntaxError as e:
    print(f"❌ Erreur de syntaxe: {e}")
    sys.exit(1)
