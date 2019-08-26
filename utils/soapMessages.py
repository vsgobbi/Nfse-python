# -*- coding: utf-8 -*-

# Schemas dos servicos para fazer a assinatura
# Toda vez que é gerado um novo envelope SOAP,
# deve conter um DigestValue diferente pois a assinatura
# do xml é feita na raiz da tag <MensagemXML> para a prefeitura de São Paulo.
# onde <MensagemXML> deve conter <![CDATA[ *MENSAGEM* ]]>
consultaCNPJ = """
<p1:PedidoConsultaCNPJ xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho Versao="1"><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente></Cabecalho><CNPJContribuinte><CNPJ></CNPJ></CNPJContribuinte></p1:PedidoConsultaCNPJ>
"""

# A assinatura do RPS deve ser feita em RSA-SHA1 antes de assinar a MensagemXML.
envioRPS = """
<p1:PedidoEnvioRPS xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho xmlns="" Versao="1"><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente></Cabecalho><RPS xmlns=""><Assinatura></Assinatura><ChaveRPS><InscricaoPrestador></InscricaoPrestador><SerieRPS>OL03</SerieRPS><NumeroRPS>4105</NumeroRPS></ChaveRPS><TipoRPS>RPS-M</TipoRPS><DataEmissao>2019-07-01</DataEmissao><StatusRPS>N</StatusRPS><TributacaoRPS>T</TributacaoRPS><ValorServicos>11100</ValorServicos><ValorDeducoes>0</ValorDeducoes><ValorPIS>10</ValorPIS><ValorCOFINS>10</ValorCOFINS><ValorINSS>10</ValorINSS><ValorIR>10</ValorIR><ValorCSLL>10</ValorCSLL><CodigoServico>02660</CodigoServico><AliquotaServicos>0.5</AliquotaServicos><ISSRetido>false</ISSRetido><CPFCNPJTomador><CNPJ>30134945000167</CNPJ></CPFCNPJTomador><RazaoSocialTomador></RazaoSocialTomador><EnderecoTomador><Logradouro>Rua dos Ingleses</Logradouro><NumeroEndereco>586</NumeroEndereco><ComplementoEndereco>Apto 182</ComplementoEndereco><Bairro>Jardim Paulista</Bairro><Cidade>3550308</Cidade><UF>SP</UF><CEP>01329000</CEP></EnderecoTomador><EmailTomador>aaaaaaa@aaaaaaa.com.br</EmailTomador><Discriminacao>Envio NFSe teste</Discriminacao></RPS></p1:PedidoEnvioRPS>
"""

envioRPS2 = """
<p1:PedidoEnvioRPS xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho xmlns="" Versao="1"><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente></Cabecalho><RPS xmlns=""><Assinatura></Assinatura><ChaveRPS><InscricaoPrestador></InscricaoPrestador><SerieRPS>BB</SerieRPS><NumeroRPS>4102</NumeroRPS></ChaveRPS><TipoRPS>RPS</TipoRPS><DataEmissao>2015-01-20</DataEmissao><StatusRPS>N</StatusRPS><TributacaoRPS>T</TributacaoRPS><ValorServicos>100</ValorServicos><ValorDeducoes>0</ValorDeducoes><ValorPIS>1.01</ValorPIS><ValorCOFINS>1.02</ValorCOFINS><ValorINSS>1.03</ValorINSS><ValorIR>1.04</ValorIR><ValorCSLL>1.05</ValorCSLL><CodigoServico>7811</CodigoServico><AliquotaServicos>0.05</AliquotaServicos><ISSRetido>false</ISSRetido><CPFCNPJTomador><CPF>99999999727</CPF></CPFCNPJTomador><RazaoSocialTomador>ANTONIO PRUDENTE</RazaoSocialTomador><EnderecoTomador><TipoLogradouro>RUA</TipoLogradouro><Logradouro>PEDRO AMERICO</Logradouro><NumeroEndereco>1</NumeroEndereco><ComplementoEndereco>1 ANDAR</ComplementoEndereco><Bairro>CENTRO</Bairro><Cidade>3550308</Cidade><UF>SP</UF><CEP>00001045</CEP></EnderecoTomador><EmailTomador>teste@teste.com</EmailTomador><Discriminacao>Nota Fiscal de Teste Emitida por Cliente Web</Discriminacao><ValorCargaTributaria>30.25</ValorCargaTributaria><PercentualCargaTributaria>15.12</PercentualCargaTributaria><FonteCargaTributaria>IBPT</FonteCargaTributaria></RPS></p1:PedidoEnvioRPS>
"""

envioLoteRPS = """
<p1:PedidoEnvioLoteRPS xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<Cabecalho xmlns="" Versao="1"><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente>
<transacao>false</transacao><initDate>2019-07-01</initDate><endDate>2019-07-01</endDate>
<QtdRPS>1</QtdRPS><ValorTotalServicos>2</ValorTotalServicos>
<ValorTotalDeducoes>0</ValorTotalDeducoes></Cabecalho><RPS xmlns="">
<Assinatura></Assinatura><ChaveRPS><InscricaoPrestador></InscricaoPrestador>
<SerieRPS>L003</SerieRPS><NumeroRPS>33</NumeroRPS></ChaveRPS><TipoRPS>RPS</TipoRPS>
<DataEmissao>2019-07-01</DataEmissao><StatusRPS>N</StatusRPS><TributacaoRPS>T</TributacaoRPS>
<ValorServicos>2</ValorServicos><ValorDeducoes>0</ValorDeducoes><CodigoServico>05895</CodigoServico>
<AliquotaServicos>0.029</AliquotaServicos><ISSRetido>false</ISSRetido><CPFCNPJTomador><CNPJ></CNPJ>
</CPFCNPJTomador><RazaoSocialTomador></RazaoSocialTomador>
<EnderecoTomador><Logradouro>Rua dos Ingleses</Logradouro><NumeroEndereco>586</NumeroEndereco>
<ComplementoEndereco>Apto 63</ComplementoEndereco><Bairro>Jardim Paulista</Bairro>
<Cidade>3550308</Cidade><UF>SP</UF><CEP>01329000</CEP></EnderecoTomador>
<EmailTomador>email@company.com.br</EmailTomador><Discriminacao>Envio NFSe teste</Discriminacao>
</RPS></p1:PedidoEnvioLoteRPS>
"""

consultaNfePeriodo = """
<p1:PedidoConsultaNFePeriodo xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho Versao="1"><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente><CPFCNPJ><CNPJ></CNPJ></CPFCNPJ><Inscricao></Inscricao><dtInicio>2019-06-01</dtInicio><dtFim>2019-07-01</dtFim><NumeroPagina>1</NumeroPagina></Cabecalho></p1:PedidoConsultaNFePeriodo>
"""

consultaNFe = """
<p1:PedidoConsultaNFe xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho Versao="1"><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente></Cabecalho><Detalhe><ChaveNFe><InscricaoPrestador>57038597</InscricaoPrestador><NumeroNFe></NumeroNFe></ChaveNFe></Detalhe></p1:PedidoConsultaNFe>
"""

# Deve retornar assinatura utilizando RSA SHA1 de 172 caracteres em ASCII
"""
# Para criar a assinatura deverá ser gerado um Hash (utilizando SHA1) de uma cadeia de caracteres (ASCII) com informações da NF-e a ser cancelada.
# Este Hash deverá ser assinado utilizando RSA.
# A assinatura do Hash será informada na TAG AssinaturaCancelamento.
"""
# Prazo de cancelamento da NFS-e: 20 dias
cancelamentoNota = """
<p1:PedidoCancelamentoNFe xmlns:p1="http://www.prefeitura.sp.gov.br/nfe" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><Cabecalho Versao="1" xmlns=""><CPFCNPJRemetente><CNPJ></CNPJ></CPFCNPJRemetente><transacao>true</transacao></Cabecalho><Detalhe xmlns=""><ChaveNFe><InscricaoPrestador></InscricaoPrestador><NumeroNFe></NumeroNFe></ChaveNFe></Detalhe></p1:PedidoCancelamentoNFe>
"""

