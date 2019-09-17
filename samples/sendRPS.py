# -*- coding: utf-8 -*-
from services.Services import Services

# Prestador
taxId = "20018183000180"  # CNPJ
providerSubscription = "57038597"  # Inscricao Municipal Prestador

# Tomador
companyName = "Google Brasil Internet Ltda"  # Razao Social Tomador
takerTaxId = "06990590000123"  # CNPJ Tomador

objServ = Services(certificateContent=open("../certfiles/converted.crt", "rb").read(),
                   RSAPrivateKeyContent=open("../certfiles/privRSAkey.pem", "rb").read(),
                   privateKeyContent=open("../certfiles/privateKey.key", "rb").read())


print(objServ.sendRPS(taxId=taxId,
                      providerSubscription=providerSubscription,
                      rpsSeries="50",
                      rpsNum="5005092019",
                      rpsType="RPS",
                      issueDate="2019-07-01",
                      rpsStatus="N",
                      rpsTax="T",
                      issRetain="false",
                      servicesValues="1",
                      deductionsValues="0",
                      pisValue="0",
                      cofinsValue="0",
                      inssValue="0",
                      serviceCode="05895",
                      aliquot="5",
                      takerTaxId=takerTaxId,
                      companyName=companyName,
                      street="Null",
                      streetNumber="0",
                      addressComplement="Null",
                      district="Null",
                      zipCode="00000000",
                      email="none@none",
                      # description="Serviços de boletos e transferências utilizados em Julho"
                      description="Null"
                      ))
