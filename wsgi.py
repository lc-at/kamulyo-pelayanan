from app import create_app
from app.models import db


app = create_app()
@app.cli.command()
def createdb():
    db.create_all()

if __name__ == '__main__':
    app.run(port=7040, debug=True)
