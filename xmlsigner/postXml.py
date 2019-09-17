import requests
import ssl
import re
import socket

from lxml import etree
from xmlsigner.certMethods import Certificate
from xmlsigner.customHttpConnection import NewAdapter


NAMESPACE_NFE = 'http://www.portalfiscal.inf.br/nfe'
NAMESPACE_NFE_PREFEITURA = 'http://www.prefeitura.sp.gov.br/nfe'
NAMESPACE_SOAP = 'http://www.w3.org/2003/05/soap-envelope'
NAMESPACE_XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NAMESPACE_XSD = 'http://www.w3.org/2001/XMLSchema'
NAMESPACE_METODO = 'http://www.portalfiscal.inf.br/nfe/wsdl/'
NAMESPACE_METODO_PREFEITURA = 'http://www.prefeitura.sp.gov.br/nfe'

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

    def __init__(self, cert, key, uf="PREFEITURA"):
        self.environment = 2 if uf == "SP" else 1
        self.cert = cert
        self.key = key
        self.uf = uf
        self.entityType = ["SP", "PREFEITURA"]

    def _getUrl(self, type):
        lista = ["SP", 'PREFEITURA']
        if self.uf.upper() in lista:
            if self.environment == 1:
                environment = 'HTTPS'
                self.url = NFE[self.uf.upper()][environment] + NFE[self.uf.upper()][type]
            else:
                environment = 'HOMOLOGACAO'
                self.url = NFE[self.uf.upper()][environment] + NFE[self.uf.upper()][type]
        return self.url

    def _postHeaders(self):
        response = {
            'content-type': 'application/soap+xml; charset=utf-8;',
            'Accept': 'application/soap+xml; charset=utf-8;',
            'Cache-Control': "no-cache",
            'Host': "nfe.prefeitura.sp.gov.br",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
        }
        return response

    def _post(self, url, xml):
        try:
            xmlDef = '<?xml version="1.0" encoding="UTF-8"?>'
            xml = re.sub('<>(.*?)</>',
                         lambda x: x.group(0).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', ''),
                         etree.tostring(xml, encoding='unicode').replace('\n', '')
                         )
            xml = xmlDef + xml

            certFile = "../certfiles/certStark.pem"
            keyFile = "../certfiles/privateKey.key"

            multipleFiles = [
                ('cert', ('certStark.pem', open('../certfiles/certStark.pem', 'rb'), 'text/text')),
                ('key', ('privateKey.key', open('../certfiles/privateKey.key', 'rb'), 'text/text'))]

            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.settimeout(20)
            socks = ssl.wrap_socket(sock=clientSocket,
                                    keyfile=keyFile,
                                    certfile=certFile,
                                    cert_reqs=ssl.CERT_REQUIRED,
                                    ssl_version=ssl.PROTOCOL_TLSv1,
                                    ca_certs="../venv/lib/python2.7/site-packages/certifi/cacert.pem",
                                    )

            s = requests.Session()

            s.mount('http://', NewAdapter(soqt=socks))
            s.mount('https://', NewAdapter(soqt=socks))

            result = s.post(url, xml, headers=self._postHeaders(), verify=True)

            self.requestStatus = result.status_code
            print "Request Status: {}".format(self.requestStatus)
            result.encoding = "utf-8"
            xmlResult = str(result.content)
            xmlResult = xmlResult.replace("&lt;", "<")
            xmlResult = xmlResult.replace("&gt;", ">")
            if self.requestStatus == 200:
                return self._resultDissector(xmlResult)
            return xmlResult
        except requests.exceptions.RequestException as e:
            raise e

    def _resultDissector(self, xmlResult):
        print(xmlResult)
        if ("""ConsultaCNPJResponse xmlns=""" and """<Sucesso>true</Sucesso>""") in xmlResult:
            splitResult = xmlResult.split("""</Cabecalho>""")
            strResult = (splitResult[1].split("</Retorno"))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            print(strResult)
            return self._resultDict(strResult)
        if ("""EnvioRPSResponse""" and """<Sucesso>true</Sucesso>""") in xmlResult:
            splitResult = xmlResult.split("""<Alerta xmlns="">""")
            strResult = (splitResult[1].split("""</Alerta>"""))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            print(strResult)
            return self._resultDict(strResult)
        if """Erro xmlns""" in xmlResult:
            splitResult = xmlResult.split("""<Erro xmlns="">""")
            strResult = (splitResult[1].split("""</Erro>"""))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            return self._resultDict(strResult)
        if ("""EnvioRPSResponse""" and """<Sucesso>false</Sucesso>""") in xmlResult:
            splitResult = xmlResult.split("""</Cabecalho>""")
            print(splitResult[1])

            strResult = (splitResult[1].split("""</RetornoEnvioRPS>"""))
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            print("false")
            print(strResult)
            return self._resultDict(strResult)
        else:
            xmlResult = xmlResult[38:]
            splitResult = xmlResult.split("<soap:Body>")
            print(splitResult)
            strResult = splitResult[1].split("</soap:Body>")
            strResult = (str(strResult[0]))
            strResult = "<root>" + strResult + "</root>"
            print("aqui")
            print(strResult)
            return self._resultDict(strResult)

    def _resultDict(self, strResult):
        res = {}
        content = []
        tags = []
        texts = []
        root = etree.fromstring(strResult)
        for i in root.iter():
            # print(i.tag)
            # print(i.text)
            text = i.text
            text = text.encode("utf-8", "replace") if text else None
            if text:
                # tags.append(i.tag)
                # texts.append(text)
                # content.append({"{tag}".format(tag=i.tag), "{text}".format(text=text)})
                content.append("{tag}: ".format(tag=i.tag))
                content.append(text)
        # zipObj = zip(tags, texts)
        print((content))
        # print(dict(zipObj))
        # print(dict(map(None, zipObj)))
            # exit()
            # text = i.text
            # text = text.encode("utf-8", "replace") if text else None
            # if text is not None:
            #     # res.setdefault("{tag}".format(tag=i.tag), "{text}".format(text=text))
            #     res.update({"{tag}".format(tag=i.tag): "{text}".format(text=text)})
            #     content.append(res)
        # return dumps(res, ensure_ascii=False)
        return res

    def _constructXmlSoap(self, metodo, data, publicEntity):
        self.entityType = publicEntity
        if publicEntity == "SP":
            root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
              "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
            body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
            a = etree.SubElement(body, "nfeDadosMsg", xmlns=NAMESPACE_METODO+metodo)
            a.append(data)
            return root
        if self.entityType == "PREFEITURA":
            root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
                "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
            body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
            a = etree.SubElement(body, "ConsultaCNPJRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
            etree.SubElement(a, "VersaoSchema").text = "1"
            a.append(data)
            return root

    def consultSubscription(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "ConsultaCNPJRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="CADASTRO")
        return self._post(url, root)

    def consultNfe(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "ConsultaNFeRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="CONSULTA")
        return self._post(url, root)

    def cancelNfe(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "CancelamentoNFeRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="CANCELAMENTO")
        return self._post(url, root)

    def bulkingRPSTests(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "TesteEnvioLoteRPSRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="TESTEENVIOLOTERPS")
        return self._post(url, root)

    def bulkRPS(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "EnvioLoteRPSRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="ENVIOLOTERPS")
        return self._post(url, root)

    def sendRPS(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "EnvioRPSRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="AUTORIZACAO")
        return self._post(url, root)

    def consultReceivedNfe(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "ConsultaNFeRecebidasRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="CONSULTA")
        return self._post(url, root)

    def consultSentNfe(self, signedXml):
        root = etree.Element("{%s}Envelope" % NAMESPACE_SOAP, nsmap={
            "xsi": NAMESPACE_XSI, "xsd": NAMESPACE_XSD, "soap": NAMESPACE_SOAP})
        body = etree.SubElement(root, "{%s}Body" % NAMESPACE_SOAP)
        a = etree.SubElement(body, "ConsultaNFeEmitidasRequest", xmlns=NAMESPACE_METODO_PREFEITURA)
        etree.SubElement(a, "VersaoSchema").text = "1"
        mensagemXml = etree.SubElement(a, "MensagemXML")
        mensagemXml.text = signedXml
        url = self._getUrl(type="CONSULTA")
        return self._post(url, root)

    def sefazSubscription(self, cnpj):  # Sefaz
        if self.uf.upper() == "SP":
            root = etree.Element("ConsCad", versao="2.00", xmlns=NAMESPACE_NFE)
            info = etree.SubElement(root, "infCons")
            etree.SubElement(info, "xServ").text = "CONS-CAD"
            etree.SubElement(info, "UF").text = self.uf.upper()
            etree.SubElement(info, "CNPJ").text = cnpj
            xml = self._constructXmlSoap("CadConsultaCadastro4", root, self.uf)
            url = self._getUrl(type="CADASTRO")
            return self._post(url, xml)

        elif self.uf.upper() == "PREFEITURA":
            root = etree.Element("MensagemXML")
            p1 = "PedidoConsultaCNPJ"
            info = etree.SubElement(root, _tag=p1, versao="4.00",
                                    nsmap={"xmlns": NAMESPACE_XSD, "xsi": NAMESPACE_XSI})
            cabecalho = etree.SubElement(root, "Cabecalho", Versao="1")
            remetente = etree.SubElement(cabecalho, "CNPJRemetente")
            etree.SubElement(remetente, "CNPJ").text = cnpj
            contribuinte = etree.SubElement(root, "CNPJContribuinte")
            etree.SubElement(contribuinte, "CNPJ").text = cnpj
            xmlToSign = etree.tostring(root)
            xmlSigned = Certificate.signWithA1Cert(xmlToSign, certContent=self.cert, RSAPrivateKeyContent=self.key)
            xmlSigned = (etree.fromstring(xmlSigned))
            xmlSigned = self._constructXmlSoap("ConsultaCNPJRequest", xmlSigned, self.uf)
            url = self._getUrl(type="CADASTRO")

            print("Envelope assinado:")
            print(etree.tostring(xmlSigned))

            return self._post(url, xmlSigned)

        else:
            url = self._getUrl(type="CADASTRO")
            root = etree.Element("ConsCad", versao="2.00", xmlns=NAMESPACE_NFE)
            info = etree.SubElement(root, "infCons")
            etree.SubElement(info, "xServ").text = "CONS-CAD"
            etree.SubElement(info, "UF").text = self.uf.upper()
            etree.SubElement(info, "CNPJ").text = cnpj
            xml = self._constructXmlSoap("ConsultaCNPJ", root, self.uf)
            return self._post(url, xml)

    def serviceStatus(self):  # Consulta status do WebService na Sefaz
        url = self._getUrl("STATUS")
        root = etree.Element("consStatServ", versao="4.00", xmlns=NAMESPACE_NFE)
        etree.SubElement(root, "tpAmb").text = str(self.environment)
        etree.SubElement(root, "cUF").text = "35"
        etree.SubElement(root, "xServ").text = "STATUS"
        xml = self._constructXmlSoap("NFeStatusServico4", root, self.uf)
        print(etree.tostring(xml))
        return self._post(url, xml)

    def autorizacao(self, nota, consulta):  # Envio de nfe na Sefaz
        url = self._getUrl(type=consulta)
        if consulta == "SP":
            xml = etree.tostring(nota, encoding="unicode", pretty_print=False)
            return self._post(url, xml)
        elif consulta == "PREFEITURA":
            xmlPrefeitura = etree.tostring(nota, encoding="unicode", pretty_print=True)
            print(xmlPrefeitura)
            return self._post(url, xmlPrefeitura)
        else:
            raise Exception("""Metodo criado somente para SEFAZ "SP" ou "PREFEITURA" de SP""")

    def receiptConsult(self, number):
        url = self._getUrl(type="RECIBO")
        root = etree.Element("consReciNFe", versao="4.00", xmlns=NAMESPACE_NFE)
        etree.SubElement(root, "tpAmb").text = str(self.environment)
        etree.SubElement(root, "nRec").text = number
        xml = self._constructXmlSoap("NFeRetAutorizacao4", root, self.uf)
        return self._post(url, xml)
