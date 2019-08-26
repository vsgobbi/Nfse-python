# -*- coding: utf-8 -*-
from services.Services import Services

taxId = "20018183000180"
municipalSubscription = "57038597"
nfeNum = "167"


objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")
print(objServ.cancelNfe(taxId=taxId, providerSubscription=municipalSubscription, nfeNum=nfeNum))
