# -*- coding: utf-8 -*-
from services.Services import Services

taxId = "87654321000198"
nfeNum = "280"


objServ = Services(
    certificateContent=open("../certfiles/converted.crt", "rb").read(),
    rsaKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
    privateKeyContent=open("../certfiles/privateKey.key", "rb").read()
)

nfse = objServ.consultNfe(taxId=taxId, nfe=nfeNum)
print(nfse)
