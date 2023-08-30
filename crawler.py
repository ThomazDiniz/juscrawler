import re
import requests
from bs4 import BeautifulSoup
import json

TJAL = "TJAL"
TJCE = "TJCE"

def crawl(processo,localizacao):
	if localizacao == TJAL:
		return crawl_tjal(processo)
	
	if localizacao == TJCE:
		return crawl_tjce(processo)

	raise Exception("Não damos suporte a localização deste processo ainda")

def crawl_tjal(processo):
    return [crawl_tjal_1a_instancia(processo),crawl_tjal_2a_instancia(processo)];

def crawl_tjce(processo):
    return [crawl_tjce_1a_instancia(processo),crawl_tjce_2a_instancia(processo)];

def crawl_tjal_1a_instancia(processo):
    url = "https://www2.tjal.jus.br/cpopg/search.do"
    params = {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.valorConsultaNuUnificado": processo,
        "dadosConsulta.tipoNuProcesso": "UNIFICADO"
    }
    response = make_request(url,params)
    
    return parse(response)

def crawl_tjal_2a_instancia(processo):
    #request para pegar o código da 2a instancia
    url = "https://www2.tjal.jus.br/cposg5/search.do"
    params = {
        "cbPesquisa": "NUMPROC",
        "dePesquisaNuUnificado": processo,
        "tipoNuProcesso": "UNIFICADO"
    }
    response = make_request(url,params)
    codigo = get_codigo_2a_instancia(response)

    #request da 2a instancia
    url = "https://www2.tjal.jus.br/cposg5/show.do"
    params = {
        "processo.codigo": codigo,
    }
    response = make_request(url,params)
    return parse(response,2)

def crawl_tjce_1a_instancia(processo):
    url = "https://esaj.tjce.jus.br/cpopg/search.do"
    params = {
        "cbPesquisa": "NUMPROC",
        "dadosConsulta.valorConsultaNuUnificado": processo,
        "dadosConsulta.tipoNuProcesso": "UNIFICADO"
    }
    response = make_request(url,params)
    return parse(response,1,TJCE)

def crawl_tjce_2a_instancia(processo):
    #request para pegar o código da 2a instancia
    url = "https://esaj.tjce.jus.br/cposg5/search.do"
    params = {
        "cbPesquisa": "NUMPROC",
        "dePesquisaNuUnificado": processo,
        "tipoNuProcesso": "UNIFICADO"
    }
    response = make_request(url,params)
    codigo = get_codigo_2a_instancia(response)

    #request da 2a instancia
    url = "https://esaj.tjce.jus.br/cposg5/show.do"
    params = {
        "processo.codigo": codigo,
    }
    response = make_request(url,params)
    return parse(response,2,TJCE)

def make_request(url,params):
    response = requests.get(url = url,params = params)
    return response.text

def parse(response,instancia=1,localizacao=TJAL):
    #agora estamos na página que queremos coletar as infos
    html = BeautifulSoup(response,"html.parser")
    area = get_text_from_id(html, "#areaProcesso")
    classe = get_text_from_id(html,"#classeProcesso")
    vara = get_text_from_id(html,"#varaProcesso")
    assunto = get_text_from_id(html,"#assuntoProcesso")
    juiz = get_text_from_id(html,"#juizProcesso")
    valor = get_number_from_id(html,"#valorAcaoProcesso")
    data = get_text_from_id(html,"#dataHoraDistribuicaoProcesso")
    movimentacoes = get_movimentacoes(html)
    partes = get_partes(html)

    return remove_nulls_from_dict({
        'localizacao': localizacao,
        'instancia':instancia,
        'area':area,
        'classe':classe,
        'vara':vara,
        'assunto':assunto,
        'juiz':juiz,
        'valor':valor,
        'data_distribuicao':data,
        'movimentacoes':movimentacoes,
        'partes':partes
    })

def get_text_from_id(html, idd):
    try:
        return html.select_one(idd).get_text(strip=True)
    except:
        return None

def get_number_from_id(html, idd):
    try:
        return get_clean_number(html.select_one(idd).get_text(strip=True))
    except:
        return None

def get_value_from_id(html,idd):
    try:
        return html.select_one(idd)['value']
    except:
    	return ""

def get_partes(html):
    partes = {}
    try:
        tds = html.select_one("#tablePartesPrincipais").findAll("td")
        partes_array = [x.get_text(strip=True).replace("Advogado",", Advogado").replace("Advogada",", Advogada") for x in tds]
        for x in range(0,len(partes_array),2):
            
            partes[partes_array[x]]=partes_array[x+1]
    except Exception as e:
        partes = None

    return partes

def get_movimentacoes(html):
    movimentacoes = []
    try:
        tds = html.select_one("#tabelaTodasMovimentacoes").findAll("td")
        movimentacoes_array = [x.get_text().strip() for x in tds if x.get_text(strip=True) != ""]
        for x in range(0,len(movimentacoes_array),2):
            movimentacao =  {
                                'data':movimentacoes_array[x],
                                'descricao':[x.strip() for x in movimentacoes_array[x+1].split("\n") if x.strip() != ""]
                            }
            movimentacoes.append(movimentacao)
    except Exception as e:
        movimentacoes = None

    return movimentacoes

def get_clean_number(text):
    return float(text.replace("R$","").replace(" ","").replace(".","").replace(",","."))

def get_codigo_2a_instancia(response):
    html = BeautifulSoup(response,"html.parser")
    return get_value_from_id(html,"#processoSelecionado")

def remove_nulls_from_dict(dictionary):
	new_dict = {k: v for k, v in dictionary.items() if v}
	if len(new_dict) == 2:
		return {}

	return new_dict
