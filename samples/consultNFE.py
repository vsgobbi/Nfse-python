# -*- coding: utf-8 -*-
from services.Services import Services

taxId = "20018183000180"
nfeNum = "160"


objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

Services.certificateFile = "../certfiles/converted.crt"
Services.privateKeyRSA = "../certfiles/privRSAkey.pem"
Services.privateKeyFile = "../certfiles/privateKey.key"
nfse = objServ.consultNfe(taxId=taxId, nfe=nfeNum)
print(nfse)
