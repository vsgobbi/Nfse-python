# -*- coding: utf-8 -*-
from services.Services import Services


cnpj = "43211234567890"
cnpjPrestador = "43211234567890"
inscricaoMunicipal = "098765432"
numeroNfe = "153"
dtInicio = "2019-06-01"
dtFim = "2019-07-01"

objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

nfseEmitidas = objServ.consultaNFeEmitidas(cnpj=cnpj, inscricao=inscricaoMunicipal,
                                           dtInicio=dtInicio, dtFim=dtFim,
                                           cnpjPrestador=cnpjPrestador)

nfseRecebidas = objServ.consultaNFeRecebidas(cnpj=cnpj, inscricao=inscricaoMunicipal,
                                             dtInicio=dtInicio, dtFim=dtFim,
                                             cnpjTomador=cnpjPrestador)
