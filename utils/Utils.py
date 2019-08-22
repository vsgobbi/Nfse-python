# -*- coding: utf-8 -*-

import rsa
import hashlib
import base64
from signxml import XMLSigner, XMLVerifier, methods
from lxml import etree
try:
    from Crypto.Hash import SHA
    from Crypto.Signature import PKCS1_v1_5
    from Crypto.PublicKey import RSA
except ImportError:
    import sys
    sys.path.append('./lib/python2.7/site-packages/')
    # from Crypto.Hash import SHA  # requires PyCrypto from Crypto.Signature import PKCS1_v1_5
    # from Crypto.Cipher import PKCS1_OAEP, PKCS1_v1_5
    # from Crypto.PublicKey import RSA

from traceback import print_exc


NAMESPACE_SIG = "http://www.w3.org/2000/09/xmldsig#"


class Certificate(object):

    certFile = ""
    keyFile = ""

    def __init__(self, keyFile, certFile):
        self.certFile = certFile
        self.keyFile = keyFile


class CertData(Certificate):

    def extractCertContent(self):

        # Extract base64 data from cert.crt file:
        with open(self.certFile, "rb") as certData:
            certBuffer = certData.read()
        certBuffer = certBuffer.replace("\n", "")
        certData1 = certBuffer.split("-----BEGIN CERTIFICATE-----")
        certBuffer = str((certData1[1].replace("-----END CERTIFICATE-----", "")))
        return certBuffer

    def extractKeyContent(self):

        # Extract base64 data from PrivateKey file
        with open(self.keyFile, "rb") as keyData:
            keyBuffer = keyData.read()
        keyBuffer = keyBuffer.replace("\n", "")
        keyData1 = keyBuffer.split("-----BEGIN PRIVATE KEY-----")
        keyBuffer = str((keyData1[0].replace("-----END PRIVATE KEY-----", "")))
        return keyBuffer

    def signWithCert(self, bufferXml, key, returnString=True):

        reference = bufferXml.findall(".//*[@Id]")
        cert = self.extractCertContent()
        key = open(key, "rb").read()
        signer = XMLSigner(
            method=methods.enveloped, signature_algorithm="rsa-sha1",
            digest_algorithm='sha1',
            c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315')
        ns = {None: signer.namespaces['ds']}
        signer.namespaces = ns

        refUri = ('#%s' % reference) if reference else None
        signedRoot = signer.sign(bufferXml, key=key, cert=cert, reference_uri=refUri)
        ns = {'ns': NAMESPACE_SIG}
        # Insert the cert file buffered data (content) into specified tags X509Data/X509Certificate
        tagX509Data = signedRoot.find('.//ns:X509Data', namespaces=ns)
        etree.SubElement(tagX509Data, 'X509Certificate').text = cert

        if returnString:
            xmlEnvelope = etree.tostring(signedRoot, encoding="unicode",  pretty_print=False)
            return xmlEnvelope
        else:
            return signedRoot

    def verifyCert(self, signedRoot=signWithCert):

        cert = self.extractCertContent()
        try:
            ver = XMLVerifier().verify(signedRoot, x509_cert=cert)
            assert ver
            print "Successfully verified message"
        except:
            print "Signed XML verificiation failed"
            print_exc()

    def signRPSWithRSA(self, bufferXml, key):
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
        if "false" in signISSRetido:
            signISSRetido = "N"
        else:
            signISSRetido = "S"

        stringConcat = '%s%s%s%sT%s%s%015d%015d%s%s%s' % (
            str(signInscricaoPrestador).zfill(8),
            signSerieRPS.ljust(5),
            str(signNumeroRPS).zfill(12),
            str(signDataEmissao.replace("-", "")),
            str(signStatusRPS),
            str(signISSRetido),
            int(signValorServicos) * 100,
            int(signValorDeducoes) * 100,
            str(signCodigoServico).zfill(5),
            str(2),
            str(signCPFCNPJTomador).zfill(14))

        print("message:", stringConcat)

        digest = SHA.new(stringConcat)

        # Read shared key from file
        with open(key, "r") as RSAKeyFile:
            private_key = RSA.importKey(RSAKeyFile.read())

        # Load private key and sign message
        signer = PKCS1_v1_5.new(private_key)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        bufferXml.find(".//Assinatura", namespaces=ns).text = b64Signed
        return self.signWithCert(bufferXml, key=self.keyFile)

    def signCancelWithCrypto(self, bufferXml, key):  # Used to sign NFe cancel request
        ns = {}
        signInscricaoPrestador = bufferXml.find('.//InscricaoPrestador', namespaces=ns).text
        signNumeroNFe = bufferXml.find('.//NumeroNFe', namespaces=ns).text
        stringConcat = signInscricaoPrestador + signNumeroNFe.zfill(12)
        print("message: ", stringConcat)

        digest = SHA.new(stringConcat)

        # Read shared key from file
        with open(key, "r") as RSAKeyFile:
            private_key = RSA.importKey(RSAKeyFile.read())

        # Load private key and sign message
        signer = PKCS1_v1_5.new(private_key)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        # Load public key and verify message
        try:
            verifier = PKCS1_v1_5.new(private_key.publickey())
            verified = verifier.verify(digest, sign)
            assert verified
            print(verified, "Successfully verified message")
        except:
            return "RSA Verificiation failed"

        ns = {}
        tagCancelSignature9Data = bufferXml.find('.//Detalhe', namespaces=ns)
        etree.SubElement(tagCancelSignature9Data, 'AssinaturaCancelamento').text = b64Signed
        return self.signWithCert(bufferXml, key=self.keyFile)

    # Metodo para assinar campos de Lote RPS
    def signLoteRPS(self, stringXml, key):

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
        print("Valor total servicos:", bufferXml.find(".//ValorTotalServicos").text)
        signValorServicos = signValorServicos.rjust(15, "0")
        print("Valor servicos: ", signValorServicos)
        signValorDeducoes = signValorDeducoes.replace("R$", "")
        print("Valor total deducoes:", bufferXml.find(".//ValorTotalDeducoes").text)

        signValorDeducoes = signValorDeducoes.rjust(15, "0")
        print("Valor deducoes: ", signValorDeducoes)

        signCodigoServico + signCodigoServico.rjust(5, "0")
        print("Status RPS: ", signStatusRPS)

        if bufferXml.find(".//CPFCNPJIntermediario", namespaces=ns) != None:
            signCPFCNPJIntermediario = bufferXml.find(".//CPFCNPJIntermediario", namespaces=ns).text
            signInscricaoMunicipalIntermediario = bufferXml.find(".//InscricaoMunicipalIntermediario", namespaces=ns).text
            signISSRetidoIntermediario = bufferXml.find(".//ISSRetidoIntermediario", namespaces=ns).text
            if "false" in signISSRetidoIntermediario:
                signISSRetidoIntermediario = "N"
            else:
                signISSRetidoIntermediario = "S"
                signCPFCNPJIntermediario = "2" + signCPFCNPJIntermediario

        stringConcat = str(signInscricaoPrestador + signSerieRPS + " " + signNumeroRPS + signDataEmissao
                           + signTributacaoRPS + signStatusRPS + signValorServicos + signValorDeducoes + "0"
                           + signCodigoServico + signISSRetido + signCPFCNPJTomador + signCPFCNPJIntermediario
                           + signInscricaoMunicipalIntermediario + signISSRetidoIntermediario)


        print "Error, concatenation of string must be greater than 85 chars" if len(stringConcat) <= 85 else len(stringConcat)
        print("message", stringConcat)

        message = str(stringConcat).encode("ascii")
        digest = SHA.new(message)

        # Read shared key from file
        with open(key, "r") as RSAKeyFile:
            private_key = RSA.importKey(RSAKeyFile.read())

        # Load private key and sign message
        signer = PKCS1_v1_5.new(private_key)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        # Load public key and verify message
        try:
            verifier = PKCS1_v1_5.new(private_key.publickey())
            verified = verifier.verify(digest, sign)
            assert verified
            print(verified, "Successfully verified RPS message")
        except:
            print("Verificiation failed")
        ns = {}
        bufferXml = etree.fromstring(stringXml)
        bufferXml.find(".//Assinatura", namespaces=ns).text = b64Signed

        print("stringGerada", stringConcat)
        xmlEnvelope = etree.tostring(bufferXml, encoding="unicode",  pretty_print=False)
        return self.signWithCert(xmlEnvelope, key=self.keyFile)

    def signMessageWithCrypto(self, message, stringXml):  # Utilizada para assinar e validar mensagem de envioRPS

        message = [elem.encode("hex") for elem in message]
        print("Message 08b: ", message)
        encoded = hashlib.sha1(bytes(message)).digest()
        digest = SHA.new(encoded)

        # Read shared key from file
        with open("certfiles/privRSAkey.pem", "r") as myfile:
            private_key = RSA.importKey(myfile.read())

        # Load private key and sign message
        signer = PKCS1_v1_5.new(private_key)
        sign = signer.sign(digest)
        b64Signed = base64.b64encode(sign)

        # Load public key and verify message
        try:
            verifier = PKCS1_v1_5.new(private_key.publickey())
            verified = verifier.verify(digest, sign)
            assert verified
            print(verified, "Successfully verified message")
            print(b64Signed)
        except:
            print("Verificiation failed")

        # Sign xml message
        try:
            bufferXml = etree.fromstring(stringXml)
            bufferXml.find(".//Assinatura", namespaces={}).text = b64Signed
            xmlEnvelope = etree.tostring(bufferXml, encoding="unicode", pretty_print=False)
            xmlEnvelope = self.signWithCert(xmlEnvelope, key=self.keyFile)
            return xmlEnvelope
        except etree.clear_error_log() as err:
            print("Can't sign xml", err.args)

    def signRPS(self, stringXml, key):

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
        if bufferXml.find('.//CPFCNPJTomador/CNPJ', namespaces=ns) != None:
            signCPFCNPJTomador = bufferXml.find('.//CPFCNPJTomador/CNPJ', namespaces=ns).text
        elif bufferXml.find('.//CPFCNPJTomador/CPF', namespaces=ns) != None:
            signCPFCNPJTomador = bufferXml.find('.//CPFCNPJTomador/CPF', namespaces=ns).text
        else:
            signCPFCNPJTomador = None

        if "false" in signISSRetido:
             signISSRetido = "N"
        else:
             signISSRetido = "S"

        stringConcat = '%s%s%s%sT%s%s%015d%015d%s%s%s' % (
            str(signInscricaoPrestador).zfill(8),
            signSerieRPS.ljust(5),
            str(signNumeroRPS).zfill(12),
            str(signDataEmissao.replace("-", "")),
            str(signStatusRPS),
            str(signISSRetido),
            round(int(signValorServicos) * 100),
            round(int(signValorDeducoes) * 100),
            str(signCodigoServico).zfill(5),
            str(2),
            str(signCPFCNPJTomador).zfill(14))
        print("message:", stringConcat)


        signSerieRPS = signSerieRPS.ljust(5)
        signNumeroRPS = signNumeroRPS.rjust(12, "0")
        signDataEmissao = signDataEmissao.replace("-", "")
        signValorServicos = signValorServicos.replace("R$", "")
        signValorServicos = signValorServicos.rjust(15, "0")
        signValorDeducoes = signValorDeducoes.replace("R$", "")
        signValorDeducoes = signValorDeducoes.rjust(15, "0")
        signCodigoServico + signCodigoServico.rjust(5, "0")

        stringConcat = str(signInscricaoPrestador + signSerieRPS + signNumeroRPS + signDataEmissao
                           + signStatusRPS + signTributacaoRPS + signValorServicos + signValorDeducoes
                           + signCodigoServico + "2" + signCPFCNPJTomador)

        print("message: ", stringConcat)

        print("Error, concatenation of string must be "
              "greater than 85 chars" if len(stringConcat) < 85 else "Len: ", (len(stringConcat)))

        message = str(stringConcat).encode("hex")
        digest = SHA.new(message)

        # Read shared key from file
        with open(key, "r") as RSAKeyFile:
            private_key_string = RSA.importKey(RSAKeyFile.read())

        with open("../certfiles/privkey.pem", "rb") as pemKey:
            pemKey = pemKey.read()


        RSAKey = RSA.importKey(pemKey)
        signer = PKCS1_v1_5.new(RSAKey)
        signature = signer.sign(digest)
        b64Signed = base64.b64encode(signature)
        print(b64Signed)

        with open('../certfiles/privkey.pem', mode='rb') as privatefile:
            keyData = privatefile.read()
        privKey = rsa.PrivateKey.load_pkcs1(keyData)

        signature2 = base64.b64encode(rsa.sign(digest, privKey, hash_method="SHA-1"))
        print(signature2)

        bufferXml = etree.fromstring(stringXml)
        bufferXml.find(".//Assinatura", namespaces=ns).text = signature2

        xmlEnvelope = etree.tostring(bufferXml, encoding="unicode",  pretty_print=False)
        xmlEnvelope = self.signWithCert(xmlEnvelope, key=self.keyFile)
        return xmlEnvelope
