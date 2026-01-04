from app import create_app
import sys

print("Starting Flask Application...", file=sys.stderr)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
