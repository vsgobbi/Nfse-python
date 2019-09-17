# -*- coding: utf-8 -*-
import logging
import base64
from lxml import etree
from xmlsigner import xmlDigSign as signer

try:
    from Crypto.Hash import SHA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.PublicKey import RSA
except ImportError:
    import sys
    sys.path.append('./libs/')
    from Crypto.Hash import SHA  # requires PyCrypto from Crypto.Signature import PKCS1_v1_5
    from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
    from Crypto.PublicKey import RSA


class Certificate(object):

    @classmethod
    def valdidatePrivateKey(cls, privateKeyContent):
        try:
            if "-----BEGIN PRIVATE KEY-----" in privateKeyContent:
                if "-----END PRIVATE KEY-----" in privateKeyContent:
                    key = RSA.importKey(privateKeyContent)
                    return key.keydata
        except Exception as e:
            return "Invalide Private Key{:s}".format(e)

    @classmethod
    def extractCertContent(cls, certContent):
        certBuffer = certContent.replace("\n", "")
        certData1 = certBuffer.split("-----BEGIN CERTIFICATE-----")
        certBuffer = str((certData1[1].replace("-----END CERTIFICATE-----", "")))
        return certBuffer

    @classmethod
    def signWithA1Cert(cls, xml, certContent, RSAPrivateKeyContent, returnString=True):

        certContent = cls.extractCertContent(certContent)

        xml = etree.tostring(xml, encoding="utf-8")
        signedXml = signer.sign(xml=xml, certContent=certContent, RSAKeyContent=RSAPrivateKeyContent)

        isVerified = signer.verify(xml=signedXml, RSAKeyContent=RSAPrivateKeyContent)
        assert isVerified

        if returnString:
            return signedXml
        else:
            signedXml = etree.fromstring(signedXml)
            return signedXml

    @classmethod
    def verifyCert(cls, RSAPrivateKeyContent, signedRoot=signWithA1Cert):
        try:
            ver = signer.verify(signedRoot, RSAKeyContent=RSAPrivateKeyContent)
            assert ver
            logging.debug("Successfully verified certificate")
        except Exception as e:
            logging.debug("Signed XML verificiation failed {:s}".format(e))

    @classmethod
    def verifySignature(cls, RSAPrivateKeyContent, digest, sign):
        # Load public key and verify message
        try:
            verifier = PKCS1_v1_5.new(RSAPrivateKeyContent.publickey())
            verified = verifier.verify(digest, sign)
            assert verified
            logging.debug(verified, "Successfully verified message")
            return verified
        except Exception as e:
            return "RSA Verificiation failed, {:s}".format(e)

    @classmethod
    def signRPSWithRSA(cls, bufferXml, RSAPrivateKeyContent, certContent):
        ns = {}
        signInscricaoPrestador = bufferXml.find('.//InscricaoPrestador', namespaces=ns).text
        signSerieRPS = bufferXml.find('.//SerieRPS', namespaces=ns).text
        signNumeroRPS = bufferXml.find('.//NumeroRPS', namespaces=ns).text
        signDataEmissao = bufferXml.find('.//DataEmissao', namespaces=ns).text
        signStatusRPS = bufferXml.find('.//StatusRPS', namespaces=ns).text
        signTributacaoRPS = bufferXml.find('.//TributacaoRPS', namespaces=ns).text
        signValorServicos = bufferXml.find('.//ValorServicos', namespaces=ns).text
        signValorDeducoes = bufferXml.find('.//ValorDeducoes', namespaces=ns).text
        signCodigoServico = bufferXml.find('.//CodigoServico', namespaces=ns).text
        signISSRetido = bufferXml.find('.//ISSRetido', namespaces=ns).text
        signCPFCNPJTomador = bufferXml.find('.//CPFCNPJTomador/CNPJ', namespaces=ns).text

        if signISSRetido == "false":
            signISSRetido = "N"
        else:
            signISSRetido = "S"
        print("status rps", signStatusRPS)
        stringConcat = '%s%s%s%sT%s%s%015d%015d%05d%s%s' % (
            str(signInscricaoPrestador).zfill(8),
            str(signSerieRPS.ljust(5)).upper(),
            str(signNumeroRPS).zfill(12),
            str(signDataEmissao.replace("-", "")),
            str(signStatusRPS),
            str(signISSRetido),
            int(float(signValorServicos) * 100),
            int(float(signValorDeducoes) * 100),
            int(signCodigoServico),
            str(2),
            str(signCPFCNPJTomador).zfill(14))

        logging.debug("message:", stringConcat)

        # Load private key and sign message
        digest = SHA.new(stringConcat)
        privateKey = RSA.importKey(RSAPrivateKeyContent)
        signer = PKCS1_v1_5.new(privateKey)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        cls.verifySignature(RSAPrivateKeyContent, digest, sign)

        bufferXml.find(".//Assinatura", namespaces=ns).text = b64Signed
        print(etree.tostring(bufferXml))
        return cls.signWithA1Cert(bufferXml, certContent=certContent, RSAPrivateKeyContent=RSAPrivateKeyContent)

    @classmethod
    def signCancelWithRSA(cls, bufferXml, RSAPrivateKeyContent, certContent):
        ns = {}

        signInscricaoPrestador = bufferXml.find('.//InscricaoPrestador', namespaces=ns).text
        signNumeroNFe = bufferXml.find('.//NumeroNFe', namespaces=ns).text
        stringConcat = signInscricaoPrestador + signNumeroNFe.zfill(12)

        digest = SHA.new(stringConcat)

        RSAKey = RSA.importKey(RSAPrivateKeyContent)
        signer = PKCS1_v1_5.new(RSAKey)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        cls.verifySignature(RSAPrivateKeyContent, digest, sign)

        tagCancelSignature9Data = bufferXml.find('.//Detalhe', namespaces=ns)
        etree.SubElement(tagCancelSignature9Data, 'AssinaturaCancelamento').text = b64Signed
        return cls.signWithA1Cert(bufferXml, certContent=certContent, RSAPrivateKeyContent=RSAPrivateKeyContent)

    @classmethod
    def signLoteRPS(cls, stringXml, certContent, RSAPrivateKeyContent):  # Used to sign Lote(Bulking) RPS

        ns = {}
        bufferXml = etree.fromstring(stringXml)
        signInscricaoPrestador = bufferXml.find('.//InscricaoPrestador', namespaces=ns).text
        signSerieRPS = bufferXml.find('.//SerieRPS', namespaces=ns).text

        signNumeroRPS = bufferXml.find('.//NumeroRPS', namespaces=ns).text
        signDataEmissao = bufferXml.find('.//DataEmissao', namespaces=ns).text
        signStatusRPS = bufferXml.find('.//StatusRPS', namespaces=ns).text
        signTributacaoRPS = bufferXml.find('.//TributacaoRPS', namespaces=ns).text
        signValorServicos = bufferXml.find('.//ValorServicos', namespaces=ns).text
        signValorDeducoes = bufferXml.find('.//ValorDeducoes', namespaces=ns).text
        signCodigoServico = bufferXml.find('.//CodigoServico', namespaces=ns).text
        signISSRetido = bufferXml.find('.//ISSRetido', namespaces=ns).text
        signCPFCNPJTomador = bufferXml.find('.//CPFCNPJTomador/CNPJ', namespaces=ns).text

        if "false" in signISSRetido:
            signISSRetido = "N"
        else:
            signISSRetido = "S"
        signNumeroRPS = signNumeroRPS.rjust(12, "0")
        signDataEmissao = signDataEmissao.replace("-", "")
        signValorServicos = signValorServicos.replace("R$", "")
        signValorServicos = signValorServicos.rjust(15, "0")
        signValorDeducoes = signValorDeducoes.replace("R$", "")
        signValorDeducoes = signValorDeducoes.rjust(15, "0")
        signCodigoServico + signCodigoServico.rjust(5, "0")

        signCPFCNPJIntermediario = bufferXml.find(".//CPFCNPJIntermediario", namespaces=ns).text

        if signCPFCNPJIntermediario != None:
            signISSRetidoIntermediario = bufferXml.find(".//ISSRetidoIntermediario", namespaces=ns).text
            signInscricaoMunicipalIntermediario = bufferXml.find(".//InscricaoMunicipalIntermediario",
                                                                 namespaces=ns).text
            if "false" in signISSRetidoIntermediario:
                stringConcat = str(signInscricaoPrestador + signSerieRPS + " " + signNumeroRPS + signDataEmissao
                                   + signTributacaoRPS + signStatusRPS + signValorServicos + signValorDeducoes + "0"
                                   + signCodigoServico + signISSRetido + signCPFCNPJTomador)
            else:
                signISSRetidoIntermediario = "S"
                signCPFCNPJIntermediario = "2" + signCPFCNPJIntermediario
                stringConcat = str(signInscricaoPrestador + signSerieRPS + " " + signNumeroRPS + signDataEmissao
                                   + signTributacaoRPS + signStatusRPS + signValorServicos + signValorDeducoes + "0"
                                   + signCodigoServico + signISSRetido + signCPFCNPJTomador + signCPFCNPJIntermediario
                                   + signInscricaoMunicipalIntermediario + signISSRetidoIntermediario)

        logging.debug("Error, concatenation of string must "
                      "be greater than 85 chars" if len(stringConcat) <= 85 else len(stringConcat))

        message = str(stringConcat).encode("ascii")

        digest = SHA.new(message)

        # Load private key and sign message
        RSAKey = RSA.importKey(RSAPrivateKeyContent)
        signer = PKCS1_v1_5.new(RSAKey)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        cls.verifySignature(RSAPrivateKeyContent, digest, sign)

        ns = {}
        bufferXml = etree.fromstring(stringXml)
        bufferXml.find(".//Assinatura", namespaces=ns).text = b64Signed

        print("stringGerada", stringConcat)
        xmlEnvelope = etree.tostring(bufferXml, encoding="unicode", pretty_print=True)
        logging.debug(xmlEnvelope)
        return cls.signWithA1Cert(bufferXml, certContent=certContent, RSAPrivateKeyContent=RSAPrivateKeyContent)
