import requests, datetime, os, re
from bs4 import BeautifulSoup
# from orders.scrapers.util import exceptions
from util import exceptions

import dotenv
dotenv.load_dotenv()

TRACK_URL = 'https://www2.correios.com.br/sistemas/rastreamento/ctrl/ctrlRastreamento.cfm?'
BASE_URL = 'https://apps.correios.com.br'
LOGIN_ENDPOINT = '/portalimportador'


def _parse_info(resp):
    soup = BeautifulSoup(resp.content, 'lxml')\
        .find('div', class_='ctrlcontent').find_all('table', class_='listEvent')
    items = [
        i.find_all('td') for i in soup
    ]
    parsed = []
    need_cpf = False

    for i in items:
        description = ' '.join(i[1].text.strip().split())
        index = description.find('Informar nº do documento para a fiscalização')
        if index != -1:
            description = description[:index].strip()
            need_cpf = True
        
        parsed.append({
            'Date': datetime.datetime.strptime(
                ' '.join(i[0].text.strip().split()[:2]),
                '%d/%m/%Y %H:%M'
            ),
            'Place': ''.join(i[0].text.strip().split()[2:]),
            'Info': {
                'Status': i[1].find('strong').text.strip(),
                'Description': description,
            }
        })
    parsed.reverse()
    return parsed, need_cpf


def delivery_info(code : str):
    if len(code) != 13:
        raise exceptions.InvalidTrackingCode

    s = requests.Session()
    resp = s.post(TRACK_URL, data={
        'acao': 'track',
        'objetos': code,
        'btnPesq': 'Buscar',
    })
    
    if 'Aguardando postagem pelo remetente' in resp.text:
        raise exceptions.OrderNotShipped
    
    result, need_cpf = _parse_info(resp)
    return result, need_cpf


def _do_login(s):
    resp = s.get(BASE_URL + LOGIN_ENDPOINT)
    link = BeautifulSoup(resp.content, 'lxml')\
        .find('head').find('meta', attrs={'http-equiv': 'Refresh'})\
            ['content'][len('0;url='):]
    resp = s.get(BASE_URL + link)
    
    soup = BeautifulSoup(resp.content, 'lxml').find('form')
    form_data = {
        'username': os.getenv('MY_EMAIL'),
        'password': os.getenv('CORREIOS_PASS'),
        'lt': soup.find('input', attrs={'name': 'lt'})['value'],
        'execution': soup.find('input', attrs={'name': 'execution'})['value'],
        '_eventId': soup.find('input', attrs={'name': '_eventId'})['value'],
    }
    link = soup['action']
    
    return s.post(BASE_URL + link, data=form_data)


def _find_item(s, resp, code):
    soup = BeautifulSoup(resp.content, 'lxml')\
        .find('div', class_='content').find('form')
    form_data = {
        'form-pesquisarRemessas': 'form-pesquisarRemessas',
        'form-pesquisarRemessas:codigoEncomenda': code,
        'form-pesquisarRemessas:j_idt65:j_idt77': '1',
        'form-pesquisarRemessas:j_idt115:j_idt127': '1',
        'javax.faces.ViewState': \
            soup.find('input', id='javax.faces.ViewState')['value'],
        'javax.faces.source': 'form-pesquisarRemessas:btnPesquisar',
        'javax.faces.partial.event': 'click',
        'javax.faces.partial.execute': \
            'form-pesquisarRemessas:btnPesquisar form-pesquisarRemessas',
        'javax.faces.partial.render': 'form-pesquisarRemessas',
        'javax.faces.behavior.event': 'action',
        'javax.faces.partial.ajax': 'true',
    }
    link = soup['action']
    resp = s.post(BASE_URL + link, data=form_data)
    
    if 'Nenhum registro encontrado.' in resp.text:
        raise exceptions.OrderNotFound
    
    link = resp.text.split('<redirect url="')[-1].split('"></redirect>')[0]

    if '</div>' in link:
        raise exceptions.DocumentAlreadyRegistered

    return s.get(BASE_URL + link)


def _register_cpf(s, resp):
    soup = BeautifulSoup(resp.content).find('form', id='form-autodeclaracao')
    form_data = {
        'form-autodeclaracao': 'form-autodeclaracao',
        'form-autodeclaracao:tipoDocumentoImportador': '1',
        'form-autodeclaracao:numDocumentoImportador': os.getenv('MY_CPF'),
        'form-autodeclaracao:btnSalvar': 'Salvar',
        'javax.faces.ViewState': soup.find(
            'input', id='javax.faces.ViewState'
        )['value'],
    }
    resp = s.post(BASE_URL + soup['action'], data=form_data)

    return resp


def register_cpf(code : str):
    if len(code) != 13:
        raise exceptions.InvalidTrackingCode
    
    s = requests.Session()
    resp = _do_login(s)
    resp = _find_item(s, resp, code)
    resp = _register_cpf(s, resp)
    

if __name__ == '__main__':
    register_cpf('LB332085924SE')
    # delivery_info('LB332085924SE')
