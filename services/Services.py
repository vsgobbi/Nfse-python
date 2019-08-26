from utils import soapMessages
from utils.formatCurrency import Currency
from utils.PostXML import PostXML
from utils.SignerXML import SignCert
from lxml import etree


class Services(object):

    def __init__(self, privateKeyFile, certificateFile, privateKeyRSA=None):
        self.objSignCert = SignCert(privateKeyFile=privateKeyFile,
                                    certificateFile=certificateFile,
                                    privateKeyRSA=privateKeyRSA)
        self.objSignCert.loadPem()
        self.postObj = PostXML(cert=certificateFile, key=privateKeyRSA, uf="PREFEITURA")

    def consultTaxIdInscription(self, taxId, taxPayerId):
        consultCNPJTree = etree.fromstring(soapMessages.consultaCNPJ)
        consultCNPJTree.find('.//CNPJ', namespaces={}).text = taxId
        consultCNPJTree.find('.//CNPJContribuinte/CNPJ', namespaces={}).text = taxPayerId
        signedConsultaCNPJ = self.objSignCert.signA1Cert(consultCNPJTree)
        result = self.postObj.consultSubscription(signedXml=signedConsultaCNPJ)
        return self.postObj.resultDissector(xmlResult=result)

    def consultNfe(self, nfe, taxId):
        consultNfeTree = etree.fromstring(soapMessages.consultaNFe)
        consultNfeTree.find('.//CNPJ', namespaces={}).text = taxId
        consultNfeTree.find('.//NumeroNFe', namespaces={}).text = nfe
        signedConsultaCNPJ = self.objSignCert.signA1Cert(bufferXml=consultNfeTree)
        result = self.postObj.consultNfe(signedXml=signedConsultaCNPJ)
        return self.postObj.resultDissector(xmlResult=result)

    def sendRPS(self, taxId, providerSubscription, rpsSeries, rpsNum, rpsType, issueDate, rpsStatus, rpsTax,
                servicesValues, deductionsValues, pisValue, cofinsValue, inssValue, serviceCode, aliquot,
                takerTaxId, companyName, street, streetNumber, addressComplement, district,
                zipCode, email, description):
        sendRPSTree = etree.fromstring(soapMessages.envioRPS)
        sendRPSTree.find('.//CNPJ', namespaces={}).text = taxId
        sendRPSTree.find('.//InscricaoPrestador', namespaces={}).text = providerSubscription
        sendRPSTree.find('.//SerieRPS', namespaces={}).text = rpsSeries
        sendRPSTree.find('.//NumeroRPS', namespaces={}).text = rpsNum
        sendRPSTree.find('.//TipoRPS', namespaces={}).text = rpsType
        sendRPSTree.find('.//DataEmissao', namespaces={}).text = issueDate
        sendRPSTree.find('.//StatusRPS', namespaces={}).text = rpsStatus
        sendRPSTree.find('.//TributacaoRPS', namespaces={}).text = rpsTax
        sendRPSTree.find('.//ValorServicos', namespaces={}).text = servicesValues
        sendRPSTree.find('.//ValorDeducoes', namespaces={}).text = deductionsValues
        sendRPSTree.find('.//ValorPIS', namespaces={}).text = pisValue
        sendRPSTree.find('.//ValorCOFINS', namespaces={}).text = cofinsValue
        sendRPSTree.find('.//ValorINSS', namespaces={}).text = inssValue
        sendRPSTree.find('.//CodigoServico', namespaces={}).text = serviceCode
        sendRPSTree.find('.//AliquotaServicos', namespaces={}).text = Currency.formatted(aliquot)
        sendRPSTree.find('.//CPFCNPJTomador/CNPJ', namespaces={}).text = takerTaxId
        sendRPSTree.find('.//RazaoSocialTomador', namespaces={}).text = companyName
        sendRPSTree.find('.//EnderecoTomador/Logradouro', namespaces={}).text = street
        sendRPSTree.find('.//EnderecoTomador/NumeroEndereco', namespaces={}).text = streetNumber
        sendRPSTree.find('.//EnderecoTomador/ComplementoEndereco', namespaces={}).text = addressComplement
        sendRPSTree.find('.//EnderecoTomador/Bairro', namespaces={}).text = district
        sendRPSTree.find('.//EnderecoTomador/CEP', namespaces={}).text = zipCode
        sendRPSTree.find('.//EmailTomador', namespaces={}).text = email
        sendRPSTree.find('.//Discriminacao', namespaces={}).text = description

        signedRPS = self.objSignCert.signRPSWithRSA(sendRPSTree)
        result = self.postObj.sendRPS(signedXml=signedRPS)
        return self.postObj.resultDissector(xmlResult=result)

    def bulkingRPS(self):
        signedEnvioLoteRPS = self.objSignCert.signLoteRPS(soapMessages.envioLoteRPS)
        result = self.postObj.envioLoteRPS(signedXml=signedEnvioLoteRPS)
        return self.postObj.resultDissector(xmlResult=result)

    def cancelNfe(self, taxId, providerSubscription, nfeNum):
        cancelTree = etree.fromstring(soapMessages.cancelamentoNota)
        cancelTree.find('.//CNPJ', namespaces={}).text = taxId
        cancelTree.find('.//InscricaoPrestador', namespaces={}).text = providerSubscription
        cancelTree.find('.//NumeroNFe', namespaces={}).text = nfeNum
        signedCancelContent = self.objSignCert.signCancelWithCrypto(cancelTree)
        result = self.postObj.cancelNfe(signedXml=signedCancelContent)
        return self.postObj.resultDissector(xmlResult=result)

    def consultReceivedNfe(self, cnpj, initDate, endDate, receiverTaxId, subscription):
        consultTree = etree.fromstring(soapMessages.consultaNfePeriodo)
        consultTree.find('.//CPFCNPJRemetente/CNPJ', namespaces={}).text = cnpj
        consultTree.find('.//dtInicio', namespaces={}).text = initDate
        consultTree.find('.//dtFim', namespaces={}).text = endDate
        consultTree.find('.//CPFCNPJ/CNPJ', namespaces={}).text = receiverTaxId
        consultTree.find('.//Inscricao', namespaces={}).text = subscription
        signedReceivedTree = self.objSignCert.signA1Cert(consultTree)
        result = self.postObj.consultReceivedNfe(signedXml=signedReceivedTree)
        return self.postObj.resultDissector(xmlResult=result)

    def consultSentNfe(self, cnpj, initDate, endDate, providerTaxId, subscription):
        consultTree = etree.fromstring(soapMessages.consultaNfePeriodo)
        consultTree.find('.//CPFCNPJRemetente/CNPJ', namespaces={}).text = cnpj
        consultTree.find('.//dtInicio', namespaces={}).text = initDate
        consultTree.find('.//dtFim', namespaces={}).text = endDate
        consultTree.find('.//CPFCNPJ/CNPJ', namespaces={}).text = providerTaxId
        consultTree.find('.//Inscricao', namespaces={}).text = subscription
        signedSentTree = self.objSignCert.signA1Cert(consultTree)
        result = self.postObj.consultSentNfe(signedXml=signedSentTree)
        return self.postObj.resultDissector(xmlResult=result)
