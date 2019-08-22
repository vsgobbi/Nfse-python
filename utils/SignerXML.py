# -*- coding: utf-8 -*-
import subprocess
from utils.Utils import Certificate, CertData
from PostXML import PostXML

NAMESPACE_SIG = 'http://www.w3.org/2000/09/xmldsig#'

# Working with .crt and .pem files:
# certificateFile = "../certfiles/converted.crt"
# privatekeyRSA = "../certfiles/privRSAkey.pem"
# privatekeyFile = "../certfiles/privateKey.key"

# postObj = PostXML(cert=certificateFile, key=privatekeyRSA, uf="PREFEITURA")


class SignCert:

    def __init__(self, privateKeyFile, certificateFile, privateKeyRSA=None):
        self.privatekeyFile = privateKeyFile
        self.certificateFile = certificateFile
        self.privateKeyRSA = privateKeyRSA
        self.cert = Certificate(certFile=certificateFile, keyFile=privateKeyFile)
        self.certData = CertData(certFile=certificateFile, keyFile=privateKeyFile)

    # Generate a self signed key and cert file if they doesnt't exists:
    def generateCert(self):
        print subprocess.Popen("ls -lash", shell=True, stdout=subprocess.PIPE).stdout.read()
        listPem = subprocess.Popen("ls -lash *pem", shell=True, stdout=subprocess.PIPE).stdout.read()
        generatePem = "openssl req -new -newkey rsa:4096 -nodes -keyout snakeoil.key -out snakeoil.csr"
        generateSelfSigned = "openssl x509 -req -sha256 -days 365 -in snakeoil.csr -signkey snakeoil.key -out snakeoil.pem"
        if "snakeoil.pem" in listPem:
            print("PEM file already found")
            return listPem
        subprocess.Popen(generatePem, shell=True, stdout=subprocess.PIPE).stdout.read()
        subprocess.Popen(generateSelfSigned, shell=True, stdout=subprocess.PIPE).stdout.read()

    # Load certificate content from .pem or certificate files
    def loadPem(self):
        f = open(self.privatekeyFile, "rb")
        pem_data = f.read()
        f.close()
        return pem_data

    def loadCert(self):
        return self.certData.extractCertContent()

    def loadKey(self):
        return self.certData.extractKeyContent()

    def signA1Cert(self, bufferXml):
        return self.certData.signWithCert(bufferXml=bufferXml, key=self.privatekeyFile)

    def verifySignature(self, signedRoot):
        return self.certData.verifyCert(signedRoot)

    def signRPSWithRSA(self, bufferXml):
        return self.certData.signRPSWithRSA(bufferXml, self.privateKeyRSA)

    def signCancelWithCrypto(self, bufferXml):
        print(self.privateKeyRSA)
        return self.certData.signCancelWithCrypto(bufferXml, key=self.privateKeyRSA)

    def signRPS(self, stringXml):
        return self.certData.signRPS(stringXml, self.privateKeyRSA)

    def signLoteRPS(self, stringXml):
        return self.certData.signLoteRPS(stringXml, self.privateKeyRSA)

    def signMessageWithCrypto(self, message, stringXml):
        return self.certData.signMessageWithCrypto(message, stringXml)
