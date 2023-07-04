from flask import Flask, render_template, flash, redirect
from app.controllers import controllers

# call env/Scripts/activate

app = Flask(__name__, 
            static_url_path='/static', 
            static_folder='app/static')
app.register_blueprint(controllers)
app.config.from_pyfile('config.py')

@app.errorhandler(Exception)
def handle_all_errors(e):
    flash(f"Sayfa Bulunamadı", "warning")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)