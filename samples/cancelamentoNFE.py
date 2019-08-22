# -*- coding: utf-8 -*-
from services.Services import Services

cnpj = "43211234567890"
inscricaoMunicipal = "098765432"
numeroNfe = "157"


objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")
print(objServ.cancelaNFe(cnpj=cnpj, inscricao=inscricaoMunicipal, nfe=numeroNfe))
