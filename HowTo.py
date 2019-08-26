from utils.SignerXML import SignCert
from services.Services import Services
from lxml import etree


# Works with .crt and .pem files
certificateFile = "./certfiles/converted.crt"
privateKeyRSA = "./certfiles/privRSAkey.pem"
privateKeyFile = "./certfiles/privateKey.key"

objSignCert = SignCert(privateKeyFile=privateKeyFile,
                       certificateFile=certificateFile,
                       privateKeyRSA=privateKeyRSA)

objSignCert.loadPem()
certContent = objSignCert.loadCert()
print(certContent)
keyContent = objSignCert.loadKey()
print(keyContent)

xmlEnvelope = "file.xml"
with open(xmlEnvelope, 'rb') as xmlEnvelope:
    xmlData = xmlEnvelope.read()

# Simply sign with extended A1 certificate
xmlEnvelope = etree.fromstring(xmlData)
signedRoot = objSignCert.signA1Cert(xmlEnvelope)
print "Signed root:"
print signedRoot


objSignCert.verifySignature(signedRoot)


# Sign and post a xml example:
objRequestPost = Services(certificateFile=certificateFile, privateKeyRSA=privateKeyRSA, privateKeyFile=privateKeyFile)
taxId = "00623904000173"
taxPayerId = "00623904000173"
result = objRequestPost.consultTaxIdInscription(taxId=taxId, taxPayerId=taxPayerId)
print(result)
