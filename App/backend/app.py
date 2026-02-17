from app import create_app
import sys

# Indique dans les logs système que l'application démarre
print("Starting Flask Application...", file=sys.stderr)

# Création de l'instance de l'application Flask via la factory function
app = create_app()

if __name__ == "__main__":
    # Démarrage du serveur de développement Flask
    # host="0.0.0.0" permet d'accepter les connexions venant de l'extérieur (nécessaire pour Docker)
    app.run(host="0.0.0.0", port=5000, debug=True)
