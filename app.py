from flask import Flask, render_template, request,abort,jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index_page_landing():
    return render_template("layout.html")

@app.route('/api/v1/temperature',methods=['POST'])
def recieveTemp():
    if 'temperature' in request.json and type(request.json['temperature'])==float:
        print(request.json)
        return "posted"

if __name__ == "__main__":
    app.run(host='0.0.0.0')