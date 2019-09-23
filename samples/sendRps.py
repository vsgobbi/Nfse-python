# -*- coding: utf-8 -*-
from services.Services import Services


# NFSe Provider
taxId = "87654321000198"
providerSubscription = "12345678"  # Provider city subscription

# NFSe Taker
companyName = "SOME COMPANY LTDA"
takerTaxId = "12345678000198"

objServ = Services(
    certificateContent=open("../certfiles/converted.crt", "rb").read(),
    rsaKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
    privateKeyContent=open("../certfiles/privateKey.key", "rb").read()
)

print(objServ.sendRPS(
    taxId=taxId,
    providerSubscription=providerSubscription,
    rpsSeries="TESTE",
    rpsNumber="5117092019",
    rpsType="RPS",
    issueDate="2019-07-01",
    rpsStatus="N",
    rpsTax="T",
    issRetain="false",
    servicesAmount="1",
    deductionsAmount="0",
    pisAmount="0",
    irAmount="0",
    csllAmount="0",
    cofinsAmount="0",
    inssAmount="0",
    serviceCode="05895",
    aliquot="2",
    takerTaxId=takerTaxId,
    companyName=companyName,
    streetLine="Null",
    streetNumber="0",
    streetLine2="Null",
    district="Null",
    zipCode="00000000",
    email="none@none",
    description="Teste de emissão automática de NFS-e de boletos e transferências prestados",
))
