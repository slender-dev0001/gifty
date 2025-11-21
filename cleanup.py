import os

files_to_remove = [
    r"c:\Users\Asus tuf\Downloads\bot discord +\cogs\all_slash_commands.py",
    r"c:\Users\Asus tuf\Downloads\bot discord +\cogs\slash_commands.py"
]

for file_path in files_to_remove:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Supprimé: {file_path}")
    else:
        print(f"Fichier non trouvé: {file_path}")
