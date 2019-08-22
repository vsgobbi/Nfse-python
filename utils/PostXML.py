import re
import requests
import tempfile
from lxml import etree
from utils.Utils import CertData
from json import dumps

NAMESPACE_NFE = 'http://www.portalfiscal.inf.br/nfe'
NAMESPACE_NFE_PREFEITURA = 'http://www.prefeitura.sp.gov.br/nfe'
NAMESPACE_SIG = 'http://www.w3.org/2000/09/xmldsig#'
NAMESPACE_SOAP = 'http://www.w3.org/2003/05/soap-envelope'
NAMESPACE_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NAMESPACE_XSD = 'http://www.w3.org/2001/XMLSchema'
NAMESPACE_METODO = 'http://www.portalfiscal.inf.br/nfe/wsdl/'
NAMESPACE_METODO_PREFEITURA = 'http://www.prefeitura.sp.gov.br/nfe'

NFSE = {
    'AUTORIZACAO': 'https://nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx'
}    # Prefeitura nao possui ambiente de homologacao para nfse

NFE = {
        'SP': {
        'STATUS': 'nfe.fazenda.sp.gov.br/ws/nfestatusservico4.asmx',
        'AUTORIZACAO': 'nfe.fazenda.sp.gov.br/ws/nfeautorizacao4.asmx',
        'RECIBO': 'nfe.fazenda.sp.gov.br/ws/nferetautorizacao4.asmx',
        'CHAVE': 'nfe.fazenda.sp.gov.br/ws/nfeconsultaprotocolo4.asmx',
        'INUTILIZACAO': 'nfe.fazenda.sp.gov.br/ws/nfeinutilizacao4.asmx',
        'EVENTOS': 'nfe.fazenda.sp.gov.br/ws/nferecepcaoevento4.asmx',
        'CADASTRO': 'nfe.fazenda.sp.gov.br/ws/cadconsultacadastro4.asmx',
        'HTTPS': 'https://',
        'HOMOLOGACAO': 'https://homologacao.'
        },
        'PREFEITURA': {
        'STATUS': 'nfe.fazenda.sp.gov.br/ws/nfestatusservico4.asmx',
        'CADASTRO': 'nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx',
        'AUTORIZACAO': 'nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx',
        'CANCELAMENTO': 'nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx',
        'CONSULTA': 'nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx',
        'TESTEENVIOLOTERPS': 'nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx',
        'ENVIOLOTERPS': 'nfe.prefeitura.sp.gov.br/ws/lotenfe.asmx',
        'HTTPS': 'https://',
        }
    }


class PostXML:

    def __init__(self, uf, cert, key):
        self.uf = uf
        self.ambiente = 2 if uf == "SP" else 1
        self.cert = cert
        self.key = key
        self.entityType = ["SP", "PREFEITURA"]

    def _get_url(self, consulta):
        lista = ["SP", 'PREFEITURA']
        if self.uf.upper() in lista:
            if self.ambiente == 1:
                ambiente = 'HTTPS'
                self.url = NFE[self.uf.upper()][ambiente] + NFE[self.uf.upper()][consulta]
            else:
                ambiente = 'HOMOLOGACAO'
                self.url = NFE[self.uf.upper()][ambiente] + NFE[self.uf.upper()][consulta]
        return self.url

    def _post_header(self):
        response = {
            'content-type': 'application/soap+xml; charset=utf-8;',
            'Accept': 'application/soap+xml; charset=utf-8;',
        }
        return response

    def _post(self, url, xml):
        try:
            xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
            xml = re.sub(
                '<qrCode>(.*?)</qrCode>',
                lambda x: x.group(0).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', ''),
                etree.tostring(xml, encoding='unicode').replace('\n', '')
            )
            xml = xml_declaration + xml

            # Must create cert and key with white spaces :
            with open(self.cert, "rb") as certBuffer:
                certBuffer = certBuffer.read()
            with open(self.key, "rb") as keyBuffer:
                keyBuffer = keyBuffer.read()

            with tempfile.NamedTemporaryFile(delete=False) as arqcert:
                arqcert.write(certBuffer)
            with tempfile.NamedTemporaryFile(delete=False) as arqchave:
                arqchave.write(keyBuffer)

            cert_key = (arqcert.name, arqchave.name)
            result = requests.post(url, xml, headers=self._post_header(),
                                   cert=cert_key, verify=False)
            print "Request Status: {}".format(result.status_code)
            result.encoding = 'utf-8'
            xmlResult = str(result.content)
            xmlResult = xmlResult.replace("&lt;", "<")
            xmlResult = xmlResult.replace("&gt;", ">")
            return str(xmlResult)
        except requests.exceptions.RequestException as e:
            raise e

    def resultDissector(self, xmlResult):
        if ("""ConsultaCNPJResponse xmlns=""" and """<Sucesso>true</Sucesso>""") in xmlResult:
            splitResult = xmlResult.split("""</Cabecalho>""")
            strResult = (splitResult[1].split("</Retorno"))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            return self._resultDict(strResult)
        if ("""EnvioRPSResponse""" and """<Sucesso>true</Sucesso>""") in xmlResult:
            splitResult = xmlResult.split("""<Alerta xmlns="">""")
            strResult = (splitResult[1].split("""</Alerta>"""))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            return self._resultDict(strResult)
        if """Erro xmlns""" in xmlResult:
            splitResult = xmlResult.split("""<Erro xmlns="">""")
            strResult = (splitResult[1].split("""</Erro>"""))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            return self._resultDict(strResult)
        if ("""EnvioRPSResponse""" and """<Sucesso>false</Sucesso>""") in xmlResult:
            splitResult = xmlResult.split("""<Alerta xmlns="">""")
            strResult = (splitResult[1].split("""</Alerta>"""))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            return self._resultDict(strResult)
        else:
            xmlResult = xmlResult[38:]
            splitResult = xmlResult.split("<soap:Body>")
            strResult = (splitResult[1].split("</soap:Body>"))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            return self._resultDict(strResult)

    def _resultDict(self, strResult):
        res = {}
        root = etree.fromstring(strResult)
        for i in root.iter():
            text = i.text
            text = text.encode("utf-8", "replace") if text else None
            if text is not None:
                res.setdefault("{tag}".format(tag=i.tag), "{text}".format(text=text))
        return dumps(res, ensure_ascii=False)

    def _construir_xml_soap(self, metodo, dados, orgao_publico):
        self.entityType = orgao_publico
        if orgao_publico == "SP":
            raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
              'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
            body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
            a = etree.SubElement(body, 'nfeDadosMsg', xmlns=NAMESPACE_METODO+metodo)
            a.append(dados)
        elif self.entityType == "PREFEITURA":
            raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
                'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
            body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
            a = etree.SubElement(body, 'ConsultaCNPJRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
            etree.SubElement(a, "VersaoSchema").text = "1"
            a.append(dados)
        else:
            return "Nao foi possivel verificar tipo de servico"
        return raiz

    def consultaCNPJ(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'ConsultaCNPJRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='CADASTRO')
        return self._post(url, raiz)

    def consultaNFe(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'ConsultaNFeRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='CONSULTA')
        return self._post(url, raiz)

    def cancelaNfe(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'CancelamentoNFeRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        url = self._get_url(consulta="CANCELAMENTO")
        return self._post(url, raiz)

    def testeEnvioLoteRPS(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'TesteEnvioLoteRPSRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='TESTEENVIOLOTERPS')
        return self._post(url, raiz)

    def envioLoteRPS(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'EnvioLoteRPSRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='ENVIOLOTERPS')
        return self._post(url, raiz)

    def envioRPS(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'EnvioRPSRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='AUTORIZACAO')
        return self._post(url, raiz)

    def consultaNFeRecebidas(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'ConsultaNFeRecebidasRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='CONSULTA')
        return self._post(url, raiz)

    def consultaNFeEmitidas(self, signedXml):
        raiz = etree.Element('{%s}Envelope' % NAMESPACE_SOAP, nsmap={
            'xsi': NAMESPACE_XSI, 'xsd': NAMESPACE_XSD, 'soap': NAMESPACE_SOAP})
        body = etree.SubElement(raiz, '{%s}Body' % NAMESPACE_SOAP)
        a = etree.SubElement(body, 'ConsultaNFeEmitidasRequest', xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, 'MensagemXML')
        mensagemXml.text = signedXml
        print("Envelope assinado: ")
        print(etree.tostring(raiz))
        url = self._get_url(consulta='CONSULTA')
        return self._post(url, raiz)

    def consultaCadastro(self, cnpj):
        if self.uf.upper() == 'SP':
            url = NFE['SP']['CADASTRO']
            raiz = etree.Element('ConsCad', versao='2.00', xmlns=NAMESPACE_NFE)
            info = etree.SubElement(raiz, 'infCons')
            etree.SubElement(info, 'xServ').text = 'CONS-CAD'
            etree.SubElement(info, 'UF').text = self.uf.upper()
            etree.SubElement(info, 'CNPJ').text = cnpj
            xml = self._construir_xml_soap('CadConsultaCadastro4', raiz, self.uf)
            url = self._get_url(consulta='CADASTRO')
            return self._post(url, xml)

        elif self.uf.upper() == 'PREFEITURA':
            url = NFE['PREFEITURA']['CADASTRO']
            raiz = etree.Element('MensagemXML')
            p1 = 'PedidoConsultaCNPJ'
            info = etree.SubElement(raiz, _tag=p1, versao='4.00',
                                    nsmap={'xmlns': NAMESPACE_XSD, 'xsi': NAMESPACE_XSI})
            cabecalho = etree.SubElement(raiz, 'Cabecalho', Versao="1")
            remetente = etree.SubElement(cabecalho, "CNPJRemetente")
            etree.SubElement(remetente, 'CNPJ').text = cnpj
            contribuinte = etree.SubElement(raiz, 'CNPJContribuinte')
            etree.SubElement(contribuinte, 'CNPJ').text = cnpj
            xmlToSign = etree.tostring(raiz)
            signedEnvelope = CertData(certFile=self.cert, keyFile=self.key)
            xmlSigned = signedEnvelope.signWithCert(xmlToSign, key=self.key)
            xmlSigned = (etree.fromstring(xmlSigned))
            xmlSigned = self._construir_xml_soap('ConsultaCNPJRequest', xmlSigned, self.uf)
            url = self._get_url(consulta='CADASTRO')

            print("Envelope assinado:")
            print(etree.tostring(xmlSigned))

            return self._post(url, xmlSigned)

        else:
            url = self._get_url(consulta='CADASTRO')
            raiz = etree.Element('ConsCad', versao='2.00', xmlns=NAMESPACE_NFE)
            info = etree.SubElement(raiz, 'infCons')
            etree.SubElement(info, 'xServ').text = 'CONS-CAD'
            etree.SubElement(info, 'UF').text = self.uf.upper()
            etree.SubElement(info, 'CNPJ').text = cnpj
            xml = self._construir_xml_soap('ConsultaCNPJ', raiz, self.uf)
            return self._post(url, xml)

    def status_servico(self):

        url = self._get_url('STATUS')
        raiz = etree.Element('consStatServ', versao="4.00", xmlns=NAMESPACE_NFE)
        etree.SubElement(raiz, 'tpAmb').text = str(self.ambiente)
        etree.SubElement(raiz, 'cUF').text = "35"
        etree.SubElement(raiz, 'xServ').text = "STATUS"
        xml = self._construir_xml_soap('NFeStatusServico4', raiz, self.uf)
        print(etree.tostring(xml))
        return self._post(url, xml)

    def autorizacao(self, nota, consulta):

        url = self._get_url(consulta=consulta)
        if consulta == "SP":
            xml = etree.tostring(nota, encoding='unicode', pretty_print=False)
            # comunicacao via wsdl
            return self._post(url, xml)
        elif consulta == "PREFEITURA":
            xmlPrefeitura = etree.tostring(nota, encoding='unicode', pretty_print=True)
            print(xmlPrefeitura)
            return self._post(url, xmlPrefeitura)
        else:
            raise Exception("Metodo criado somente para SEFAZ 'SP' ou 'PREFEITURA' de SP")

    def consulta_recibo(self, number):

        url = self._get_url(consulta='RECIBO')
        raiz = etree.Element('consReciNFe', versao="4.00", xmlns=NAMESPACE_NFE)
        etree.SubElement(raiz, 'tpAmb').text = str(self.ambiente)
        etree.SubElement(raiz, 'nRec').text = number
        xml = self._construir_xml_soap('NFeRetAutorizacao4', raiz, self.uf)
        return self._post(url, xml)
