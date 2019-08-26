# -*- coding: utf-8 -*-
from services.Services import Services


taxId = "20018183000180"
providerTaxId = "20018183000180"
citySubscription = "57038597"
initDate = "2019-06-01"
endDate = "2019-07-01"

objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

sentNfse = objServ.consultSentNfe(cnpj=taxId, subscription=citySubscription,
                                  initDate=initDate, endDate=endDate,
                                  cnpjPrestador=providerTaxId)

receivedNfse = objServ.consultReceivedNfe(cnpj=taxId, subscription=citySubscription,
                                          initDate=initDate, endDate=endDate,
                                          receiverTaxId=providerTaxId)

print(sentNfse)

print(receivedNfse)
