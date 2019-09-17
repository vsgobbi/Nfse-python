import hashlib
import re
from lxml import etree
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Integer import b64e, b64d

RX_ROOT = re.compile("<[^> ]+ ?([^>]*)>")
RX_NS = re.compile("xmlns:[^> ]+")
RX_SIGNATURE = re.compile("<Signature.*?</Signature>")
RX_SIGNED_INFO = re.compile("<SignedInfo.*?</SignedInfo>")
RX_SIG_VALUE = re.compile("<SignatureValue[^>]*>([^>]+)</SignatureValue>")

# Pattern Map:
#   xmlnsAttr: xml name space definition attributes including ' ' prefix
#   digestValue: padded hash of message in base64
PTN_SIGNED_INFO_XML = \
    """<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"%(xmlnsAttr)s><CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></SignatureMethod><Reference URI=""><Transforms><Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></Transform><Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod><DigestValue>%(digestValue)s</DigestValue></Reference></SignedInfo>"""

# Pattern Map:
#   signedInfoXml: str <SignedInfo> bytestring xml
#   signatureValue: str computed signature from <SignedInfo> in base64
#   keyInfoXml: str <KeyInfo> bytestring xml of signing key information
#   signatureId: str in form `Id="VALUE" ` (trailing space required) or ""
PTN_SIGNATURE_XML = \
    """<Signature %(signatureId)sxmlns="http://www.w3.org/2000/09/xmldsig#">%(signedInfoXml)s<SignatureValue>%(signatureValue)s</SignatureValue>%(keyInfoXml)s</Signature>"""

# Pattern Map:
#   modulus: str signing RSA key modulus in base64
#   exponent: str signing RSA key exponent in base64
PTN_KEY_INFO_RSA_KEY = \
    """<KeyInfo><KeyValue><RSAKeyValue><Modulus>%(modulus)s</Modulus><Exponent>%(exponent)s</Exponent></RSAKeyValue></KeyValue></KeyInfo>"""

# Pattern Map:
#   subject_name: str of <SubjectName> value
PTN_X509_SUBJECT_NAME = \
    """<X509SubjectName>%(subjectName)s</X509SubjectName>"""

KEY_INFO_XML = """<KeyInfo><X509Data/></KeyInfo>"""


def sign(xml, certContent, RSAKeyContent, signIdValue=None):
    """Return xmldsig XML string from xml_string of XML.
    Args:
      xml: str of bytestring xml to sign
      certContent: str content of certificate file
      RSAKeyContent: RSA key private content
      signIdValue: str of signature id value
    Returns:
      str: signed bytestring xml
    """
    keyInfoXml = KEY_INFO_XML

    signedInfoXml = _signedInfo(xml)
    signatureValue = signedWithRSA(signedInfoXml, RSAKeyContent)

    if signIdValue is None:
        signatureId = ""
    else:
        signatureId = "Id='%s' " % signIdValue

    signatureXml = PTN_SIGNATURE_XML % {
        "signedInfoXml": signedInfoXml,
        "signatureValue": b64e(signatureValue),
        "keyInfoXml": keyInfoXml,
        "signatureId": signatureId,
    }

    prefix = "</p1:"
    foo = xml.split(prefix)
    after = prefix+foo[1]
    signedXml = foo[0] + signatureXml + after

    ns = {"ns": "http://www.w3.org/2000/09/xmldsig#"}

    signedXml = etree.fromstring(signedXml)
    # Insert the cert file buffered data (content) into tags X509Data/X509Certificate
    tagX509Data = signedXml.find(".//ns:X509Data", namespaces=ns)

    etree.SubElement(tagX509Data, "X509Certificate").text = certContent
    xmlEnvelope = etree.tostring(signedXml)

    return xmlEnvelope


def verify(xml, RSAKeyContent):
    """Return if <Signature> is valid for "xml"

    Args:
      xml: str of XML with xmldsig <Signature> element
      RSAKeyContent: RSA key private content
    Returns:
      bool: signature for "xml" is valid
    """
    signatureXml = RX_SIGNATURE.search(xml).group(0)
    unsignedXml = xml.replace(signatureXml, "")
    # compute the given signed value
    signatureValue = RX_SIG_VALUE.search(signatureXml).group(1)
    expected = b64d(signatureValue)
    # compute the actual signed value
    signedInfoXml = _signedInfo(unsignedXml)
    actual = signedWithRSA(signedInfoXml, RSAKeyContent=RSAKeyContent)
    isVerified = (expected == actual)

    return isVerified


def _digest(data):
    """SHA1 hash digest of message data.

    Implements RFC2437, 9.2.1 EMSA-PKCS1-v1_5, Step 1. for "Hash = SHA1"

    Args:
      data: str of bytes to digest
    Returns:
      str: of bytes of digest from "data"
    """
    hasher = hashlib.sha1()
    hasher.update(data)

    return hasher.digest()


def getXmlnsPrefixes(xml):
    """Return string of root namespace prefix attributes in given order.

    Args:
      xml: str of bytestring xml
    Returns:
      str: [xmlns:prefix="uri"] list ordered as in "xml"
    """
    rxRoot = re.compile("<[^> ]+ ?([^>]*)>")
    if rxRoot.match(xml):
        rootAttr = rxRoot.match(xml).group(1)
        nsAttrs = [a for a in rootAttr.split(" ") if RX_NS.match(a)]
        return " ".join(nsAttrs)
    return None


def _signedInfo(xml):
    """Return <SignedInfo> for bytestring xml.
    Args:
      xml: str of bytestring
    Returns:
      str: xml bytestring of <SignedInfo> computed from "xml"
    """
    xmlnsAttr = getXmlnsPrefixes(xml)
    if xmlnsAttr:
        xmlnsAttr = " %s" % xmlnsAttr

    signedInfoXml = PTN_SIGNED_INFO_XML % {
        "digestValue": b64e(_digest(xml)),
        "xmlnsAttr": xmlnsAttr
    }

    return signedInfoXml


def signedWithRSA(data, RSAKeyContent):
    """SHA1 hash digest of message data.

    Args:
      data: str of bytestring
      RSAKeyContent: str extracted content of RSA Private Key
    Returns:
      str: xml bytestring of <SignedInfo> computed from "xml"
    """

    digest = SHA.new(data)
    privateKey = RSA.importKey(RSAKeyContent)
    signer = PKCS1_v1_5.new(privateKey)
    signed = signer.sign(digest)

    return signed
