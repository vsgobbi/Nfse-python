# -*- coding: utf-8 -*-
from services.Services import Services


taxId = "20018183000180"
providerTaxId = "20018183000180"
citySubscription = "57038597"
initDate = "2019-06-01"
endDate = "2019-06-05"

takerTaxId = "06990590000123"  # CNPJ Tomador


objServ = Services(certificateContent=open("../certfiles/converted.crt", "rb").read(),
                   RSAPrivateKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
                   privateKeyContent=open("../certfiles/privateKey.key", "rb").read())

sentNfse = objServ.consultSentNfe(taxId=taxId, subscription=citySubscription,
                                  initDate=initDate, endDate=endDate,
                                  providerTaxId=providerTaxId)

print(sentNfse)


# receivedNfse = objServ.consultReceivedNfe(cnpj=taxId, subscription=citySubscription,
#                                           initDate=initDate, endDate=endDate,
#                                           receiverTaxId=providerTaxId)
# print(receivedNfse)
