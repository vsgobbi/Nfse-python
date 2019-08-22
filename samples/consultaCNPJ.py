# -*- coding: utf-8 -*-
from services.Services import Services


cnpj = "43211234567890"
cnpjContribuinte = "43211234567890"

objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

# Check "Inscricao Muncipal" of target company
print(objServ.consultaCNPJ(cnpj=cnpj, cnpjContribuinte=cnpjContribuinte))
