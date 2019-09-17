# -*- coding: utf-8 -*-
from services.Services import Services

taxId = "20018183000180"
nfeNum = "171"


objServ = Services(certificateContent=open("../certfiles/converted.crt", "rb").read(),
                   RSAPrivateKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
                   privateKeyContent=open("../certfiles/privateKey.key", "rb").read())

nfse = objServ.consultNfe(taxId=taxId, nfe=nfeNum)
print(nfse)
