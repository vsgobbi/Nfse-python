# -*- coding: utf-8 -*-
from services.Services import Services

cnpj = "43211234567890"
numeroNfe = "160"


objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

nfse = objServ.consultaNFE(cnpj=cnpj, nfe=numeroNfe)
print(nfse)
