from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: sans-serif; text-align: center; background-color: #f4f4f4; padding: 50px; }
        h1 { color: #333; }
        .menu { background: white; padding: 20px; border-radius: 8px; display: inline-block; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <h1>Welcome to The Tasty Spoon</h1>
    <div class='menu'>
        <h2>Today's Special</h2>
        <p>Grilled Salmon with Asparagus</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True)