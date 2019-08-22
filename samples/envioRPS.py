# -*- coding: utf-8 -*-
from services.Services import Services


cnpj = "43211234567890"
razaoSocialTomador = "SOME COMPANY LTDA"
cnpjTomador = "49293189101110"
inscricaoPrestador = "94812318"

objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

print(objServ.envioRPS(cnpj=cnpj,
                       inscricaoPrestador=inscricaoPrestador,
                       serieRPS="35",
                       numeroRPS="4201",
                       tipoRPS="RPS",
                       dtEmissao="2019-07-03",
                       statusRPS="N",
                       tributacaoRPS="T",
                       valorServicos="3",
                       valorDeducoes="0",
                       valorPis="0",
                       valorCofins="0",
                       valorINSS="0",
                       codigoServico="02660",
                       aliquota="0",  # Passado em % # Calculado automaticamente
                       cnpjTomador=cnpjTomador,
                       razaoSocialTomador=razaoSocialTomador,
                       logradouro="Rua dos Brasileiros",
                       numero="123",
                       complemento="Apto 182",
                       bairro="Morro Stark",
                       cep="01300040",
                       email="developers@starkbank.com",
                       discriminacao="Envio de Nota Fiscal de Servico Teste"
                       ))
