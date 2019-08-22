from utils import soapMessages
from utils.formatCurrency import Currency
from utils.PostXML import PostXML
from utils.SignerXML import SignCert
from lxml import etree


class Services:

    def __init__(self, privateKeyFile, certificateFile, privateKeyRSA=None):
        self.objSignCert = SignCert(privateKeyFile=privateKeyFile,
                                    certificateFile=certificateFile,
                                    privateKeyRSA=privateKeyRSA)
        self.objSignCert.loadPem()
        self.postObj = PostXML(cert=certificateFile, key=privateKeyRSA, uf="PREFEITURA")

    def consultaNFE(self, nfe, cnpj):
        consultaNFEtree = etree.fromstring(soapMessages.consultaNFe)
        consultaNFEtree.find('.//CNPJ', namespaces={}).text = cnpj
        consultaNFEtree.find('.//NumeroNFe', namespaces={}).text = nfe
        signedConsultaCNPJ = self.objSignCert.signA1Cert(consultaNFEtree)
        result = self.postObj.consultaNFe(signedXml=signedConsultaCNPJ)
        return self.postObj.resultDissector(xmlResult=result)

    def envioRPS(self, cnpj, inscricaoPrestador, serieRPS, numeroRPS, tipoRPS, dtEmissao, statusRPS, tributacaoRPS,
                 valorServicos, valorDeducoes, valorPis, valorCofins, valorINSS, codigoServico, aliquota,
                 cnpjTomador, razaoSocialTomador, logradouro, numero, complemento, bairro,
                 cep, email, discriminacao):
        envioRPSTree = etree.fromstring(soapMessages.envioRPS)
        envioRPSTree.find('.//CNPJ', namespaces={}).text = cnpj
        envioRPSTree.find('.//InscricaoPrestador', namespaces={}).text = inscricaoPrestador
        envioRPSTree.find('.//SerieRPS', namespaces={}).text = serieRPS
        envioRPSTree.find('.//NumeroRPS', namespaces={}).text = numeroRPS
        envioRPSTree.find('.//TipoRPS', namespaces={}).text = tipoRPS
        envioRPSTree.find('.//DataEmissao', namespaces={}).text = dtEmissao
        envioRPSTree.find('.//StatusRPS', namespaces={}).text = statusRPS
        envioRPSTree.find('.//TributacaoRPS', namespaces={}).text = tributacaoRPS
        envioRPSTree.find('.//ValorServicos', namespaces={}).text = valorServicos
        envioRPSTree.find('.//ValorDeducoes', namespaces={}).text = valorDeducoes
        envioRPSTree.find('.//ValorPIS', namespaces={}).text = valorPis
        envioRPSTree.find('.//ValorCOFINS', namespaces={}).text = valorCofins
        envioRPSTree.find('.//ValorINSS', namespaces={}).text = valorINSS
        envioRPSTree.find('.//CodigoServico', namespaces={}).text = codigoServico
        envioRPSTree.find('.//AliquotaServicos', namespaces={}).text = Currency.formatted(aliquota)
        envioRPSTree.find('.//CPFCNPJTomador/CNPJ', namespaces={}).text = cnpjTomador
        envioRPSTree.find('.//RazaoSocialTomador', namespaces={}).text = razaoSocialTomador
        envioRPSTree.find('.//EnderecoTomador/Logradouro', namespaces={}).text = logradouro
        envioRPSTree.find('.//EnderecoTomador/NumeroEndereco', namespaces={}).text = numero
        envioRPSTree.find('.//EnderecoTomador/ComplementoEndereco', namespaces={}).text = complemento
        envioRPSTree.find('.//EnderecoTomador/Bairro', namespaces={}).text = bairro
        envioRPSTree.find('.//EnderecoTomador/CEP', namespaces={}).text = cep
        envioRPSTree.find('.//EmailTomador', namespaces={}).text = email
        envioRPSTree.find('.//Discriminacao', namespaces={}).text = discriminacao

        signedRPS = self.objSignCert.signRPSWithRSA(envioRPSTree)
        result = self.postObj.envioRPS(signedXml=signedRPS)
        return self.postObj.resultDissector(xmlResult=result)

    def envioLoteRPS(self):
        signedEnvioLoteRPS = self.objSignCert.signLoteRPS(soapMessages.envioLoteRPS)
        result = self.postObj.envioLoteRPS(signedXml=signedEnvioLoteRPS)
        return self.postObj.resultDissector(xmlResult=result)

    def consultaCNPJ(self, cnpj, cnpjContribuinte):
        consultaCNPJTree = etree.fromstring(soapMessages.consultaCNPJ)
        consultaCNPJTree.find('.//CNPJ', namespaces={}).text = cnpj
        consultaCNPJTree.find('.//CNPJContribuinte/CNPJ', namespaces={}).text = cnpjContribuinte
        signedConsultaCNPJ = self.objSignCert.signA1Cert(consultaCNPJTree)
        result = self.postObj.consultaCNPJ(signedXml=signedConsultaCNPJ)
        return self.postObj.resultDissector(xmlResult=result)

    def cancelaNFe(self, cnpj, inscricao, nfe):
        cancelTree = etree.fromstring(soapMessages.cancelamentoNota)
        cancelTree.find('.//CNPJ', namespaces={}).text = cnpj
        cancelTree.find('.//InscricaoPrestador', namespaces={}).text = inscricao
        cancelTree.find('.//NumeroNFe', namespaces={}).text = nfe
        signedCancelContent = self.objSignCert.signCancelWithCrypto(cancelTree)
        print signedCancelContent
        result = self.postObj.cancelaNfe(signedXml=signedCancelContent)
        return self.postObj.resultDissector(xmlResult=result)

    def consultaNFeRecebidas(self, cnpj, dtInicio, dtFim, cnpjTomador, inscricao):
        consultaTree = etree.fromstring(soapMessages.consultaNfePeriodo)
        consultaTree.find('.//CPFCNPJRemetente/CNPJ', namespaces={}).text = cnpj
        consultaTree.find('.//dtInicio', namespaces={}).text = dtInicio
        consultaTree.find('.//dtFim', namespaces={}).text = dtFim
        consultaTree.find('.//CPFCNPJ/CNPJ', namespaces={}).text = cnpjTomador
        consultaTree.find('.//Inscricao', namespaces={}).text = inscricao
        signedConsultaRecebidas = self.objSignCert.signA1Cert(consultaTree)
        print(signedConsultaRecebidas)
        result = self.postObj.consultaNFeRecebidas(signedXml=signedConsultaRecebidas)
        return self.postObj.resultDissector(xmlResult=result)

    def consultaNFeEmitidas(self, cnpj, dtInicio, dtFim, cnpjPrestador, inscricao):
        consultaTree = etree.fromstring(soapMessages.consultaNfePeriodo)
        consultaTree.find('.//CPFCNPJRemetente/CNPJ', namespaces={}).text = cnpj
        consultaTree.find('.//dtInicio', namespaces={}).text = dtInicio
        consultaTree.find('.//dtFim', namespaces={}).text = dtFim
        consultaTree.find('.//CPFCNPJ/CNPJ', namespaces={}).text = cnpjPrestador
        consultaTree.find('.//Inscricao', namespaces={}).text = inscricao
        signedConsultaEmitidas = self.objSignCert.signA1Cert(consultaTree)
        print(signedConsultaEmitidas)
        result = self.postObj.consultaNFeEmitidas(signedXml=signedConsultaEmitidas)
        return self.postObj.resultDissector(xmlResult=result)
