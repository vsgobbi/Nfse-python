from utils import soapMessages
from utils.formatCurrency import Currency
from xmlsigner.postXml import PostXML
from xmlsigner.signerXml import SignCert
from lxml import etree


class Services(object):

    def __init__(self, certificateContent, RSAPrivateKeyContent, privateKeyContent=None):
        self.objSignCert = SignCert(privateKeyContent=privateKeyContent,
                                    certificateContent=certificateContent,
                                    RSAPrivateKeyContent=RSAPrivateKeyContent)
        self.objSignCert.loadPem(certificateContent)
        self.postObj = PostXML(cert=certificateContent, key=RSAPrivateKeyContent)

    def consultTaxIdInscription(self, taxId, taxPayerId):
        consultCNPJTree = etree.fromstring(soapMessages.consultaCNPJ)
        consultCNPJTree.find('.//CNPJ', namespaces={}).text = taxId
        consultCNPJTree.find('.//CNPJContribuinte/CNPJ', namespaces={}).text = taxPayerId
        signedConsultaCNPJ = self.objSignCert.signWithA1Cert(consultCNPJTree)
        return self.postObj.consultSubscription(signedXml=signedConsultaCNPJ)

    def consultNfe(self, nfe, taxId):
        consultNfeTree = etree.fromstring(soapMessages.consultaNFe)
        consultNfeTree.find('.//CNPJ', namespaces={}).text = taxId
        consultNfeTree.find('.//NumeroNFe', namespaces={}).text = nfe
        signedConsultaCNPJ = self.objSignCert.signWithA1Cert(bufferXml=consultNfeTree)
        return self.postObj.consultNfe(signedXml=signedConsultaCNPJ)

    def sendRPS(self, taxId, providerSubscription, rpsSeries, rpsNum, rpsType, issueDate, rpsStatus, issRetain, rpsTax,
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
        sendRPSTree.find('.//ValorServicos', namespaces={}).text = Currency.formatted(servicesValues)
        sendRPSTree.find('.//ValorDeducoes', namespaces={}).text = deductionsValues
        sendRPSTree.find('.//ValorPIS', namespaces={}).text = pisValue
        sendRPSTree.find('.//ValorCOFINS', namespaces={}).text = cofinsValue
        sendRPSTree.find('.//ValorINSS', namespaces={}).text = inssValue
        sendRPSTree.find('.//CodigoServico', namespaces={}).text = serviceCode
        sendRPSTree.find('.//AliquotaServicos', namespaces={}).text = Currency.formatted(aliquot)
        sendRPSTree.find('.//CPFCNPJTomador/CNPJ', namespaces={}).text = takerTaxId
        sendRPSTree.find('.//RazaoSocialTomador', namespaces={}).text = companyName
        sendRPSTree.find('.//EnderecoTomador/Logradouro', namespaces={}).text = street.decode("utf-8")
        sendRPSTree.find('.//EnderecoTomador/NumeroEndereco', namespaces={}).text = streetNumber
        sendRPSTree.find('.//EnderecoTomador/ComplementoEndereco', namespaces={}).text = addressComplement.decode("utf-8")
        sendRPSTree.find('.//EnderecoTomador/Bairro', namespaces={}).text = district.decode("utf-8")
        sendRPSTree.find('.//EnderecoTomador/CEP', namespaces={}).text = zipCode
        sendRPSTree.find('.//EmailTomador', namespaces={}).text = email
        sendRPSTree.find('.//Discriminacao', namespaces={}).text = description.decode("utf-8") if description else None
        sendRPSTree.find('.//ISSRetido', namespaces={}).text = issRetain
        signedRPS = self.objSignCert.signRPSWithRSA(sendRPSTree)
        return self.postObj.sendRPS(signedXml=signedRPS)

    def bulkingRPS(self):
        signedEnvioLoteRPS = self.objSignCert.signLoteRPS(soapMessages.envioLoteRPS)
        return self.postObj.bulkRPS(signedXml=signedEnvioLoteRPS)

    def cancelNfe(self, taxId, providerSubscription, nfeNum):
        cancelTree = etree.fromstring(soapMessages.cancelamentoNota)
        cancelTree.find('.//CNPJ', namespaces={}).text = taxId
        cancelTree.find('.//InscricaoPrestador', namespaces={}).text = providerSubscription
        cancelTree.find('.//NumeroNFe', namespaces={}).text = str(nfeNum)
        signedCancelContent = self.objSignCert.signCancelWithCrypto(cancelTree)
        return self.postObj.cancelNfe(signedXml=signedCancelContent)

    def consultReceivedNfe(self, taxId, initDate, endDate, receiverTaxId, subscription):
        consultTree = etree.fromstring(soapMessages.consultaNfePeriodo)
        consultTree.find('.//CPFCNPJRemetente/CNPJ', namespaces={}).text = taxId
        consultTree.find('.//dtInicio', namespaces={}).text = initDate
        consultTree.find('.//dtFim', namespaces={}).text = endDate
        consultTree.find('.//CPFCNPJ/CNPJ', namespaces={}).text = receiverTaxId
        consultTree.find('.//Inscricao', namespaces={}).text = subscription
        signedReceivedTree = self.objSignCert.signWithA1Cert(consultTree)
        return self.postObj.consultReceivedNfe(signedXml=signedReceivedTree)

    def consultSentNfe(self, taxId, initDate, endDate, providerTaxId, subscription):
        consultTree = etree.fromstring(soapMessages.consultaNfePeriodo)
        consultTree.find('.//CPFCNPJRemetente/CNPJ', namespaces={}).text = taxId
        consultTree.find('.//dtInicio', namespaces={}).text = initDate
        consultTree.find('.//dtFim', namespaces={}).text = endDate
        consultTree.find('.//CPFCNPJ/CNPJ', namespaces={}).text = providerTaxId
        consultTree.find('.//Inscricao', namespaces={}).text = subscription
        signedSentTree = self.objSignCert.signWithA1Cert(consultTree)
        return self.postObj.consultSentNfe(signedXml=signedSentTree)
