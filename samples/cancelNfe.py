# -*- coding: utf-8 -*-
from services.Services import Services

taxId = "87654321000198"
municipalSubscription = "12345678"
nfeNum = range(271, 275)

objServ = Services(certificateContent=open("../certfiles/converted.crt", "rb").read(),
                   rsaKeyContent=open("../certfiles/RSAPrivateKey.pem", "rb").read(),
                   privateKeyContent=open("../certfiles/privateKey.key", "rb").read())

for num in nfeNum:
    print(objServ.cancelNfe(taxId=taxId, providerSubscription=municipalSubscription, nfeNum=num))
