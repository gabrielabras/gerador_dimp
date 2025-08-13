import streamlit as st
from datetime import datetime, timedelta
import io
import zipfile

# Lista de estados
estados = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
    'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
    'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]

# Modelo base para os arquivos
modelo_base = """|0000|09|4|{estado}|{cnpj}|{nome_empresa}|{data_ini}|{data_fim}|1|{competencia}|
|0001|1|
|0005|{nome_fantasia}|{endereco}|{cep}|{cod_mun}|{uf}|LUCAS RENNAN LEONEL LUBRIGATI|6740423050|LUCAS.LUBRIGATI@BEETELLER.COM|
|0990|4|
|1001|0|
|1990|2|
|9001|1|
|9900|0000|1|
|9900|0001|1|
|9900|0005|1|
|9900|0006|0|
|9900|0990|1|
|9900|1001|1|
|9900|1990|1|
|9900|9001|1|
|9900|9900|11|
|9900|9990|1|
|9900|9999|1|
|9990|14|
|9999|20|"""

# Dados específicos por empresa
modelos = {
    "software": {
        "cnpj": "38077404000156",
        "nome_empresa": "BEETELLER SOFTWARE LTDA",
        "nome_fantasia": "BEETELLER ID",
        "endereco": "RUA OTACILIO NEPONUCENO 600 SALA 907",
        "cep": "58410653",
        "cod_mun": "2504009",
        "uf": "PB"
    },
    "online": {
        "cnpj": "53191107000120",
        "nome_empresa": "BEETELLER PAGAMENTOS ONLINE LTDA",
        "nome_fantasia": "BEETELLER PAY",
        "endereco": "AV AFONSO PENA 5723 SALA 1805",
        "cep": "79031010",
        "cod_mun": "5002704",
        "uf": "MS"
    },
    "ip": {
        "cnpj": "32074986000130",
        "nome_empresa": "BEETELLER INSTITUICAO DE PAGAMENTO LTDA LTDA",
        "nome_fantasia": "BEETELLER BANK",
        "endereco": "AV AFONSO PENA 5723 SALA 1805",
        "cep": "79031010",
        "cod_mun": "5002704",
        "uf": "MS"
    },
    "internacional": {
        "cnpj": "38163054000140",
        "nome_empresa": "BEETELLER PAGAMENTOS INTERNACIONAIS LTDA",
        "nome_fantasia": "BEETELLER INTERNACIONAL",
        "endereco": "RUA OTACILIO NEPONUCENO 600 SALA 907",
        "cep": "58410653",
        "cod_mun": "2504009",
        "uf": "PB"
    }
}

# Lista de meses
meses = [
    ("01", "01 - Janeiro"), ("02", "02 - Fevereiro"), ("03", "03 - Março"),
    ("04", "04 - Abril"), ("05", "05 - Maio"), ("06", "06 - Junho"),
    ("07", "07 - Julho"), ("08", "08 - Agosto"), ("09", "09 - Setembro"),
    ("10", "10 - Outubro"), ("11", "11 - Novembro"), ("12", "12 - Dezembro")
]

def ultimo_dia_do_mes(ano, mes):
    """Calcula o último dia do mês para o ano e mês fornecidos."""
    try:
        data = datetime(ano, mes, 1)
        proximo_mes = data.replace(day=28) + timedelta(days=4)
        return (proximo_mes - timedelta(days=proximo_mes.day)).day
    except ValueError:
        return None

st.title("Gerador de Arquivos por Empresa, Ano e Mês")

# Interface do Streamlit
empresa = st.selectbox("Escolha a empresa", options=list(modelos.keys()), format_func=lambda x: x.capitalize())
ano = st.number_input("Ano", min_value=2000, max_value=2100, value=datetime.now().year)
competencia = st.text_input("Competência (ex: 202507)")
meses_selecionados = st.multiselect("Selecione os meses", options=meses, format_func=lambda x: x[1])

if st.button("Gerar arquivos"):
    if not meses_selecionados:
        st.warning("Selecione ao menos um mês.")
    elif not competencia:
        st.warning("Informe a competência.")
    else:
        try:
            memory_file = io.BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for mes_tuple in meses_selecionados:
                    mes = mes_tuple[0]
                    ultimo_dia = ultimo_dia_do_mes(ano, int(mes))
                    if ultimo_dia is None:
                        st.error(f"Data inválida para o mês {mes}/{ano}.")
                        break
                    data_ini = f"{ano}{mes}01"
                    data_fim = f"{ano}{mes}{ultimo_dia:02d}"

                    for estado in estados:
                        conteudo = modelo_base.format(
                            estado=estado,
                            data_ini=data_ini,
                            data_fim=data_fim,
                            competencia=competencia,
                            **modelos[empresa]
                        )
                        nome_arquivo = f"{empresa}/{ano}/{mes}/{estado}_{ano}{mes}.txt"
                        zf.writestr(nome_arquivo, conteudo)

            memory_file.seek(0)
            st.download_button(
                label="Baixar arquivos ZIP",
                data=memory_file,
                file_name=f"{empresa}_{ano}_arquivos.zip",
                mime="application/zip"
            )
            st.success("Arquivos gerados com sucesso!")
        except Exception as e:
            st.error(f"Erro ao gerar os arquivos: {str(e)}")
            