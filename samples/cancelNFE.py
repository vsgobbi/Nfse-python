# -*- coding: utf-8 -*-
from services.Services import Services

taxId = "20018183000180"
municipalSubscription = "57038597"
nfeNum = [250, 251, 252, 253, 254, 255, 256, 257, 258]


objServ = Services(certificateContent=open("../certfiles/converted.crt", "rb").read(),
                   RSAPrivateKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
                   privateKeyContent=open("../certfiles/privateKey.key", "rb").read())

for num in nfeNum:
    print(objServ.cancelNfe(taxId=taxId, providerSubscription=municipalSubscription, nfeNum=num))
