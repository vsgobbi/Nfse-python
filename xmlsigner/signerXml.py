# -*- coding: utf-8 -*-
from xmlsigner.certMethods import Certificate


class SignCert:

    def __init__(self, privateKeyContent, certificateContent, RSAPrivateKeyContent):
        self.privateKeyContent = privateKeyContent
        self.certificateContent = certificateContent
        self.RSAPrivateKeyContent = RSAPrivateKeyContent

    def loadPem(self, privateKeyContent):
        return Certificate.valdidatePrivateKey(privateKeyContent)

    def loadCert(self):
        return Certificate.extractCertContent(self.certificateContent)

    def signWithA1Cert(self, bufferXml):
        return Certificate.signWithA1Cert(xml=bufferXml,
                                          certContent=self.certificateContent,
                                          RSAPrivateKeyContent=self.RSAPrivateKeyContent)

    def verifySignature(self, signedRoot):
        return Certificate.verifyCert(RSAPrivateKeyContent=self.RSAPrivateKeyContent, signedRoot=signedRoot)

    def signRPSWithRSA(self, bufferXml):
        return Certificate.signRPSWithRSA(bufferXml=bufferXml,
                                          certContent=self.certificateContent,
                                          RSAPrivateKeyContent=self.RSAPrivateKeyContent)

    def signCancelWithCrypto(self, bufferXml):
        return Certificate.signCancelWithRSA(bufferXml,
                                             certContent=self.certificateContent,
                                             RSAPrivateKeyContent=self.RSAPrivateKeyContent)

    def signLoteRPS(self, stringXml):
        return Certificate.signLoteRPS(stringXml=stringXml,
                                       certContent=self.certificateContent,
                                       RSAPrivateKeyContent=self.RSAPrivateKeyContent,)
