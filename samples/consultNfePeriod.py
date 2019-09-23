# -*- coding: utf-8 -*-
from services.Services import Services


taxId = "12345678000198"
providerTaxId = "87654321000198"
citySubscription = "12345678"
initDate = "2019-09-15"
endDate = "2019-09-18"


objServ = Services(
    certificateContent=open("../certfiles/converted.crt", "rb").read(),
    rsaKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
    privateKeyContent=open("../certfiles/privateKey.key", "rb").read()
)

sentNfse = objServ.consultSentNfe(
    taxId=taxId,
    subscription=citySubscription,
    initDate=initDate,
    endDate=endDate,
    providerTaxId=providerTaxId
)

print(sentNfse)

receivedNfse = objServ.consultReceivedNfe(
    taxId=taxId,
    subscription=citySubscription,
    initDate=initDate,
    endDate=endDate,
    receiverTaxId=providerTaxId
)

print(receivedNfse)
