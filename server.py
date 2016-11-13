from flask import Flask, jsonify, request, render_template
app = Flask(__name__)

def the_function(param):
	return {
		"nodes" : [{"id": "point1", "x": 100, "y": 150, "affiliation": "blue"},
            {"id": "point2", "x": 150, "y": 200, "affiliation": "red"},
            {"id": "point3", "x": 200, "y": 100, "affiliation": "red"},
            {"id": "point4", "x": 400, "y": 300, "affiliation": "blue"},
            {"id": "point5", "x": 250, "y": 300, "affiliation": "green"}],
		"links" : [{"source": "point1", "target": "point2"},
            {"source": "point2", "target": "point3"},
            {"source": "point1", "target": "point4"},
            {"source": "point3", "target": "point4"},
            {"source": "point3", "target": "point1"},
            {"source": "point5", "target": "point1"}]
	}

@app.route("/")
def home():
    return render_template("index-sudo.html")

@app.route("/api/v1/search")
def search():
	# function just goes in here
	search_term = request.args.get("q")
	if not search_term:
		# bad request raise 403
		pass

	search_data = the_function(search_term)
	return jsonify(search_data)

if __name__ == "__main__":
    app.run(debug=True)

