import requests
import crawler
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup

app = Flask(__name__)
output_data = []

@app.route("/",methods=["POST"])
def processo():
	data = request.get_json()

	try:
		validate_request(data)
		if "localizacao" not in data:
			data["localizacao"] = resolve_localization(data["processo"])
		
		response = crawler.crawl(data["processo"],data["localizacao"])

		return jsonify(response), 200
	except Exception as e:
		return (str(e), 400)

def validate_request(data):
	if "processo" not in data:
		raise Exception("Sua request está faltando o processo")

def resolve_localization(processo):
	localization = processo.split(".")[3]
	
	if localization == "02":
		return crawler.TJAL
	
	if localization == "06":
		return crawler.TJCE

	raise Exception("Não damos suporte a localização deste processo ainda")

if __name__ == "__main__":
	app.run(debug=False)
