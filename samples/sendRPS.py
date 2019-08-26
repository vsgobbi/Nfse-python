# -*- coding: utf-8 -*-
from services.Services import Services

municipalSubscription = "57038597"

taxId = "20018183000180"  # CNPJ
companyName = "Google Brasil Internet Ltda"  # Razao Social Tomador
takerTaxId = "06990590000123"  # CNPJ Tomador
providerSubscription = "57038597"  # Inscricao Municipal Prestador

objServ = Services(certificateFile="../certfiles/converted.crt",
                   privateKeyRSA="../certfiles/privRSAkey.pem",
                   privateKeyFile="../certfiles/privateKey.key")

print(objServ.sendRPS(taxId=taxId,
                      providerSubscription=providerSubscription,
                      rpsSeries="35",
                      rpsNum="4201",
                      rpsType="RPS",
                      issueDate="2019-07-03",
                      rpsStatus="N",
                      rpsTax="T",
                      servicesValues="2",
                      deductionsValues="0",
                      pisValue="0",
                      cofinsValue="0",
                      inssValue="0",
                      serviceCode="02660",
                      aliquot="29",  # % calc
                      takerTaxId=takerTaxId,
                      companyName=companyName,
                      street="Rua dos Brasileiros",
                      streetNumber="123",
                      addressComplement="Apto 182",
                      district="Morro Stark",
                      zipCode="01300040",
                      email="developers@starkbank.com",
                      description="Envio de Nota Fiscal de Servico Teste"
                      ))
