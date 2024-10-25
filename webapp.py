import streamlit as st
import requests
import uuid
import time

import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Load environment variables from .env file
load_dotenv()

# Retrieve the values from the environment
#from_email = os.getenv("EMAIL_USER")  # Load email from .env file
#email_password = os.getenv("EMAIL_PASS")  # Load app password from .env file

from_email = st.secrets['EMAIL_USER']
email_password = st.secrets['EMAIL_PASS']

# Hardcoded dictionary to map source filenames to URLs
source_mapping = {
    'Circolare n. 35 del 28_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718712/Circolare+articolo+6+dPR+601+1973+e+detassazione+utili_pdf.pdf/98d7e1ea-7c74-366f-f0bd-a7fbfffdf8bf',
    'Circolare n. 34 del 28_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718712/Circolare_n_34_del_28_12_2023.pdf/7128f40e-5505-fab2-be02-512a94d3ac05',
    'Circolare n. 33 del 21_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718712/Circolare+nautica+da+diporton.+33+del+21+dicembre+2023.pdf/07c85844-d7dd-3872-1b68-e7dcb7bc5464',
    'Circolare n. 32 del 5_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718712/Circolare_n_32_Regime+forfetario_05_12_2023.pdf/23d1370d-6bba-0eb7-70b8-d1d24d5a1c0f',
    'Circolare n. 31 del 9_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671393/Circolare_n_31_del_09_11_2023.pdf/990b4017-e5b0-9b72-0bb5-84bbdad988de',
    'Circolare n. 30 del 27_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589638/Circolare+criptoattivita+del+27+ottobre+2023.pdf/1154a95a-80ea-a6ec-bcc0-731b844db9e6',
    'Circolare n. 29 del 19_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589638/Circolare+n.+29+del+19+ottobre+2023.pdf/128b0589-0cac-02da-c4a4-c5b8a4d9314c',
    'Circolare n. 28 del 16_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589638/Circolare_Rendita+Centrali+eoliche+del+16+ottobre+2023.pdf/8a2d37d8-7f34-43bb-0b14-ac82867215c7',
    'Circolare n. 27 del 7_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519468/Circolare_n_27_del_07_09_2023.pdf/7d062164-cf86-3c66-85cf-5400f5757fd0',
    'Circolare n. 26 del 29_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476618/circolare_mance.+n.+26+del+29+agosto+2023.pdf/de712227-9c32-3c1a-897f-ae782f5450cb',
    'Circolare n. 25 del 18_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476618/Circolare+Smart+working+e+Frontalieri+18+ago+2023.pdf/988122df-912b-afd1-8942-c2b20f0ab64c',
    'Circolare n. 24 del 2_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476618/circolare+n.+24+del+2+aosto+2023+energia+e+gas+-+riduzione+iva+5+per+cento.pdf/0372d2c5-1380-c25d-4537-a990aa6fc10b',
    'Circolare n. 23 del 1_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476618/circolare_welfarerev+n.+23+del+1+agosto+2023.pdf/b9c33ddb-1838-ac3d-8355-5dd1332dd196',
    'Circolare n. 22 del 28_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409684/Circolare+n.+22+del+28+luglio+2023+bollo+codice+dei+contratti+pubblici.pdf/89c37c94-19f4-1c20-be60-5e52f578d9ab',
    'Circolare n. 21 del 26_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409684/21_7Circolare+rinuncia+agevolata+del+26+luglio+2023_v2.pdf/f6068b30-b8ac-5eba-8cbc-cdcbcd4c9bf8',
    'Circolare n. 20 del 7_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409684/Circolare+n.+20+del+7+luglio+2023_Art_18_semplificazioni.pdf/c8b69382-1a8a-a65d-fdc8-3c52842336dd',
    'Circolare n. 19 del 6_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409684/Circolare_19E_06_07_2023.pdf/65e9f34a-d45f-423c-cb90-adff99071d89',
    'Circolare n. 18 del 28_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/20230628+Circolare_flat_tax_incrementale+.pdf/b782f9fc-3749-f187-9d20-538c9969d76b',
    'Circolare n. 17 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/Circolare+n.+17+guida+2023+terza+parte+26.06.23.pdf/c04a174f-084c-5ed0-fe8d-b1d0bdbc333b',
    'Circolare n. 16 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/Rideterminazione+e+affrancamento+pubbl.pdf/0ea31075-bdf6-4009-69f0-f9f5f18d350f',
    'Circolare n. 15 del 19_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/Circolare+caf+2023+parte+seconda+19.06.23.pdf/6d0a9926-9d83-81df-0026-15784cb2c2e8',
    'Circolare n. 14 del 19_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/Circolare+caf+2023+generale_sez+I+19.06.23.pdf/96ce0bb3-4efa-2bc8-72f2-e0944ab65223',
    'Circolare n. 13 del 13_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/Circolare+Superbonus+n.+13++del+13+giugno+2013.pdf/6185d591-960a-5be2-06ce-fe8f0a6397fb',
    'Circolare n. 12 del 1_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329166/Circolare+ISA+del+1+giugno+2023.pdf/449b1fa2-fe06-f663-708b-2cf162d576b1',
    'Circolare n. 11 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256660/Circolare_Frazionamento_Enti_Urbani+accessibile.pdf/4b9b0350-b283-c650-0fa4-bd4b526223e7',
    'Circolare n. 10 del 20_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187526/circolare+n.+10+del+20+aprile+2023+Cerificazione+SOA.pdf/fb5266b4-aaba-3eea-8e9c-fde5191afda2',
    'Circolare n. 9 del 19_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187526/Circolare+conciliazione+agevolata+n.+9+del+19+aprile+2023.pdf/23b89e75-0af5-7063-a91e-c36e9db05b45',
    'Circolare n. 8 del 6_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187526/Circolare_n+8+art_1_DLgs_72_2022_Iva_forze_armate.pdf/1c6d81ee-6950-7e0a-385f-28b3dd89e4b8',
    'Circolare n. 7 del 28_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081192/CIRCOLARE+n.+7+NUOVI+CHIARIMENTI+UV.pdf/8b937cd1-b861-0249-1cc3-fc0989e24f0c',
    'Circolare n. 6 del 20_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081192/circolare+n+6_tregua_fiscale_del+20+marzo+2023.pdf/5e8a2e76-dd65-3188-b9a7-9e6f1fa86aff',
    'Circolare n. 5 del 24_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988552/Circolare+nuovo+Patent+Box+24.02.23.pdf/dd915ff5-4358-658a-102d-023a65dfd9a6',
    'Circolare n. 4 del 23_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988552/Circolare_n_4_del_23_02_2023.pdf/c25e04f0-577d-0206-ae91-863d1e248c06',
    'Circolare n. 3 del 8_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988552/Circolare+10bis+art+119+dl+34+2020.pdf/b367ac4c-252c-5887-63d5-f8ca69e20218',
    'Circolare n. 2 del 27_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913759/Circolare+n+2+tregua+fiscale.pdf/653eefeb-e3a5-053c-4b70-3bc8cb8439d3',
    'Circolare n. 1 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913759/Circolare+definizione+agevolata+esiti+controllo+automatizzato+del+13+gennaio+2023.pdf/e17de938-ace5-6caf-65c8-3fa04095a3b2',
    'Circolare n. 19 del 10_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458352/circolare_bonus_100_euro_+del+10+ottobre+2024.pdf/9961bc67-a986-d44f-61de-7bdaf528bd68',
    'Circolare n. 18 del 17_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390995/Circolare+CPB_17092024.pdf/79992204-e5b6-6977-e9bc-fb5f7c5894e9',
    'Circolare n. 17 del 29_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241350/Circolare+plus.+non+residenti+29.07.24.pdf/e1583743-c87e-3868-7b97-6ed8d1f2f91e',
    'Circolare n. 16 del 28_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193294/Circolare_compensazioni_LdB_Agevolaz.+del+28+giugno+2024.pdf/cbc0841d-027f-39d8-8380-9be7e56ec888',
    'Circolare n. 15 del 25_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193294/Circolare_ISA_del+25+giugno+2024+n.+15.pdf/8279f557-a368-40b1-87e7-085389d8d595',
    'Circolare n. 14 del 18_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193294/circolare+n+14_2024+under36_milleproroghe.pdf/f56160f7-050c-8208-2041-e836277179c4',
    'Circolare n. 13 del 13_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193294/Circolare+plusvalenze+superbonus+n.+13+del+13+giugno+2024_.pdf/6aea10c1-d402-3204-eb3e-b8a64422a43d',
    'Circolare n. 12 del 31_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101200/Circolare+12+CAF+risposte+a+quesiti.pdf/5f41a2f3-934e-af7c-3e1e-42e9b27002d7',
    'Circolare n. 11 del 15_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101200/circolare_ravvedimentospeciale+n.+11+del+15+maggio+2024.pdf/e1e2117a-b455-a4c1-009b-07b20810640b',
    'Circolare n. 10 del 10_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101200/circolare+locazioni+brevi+.+10+del+10+maggio++2024.pdf/6b3c5a29-9158-959b-91fb-8cdab88367eb',
    'Circolare n. 9 del 2_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101200/Circolare+n.+9_02_05_2024.pdf/c5932a62-5b45-179a-adbe-ccdb3db9b0b8',
    'Circolare n. 8 del 11_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021640/Circolare_Adempimenti_I_dichiarazioni+n.+8+del+11+aprile+2024.pdf/12971cd2-bf4a-7a02-5884-bfe58f596211',
    'Circolare n. 7 del 21_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946182/Circolare+n.+7+del+21_03_2024.pdf/eada2826-0c44-1990-f9f9-a5cad89c35eb',
    'Circolare n. 6 del 8_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946182/Circolare+%2B+modello+n.+6+di+8+marzo+2024.pdf/dcf6fc16-b660-bbdc-01b1-7b4331d5e9c9',
    'Circolare n. 5 del 7_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946182/Circolare+n+5+del+7+marzo_2024+LB1_DL+Anticipi.pdf/ea0bc038-3618-c4f2-872f-6d20cf99ca8e',
    'Circolare n. 4 del 23_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866239/Circolare_n_4_del_23_02_2024.pdf/dd38ea66-feed-f66e-2d03-e68f9a6515f0',
    'Circolare n. 3 del 16_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866239/Circolare+n+3_del+16_2_2024.pdf/6e8e87f4-a360-b3c0-8b0b-475cf43ab2d8',
    'Circolare n. 2 del 6_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866239/Circolare_n_2_del_06_02_2024.pdf/4ec75f44-b2c0-3af7-a45a-2d971d6f3c19',
    'Circolare n. 1 del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5780794/Circolare+1_2024+-+Pubblici+registri+immobiliari+v.accessibile.pdf/db4ef611-a6fc-3b67-4512-a5ab9dfde3c3',
    'Provvedimento del 30_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913767/Provvedimento_atti_LB2023.pdf/ac04d332-4c53-71ed-d6e0-43d14e911cef',
    'Provvedimento del 27_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-27-gennaio-2023',
    'Provvedimento del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-26-gennaio-2023',
    'Provvedimento del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-18-gennaio-2023',
    'Provvedimento del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-17-gennaio-2023',
    'Provvedimento del 16_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913767/Provvedimento+del+16+gennaio+2023+medie+valute+estere+del+mese+di+dicembre+2022.pdf/208d906f-bdd5-52d0-d923-f08dfecb90e5',
    'Provvedimento del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-13-gennaio',
    'Provvedimento del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913767/Provvedimento+precompilata+IVA+del+12+gennaio+2023.pdf/5a1c896c-8483-915f-e04f-323862daa97f',
    'Provvedimento del 28_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-28-febbraio-2023',
    'Provvedimento del 24_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988273/Provvedimento+nuovo+Patent+Box_24-02-2023-U.pdf/0e1f8f26-1390-0224-6935-657fbd47beb2',
    'Provvedimento del 16_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-16-febbraio-20-1',
    'Provvedimento del 15_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988273/AGEDC001_43406_2023_+Provvedimento+del+15+febbraio+2023.pdf/f52fc6bf-cf9c-163a-a815-773c0fcfa43f',
    'Provvedimento del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988273/Provvedimento+del+14+febbraio+2023+medie+dei+cambi+delle+valute+estere+Gennaio+2023.pdf/36545765-f29b-fe20-1edd-9b8c2a0d4467',
    'Provvedimento del 08_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988273/Provvedimento+Campione+Italia+8.02.23.pdf/7e28a74b-758f-77e5-a789-39de37f54c63',
    'Provvedimento del 07_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-7-febbraio-2023',
    'Provvedimento del 06_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/foglia-provvedimento-6-febbraio-2023',
    'Provvedimento del 01_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/foglia-provvedimento-1-febbraio-2023',
    'Provvedimento del 31_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-31-marzo-2023',
    'Provvedimento del 24_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081188/Provved.+percentuale+credito+imprese+agricole+del+24+marzo+2023.pdf/190c4f01-0576-e583-4a94-a2f1cc968885',
    'Provvedimento del 23_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-23-marzo-2023',
    'Provvedimento del 22_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081188/Provvedimento+del+22+marzo+2023.pdf/b2bc2aa2-3267-237d-dde3-2b5992bffc4d',
    'Provvedimento del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081188/Provvedimento+Febbraio+2023+-+Per+pubblicazione.pdf/6f091d0e-ff64-5d13-05d9-40260950f4f1',
    'Provvedimento del 06_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081188/Provvedimento_Lista+invii+tardivi_06.03.23.pdf/1f4266bf-cc97-57c6-b27b-f53c03875424',
    'Provvedimento del 01_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-1-marzo-20-1',
    'Provvedimento del 28_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187522/provvedimento+assunzione+idonei+del+28+aprile+2023.pdf/d8b26c54-fa24-3d84-c39c-bd0f19297de3',
    'Provvedimento del 27_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187522/Provvedimento_premiale+2023_del+27+aprile+2023.pdf/21cac6d5-4402-f14f-c4e2-c0922c332315',
    'Provvedimento del 19_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187522/PROVVEDIMENTO_lettere+compliance_+del+19+aprile+2023.pdf/9db8bf4a-aaaa-c80c-e4b7-1cb44a3de540',
    'Provvedimento del 18_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187522/Provvedimento_18.04.2023_cambi.pdf/6337e208-20bf-aa5a-8137-58155277f8a0',
    'Provvedimento del 17_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-17-aprile-2023',
    'Provvedimento del 05_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187522/Provvedimento_05.04.2023_pegno-non-possessorio.pdf/fa551458-d505-2ebf-2c23-55dcecea5100',
    'Provvedimento del 04_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-4-aprile-2023',
    'Provvedimento del 03_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-3-aprile-20-1',
    'Provvedimento del 26_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4452897/10+DIR+-+atto+approvazione+graduatoria.pdf/5fac8adc-08dd-ce4f-9906-fe3335e2d1fc',
    'Provvedimento del 16_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-16-maggio-20-4',
    'Provvedimento del 12_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256656/Provvedimento_cambio_valute_aprile2023.pdf/f024ce27-4def-325a-a532-45c5dc6abce3',
    'Provvedimento del 28_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/provv_bollo+contratti+pubblici_28+giugno+2023.pdf/ddf07b91-9d18-152a-be4b-eef49f715400',
    'Provvedimento del 27_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento_articolo_1_comma_35_legge_234_2021+del+27+giugno+2023.pdf/f11799b3-c726-b4c3-07ef-20d86421fe64',
    'Provvedimento del 23_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimentodel+23+giugno+2023+-+Credito+d%27imposta+registratori+telematici.pdf/6cb76b4d-bc11-e820-7733-523bc8b9f449',
    'Provvedimento del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento+del+20_6_23_Revisione_verifiche_UPT.pdf/c38b1c26-0e4e-8cb6-6917-f8a803f43798',
    'Provvedimento del 15_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento+del+15+maggio+2023+valute+estere+maggio.pdf/1ce85b68-2622-fb63-9341-fb286cd4ff8c',
    'Provvedimento del 14_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento+codice+negozio+pegno+mobiliare++del+14+giugno+2023.pdf/853666de-be8d-62c7-4375-a3008a633153',
    'Provvedimento del 13_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento+lista+tardive+incomplete+IVA+2022.pdf/ec44ef48-7ee6-de4a-d0b9-b1a0e5dfac6f',
    'Provvedimento del 09_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento+CPR+730-2023+del+9+giugno+2023.pdf/ed8a5277-caf8-7a4d-0e77-7858de80e11c',
    'Provvedimento del 01_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-1-giugno-2023',
    'Provvedimento del 25_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/aggiornamento-del-modello-di-dichiarazione-di-successione-e-domanda-di-volture-catastali-delle-relative-istruzioni-e-specifiche-tecniche-per-la-trasmi',
    'Provvedimento del 24_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409680/bando_530_SPI.pdf/55aa2851-f221-8260-fa6d-c02043f09ca9',
    'Provvedimento del 17_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409680/Provvedimento+Giugno+2023++cambio+valute+estere+del+17+luglio+2023.pdf/1707878f-1b42-41d8-e659-9eeff880ca08',
    'Provvedimento del 11_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409680/Provvedimento+11+luglio+2023.pdf/e073a810-b333-7d49-c8ef-f3964e89becc',
    'Provvedimento del 05_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-5-luglio-2023',
    'Provvedimento del 24_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476614/bando_530_spi.pdf/b6d5640c-61cf-e715-5304-f3e6aae1c9df',
    'Provvedimento del 14_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476614/Provvedimento+Luglio++2023+-+Per+pubblicazione.pdf/07b69c2d-d316-5cd8-6098-19099f776be8',
    'Provvedimento del 07_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-07-agosto-2023',
    'Provvedimento del 06_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409680/Provvedimento+di+revoca+ad+EntratelGAIOTTIdeceduto+del+6+luglio+2023.pdf/2c11e1aa-1c7f-98de-ad46-c2a3231904e5',
    'Provvedimento del 22_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329112/Provvedimento+del+22+giugno+2023+-+Revoca+entratel.pdf/488cd8c8-3db0-3d79-bd0d-c6f1977395d7',
    'Provvedimento del 26_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519464/Provvedimento+del+26+settembre+2023+-++medie+dei+cambi+delle+valute+estere+agosto+2023.pdf/0b4fdb9c-0c88-47e9-2435-266cf6ba2658',
    'Provvedimento del 22_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-22-settembre-2023-abilitazione-servizi-online',
    'Provvedimento del 19_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519464/Bozza+Provvedimento+lista+forfettari+senza+RS_202309133453988186121309182.pdf/ae6341ff-4d77-eb99-92f1-40465b720da6',
    'Provvedimento del 15_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519464/atto+ridenominazione+Coneglianoxpub.pdf/51cde817-8331-25b8-d7ca-be3dc3da00ae',
    'Provvedimento del 18_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589642/Provvedimento+del+18+ottobre+2023+medie+valute+Settembre+2023.pdf/78bd69cc-036c-7e9b-8da5-864940b57072',
    'Provvedimento del 17_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-17-ottobre-2023',
    'Provvedimento del 16_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589642/PI_UPT_Decreto+inizio+periodo+irr.funz+-.pdf/7dde8d6f-a0ee-6f25-1119-bb79960cec1a',
    'Provvedimento del 13_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589642/Provvedimento+Senato_protocollo.pdf/5460ba4f-3382-a03b-9771-46e618b37f11',
    'Provvedimento del 09_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589642/provvedimento+riavvio+tirocinio.pdf/4e3a4045-c116-98f7-1afe-443d34178751',
    'Provvedimento del 04_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-4-ottobre-2023',
    'Provvedimento del 03_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589642/Provv.+pagamenti+elettronici_02102023.pdf/51b60412-72ee-663c-e0c8-b928c012ef40',
    'Provvedimento del 29_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-29-novembre-2023',
    'Provvedimento del 28_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671389/provvedimento+credito+FOB+FUN+2023+del+28+novembre+2023.pdf/08d5aa65-c330-53b8-c377-30f71e0e7ad4',
    'Provvedimento del 24_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671389/Provvedimento_ripartizione_cfp_interventidetraibili90.pdf/d562f480-14a6-6c07-6cfd-20642516a64c',
    'Provvedimento del 23_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671389/Provv.+comunicazione+bonus+edilizi+non+utilizzabili+PUB.pdf/63a73586-ab54-6052-f1f0-662f662c8674',
    'Provvedimento del 20_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-20-novembre-2023',
    'Provvedimento del 15_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671389/Provvedimento+n.+402886+del+15+11+23.pdf/87847202-4e19-7fd7-c9b7-1b56bb533b97',
    'Provvedimento del 14_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671389/Provvedimento+del+14+novembre+2023+media+dei+cambi+del+mese+di+ottobre.pdf/132981ad-5396-4507-9b00-3a2f38bfa22e',
    'Provvedimento del 08_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-dell-8-novembre-2023',
    'Provvedimento del 28_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718708/Modifiche+Provvedimento+4+agosto+2020.pdf/6622ce35-0672-b7fc-5c8e-c65bf3bad098',
    'Provvedimento del 20_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718708/Provvedimento+del+20+dicembre+2023+_+medie+cambi+valute+novembre+2023+.pdf/fd2d70ea-83ca-05fd-d464-41592420f14d',
    'Provvedimento del 19_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718708/PROVVEDIMENTO_ACCONTO_IVA_DICEMBRE_2023+CON+PROTOCOLLO.pdf/7c5f10a5-a068-1580-f3b3-162c4e72be8d',
    'Provvedimento del 18_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718708/Provvedimento_+fusione_tra_fondazioni_18_12_2023.pdf/188466c7-37d8-0c1e-5982-3a65071706fc',
    'Provvedimento del 07_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458356/ProvvComunicazioneDomiciliodigitaleSpeciale+del+7+ottobre+2024.pdf/f1ad2896-77fc-4a22-0e61-6acadce56a5d',
    'Provvedimento del 10_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458356/AGEDC001_383481_2024_3103_del+10+ottobre+2024.pdf/4281d0e8-1b7c-95cb-e41f-bd00db407e21',
    'Provvedimento del 02_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-2-ottobre-2024',
    'Provvedimento del 30_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6404768/Provvedimento+firma+digitale+processi+verbali+ADE+30_09_2024.pdf/2515e213-57ef-17b1-71df-3329397701a2',
    'Provvedimento del 25_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6404768/3970TRIB_aumento_Marche.pdf/6ba07ba8-d27c-b3e2-077b-17bec9c3829a',
    'Provvedimento del 19_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6404768/Provvedimento+Camera+dei+Deputati_2024_protocollo.pdf/aea03cb1-006e-f503-7e9b-2cea9c473cd6',
    'Provvedimento del 18_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-18-settembre-2024',
    'Provvedimento del 13_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6404768/Provvedimento+medie+valute+agosto+del+13+settembre+2024.pdf/13558c40-9a2e-ea4e-4682-ed02c2f2976a',
    'Provvedimento del 09_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-9-settembre-2024',
    'Provvedimento del 07_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314627/Provvedimento_Cambio_valute_7_08_2024.pdf/6a4c14e3-9c60-1068-6a09-4d6e6ff2bec6',
    'Provvedimento del 31_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241354/Provvedimento_del_31_07_2024.pdf/b0ada687-16e5-0be0-bcfc-cb451b6fa84e',
    'Provvedimento del 29_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241354/3970+trib_rettifica_Umbria.pdf/d2147150-61f7-b7cf-5f3c-8f960dac1273',
    'Provvedimento del 22_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241354/Provvedimento_del_22_07_2024_percentuale_credito_ZES_UNICA.pdf/9cbae0ac-1361-efbf-7c45-9845e0124fb3',
    'Provvedimento del 16_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241354/PROVV.+VEICOLI+STATI+ART.+71.pdf/cf241bb4-3bc3-bc14-6cba-b0776ecf7f04',
    'Provvedimento del 15_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241354/Provvedimento+accertamento+valute+estere+giugno+2024+del+15+luglio+2024.pdf/b5aa5bce-9834-e8b0-deec-42175b86ab10',
    'Provvedimento del 11_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-11-luglio-2024',
    'Provvedimento del 01_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-1-luglio-2024',
    'Provvedimento del 11_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193290/Bando+RU+modifica.pdf/e6678968-5c41-900b-dc17-674c72051b43',
    'Provvedimento del 27_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-27-giugno-2024',
    'Provvedimento del 26_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193290/Provvedimento+Deskdel+26+giugno+2024.pdf/d860fa81-1922-866b-97ae-91f86b9a073a',
    'Provvedimento del 20_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-20-giugno-2024',
    'Provvedimento del 17_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193290/Provvedimento+CPR+730-17.06.24.pdf/9707ba92-3f94-49c1-0aa3-28bbeb1bf0fe',
    'Provvedimento del 12_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193290/Provvedimento+lista+tardive+incomplete+IVA+del+12+giugno+2024.pdf/80f10dae-8af7-e151-f6e5-2b32758e1b74',
    'Provvedimento del 07_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193290/Provvedimento+percentuale+credito+impianti+compostaggio+del+7+giugno+2024.pdf/d83bec79-89b5-23fd-0e54-ebed1c342d6d',
    'Provvedimento del 05_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193290/Provvedimento_art+38+bis+lett+g_1+del+5+giugno+2024.pdf/994d210f-049f-fad2-ba79-20f78664b741',
    'Provvedimento del 09_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101192/amm_trasp_rettifica+bando+530+SPI.pdf/1fad8460-2a58-b4fa-76f7-fe5f3e03c541',
    'Provvedimento del 31_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101192/provvedimento_cessione_cuochi_professionisti_del+31+mqggio+2024.pdf/82481243-781a-355a-b8c5-970f6615d567',
    'Provvedimento del 15_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101192/Provvedimento+Aprile+2024++accertamento+cambio+valute+estere.pdf/b9a58571-1b9d-b8ce-4bc3-f5dcd101fe13',
    'Provvedimento del 07_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101192/3+-+Provvedimento+prot.+221010+del+7+maggio+2024_pub.pdf/5f8ff398-35bd-1bf5-284a-289caa258d51',
    'Provvedimento del 29_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-29-aprile-2024',
    'Provvedimento del 22_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021288/Provvedimento_premiale+2024_firmato+e+protocollato.pdf/e6e86d0a-8498-83b8-5ba3-8ad9b56a7be7',
    'Provvedimento del 17_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021288/provvedimento_concorso_10_dir_idonei.pdf/b026a622-6a69-4217-fd77-acf5f9513855',
    'Provvedimento del 16_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-16-aprile-2024',
    'Provvedimento del 12_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-12-aprile-2024',
    'Provvedimento del 15_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021288/Provvedimento+cambio+valute+Marzo+2024+.pdf/33036ab5-f879-da24-14d5-7a2a13ca616a',
    'Provvedimento del 30_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021288/Provvedimento+CFC+opzione+4+ter+30_4_24.pdf/7def3d89-0890-74a5-ce3e-c4af831383b1',
    'Provvedimento del 29_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-29-marzo-2024',
    'Provvedimento del 27_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-27-marzo-2024',
    'Provvedimento del 22_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946186/Provvedimento+percentuale+credito+acqua+potabile+del+22+marzo+2024.pdf/3a3a1ad0-1a08-5b83-f162-b977affeaff0',
    'Provvedimento del 21_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946186/Provvedimento_21_03_2024.pdf/95616285-eb29-1ddf-f8ff-ae1e7f69c046',
    'Provvedimento del 14_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-14-marzo-2024',
    'Provvedimento del 13_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/atto-congiunto-del-13-marzo-2024-agenzia-delle-entrate-e-inps',
    'Provvedimento del 08_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946186/Provvedimento+FE105669_24-03-08.pdf/af6f36cc-f274-e712-65eb-5183ca3c739d',
    'Provvedimento del 04_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-4-marzo',
    'Provvedimento del 28_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-28-febbraio-2-15',
    'Provvedimento del 26_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-26-febbraio-2024',
    'Provvedimento del 21_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-21-febbraio-2024',
    'Provvedimento del 09_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-9-febbraio-20-3',
    'Provvedimento del 30_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5780651/Provvedimento_30_01_2024_DAC7.pdf/003ec65e-07d2-46e2-729f-967618a590cd',
    'Provvedimento del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-di-nomina-degli-agenti-contabili-del-29-gennaio-2024',
    'Provvedimento del 26_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-26-gennaio-2024',
    'Provvedimento del 23_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5780651/Provvedimento+estensione+MUI+del+23+gennaio+2024.pdf/22b1f548-207a-069c-38e3-71dbeb601dd3',
    'Provvedimento del 22_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-22-gennaio-2024',
    'Provvedimento del 19_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5780651/Provvedimento+n.+11806+del+19+gennaio+2024.pdf/242d618f-5f98-69c4-655e-3fce8487ad15',
    'Provvedimento del 17_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5780651/Provvedimento+Dicembre+2023+-+Per+pubblicazione.pdf/aea5283f-a9d1-9f81-7715-e91b3f4d18a2',
    'Provvedimento del 15_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-15-gennaio-2024',
    'Provvedimento del 11_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/web/guest/-/provvedimento-del-11-gennaio-2024',
    'Provvedimento del 09_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5780651/Provv.to+di+modifica+credito+acqua+potabile+26+1+22.pdf/a73cc0b8-c2ee-476d-152e-f590e53a8c98',
    'Risoluzione n. 77 del 22_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/Risoluzione_77_del_22_12_2023.pdf/490182a5-331c-b293-506b-d628de067e2c',
    'Risoluzione n. 76 del 22_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/Risoluzione+n.+76_2023.pdf/5f74d33c-4647-c174-367e-bd40b52e17b9',
    'Risoluzione n. 75 del 21_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/Risoluzione+n.+75_2023.pdf/3352170d-457b-d3bd-2c2a-e38b564fcd21',
    'Risoluzione n. 74 del 20_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_n_74_del_20_12_2023.pdf/6349538f-bd67-27ae-4d76-e38a61a23027',
    'Risoluzione n. 73 del 20_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_n_73_del_20_12_2023.pdf/2367f02b-6a78-f573-4340-5de6eb2e4edc',
    'Risoluzione n. 72 del 20_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_n_72_del_20_12_2023.pdf/a1392731-c089-cef7-5b32-a9fe3770c467',
    'Risoluzione n. 71 del 19_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_n_71_del_19_12_2023.pdf/c2fac128-536e-95a9-0465-18138f289a62',
    'Risoluzione n. 70 del 18_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_n_70_del_18_12_2023.pdf/c25664c8-7fab-b860-67f7-7c71fcd42b71',
    'Risoluzione n. 69 del 13_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_CONS_LAV_FIRENZE13.12.23.pdf/b5ad934b-21f2-c603-850a-fd370436ed39',
    'Risoluzione n. 68 del 7_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RISOLUZIONE+68_2023.pdf/e67feda3-a5c0-64d1-002b-60ad0c7b019b',
    'Risoluzione n. 67 del 6_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/Risoluzione+n.+67+del+6+dicembre+2023.pdf/f3b2830c-2d8d-e4a8-3109-836261f32bd4',
    'Risoluzione n. 66 del 4_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718716/RIS_n_66_del_04_12_2023.pdf/6b01f634-5f72-7fb9-8026-270fd415139e',
    'Risoluzione n. 65 del 28_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/Risoluzione+65+Incorporazione+Campospinoso+Albaredo_B567.pdf/96d10e35-78e4-1c83-afed-e15c045d5910',
    'Risoluzione n. 64 del 24_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/RIS_n_64_del_24_11_2023.pdf/30259e09-ebfa-180d-4587-9813294442f0',
    'Risoluzione n. 63 del 24_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/RIS_n_63_del_24_11_2023.pdf/dbf92aa1-3d82-8138-eb4e-e6cc3bf1bb46',
    'Risoluzione n. 62 del 13_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/Risoluzione_62_2023.pdf/31b3f327-06be-e04a-cd59-75d0556791d7',
    'Risoluzione n. 61 del 10_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/RIS_n_61_del_10_11_2023.pdf/b2774c45-0410-09ab-0102-f40a6d23ccfe',
    'Risoluzione n. 60 del 8_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/RIS_n_60_del_08_11_2023.pdf/151d1a73-d908-b8ed-739a-d86035834beb',
    'Risoluzione n. 59 del 2_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/Risoluzione+cambio+denominazione+Montemagno+Monferrato_F556.pdf/ef7a8a10-6bee-8512-b021-ca6fd329c2ed',
    'Risoluzione n. 58 del 2_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671397/Accessibile-Risoluzione+cambio+denominazione+Popoli+Terme_G878.pdf/297e7a71-4024-39fc-c9fe-55dd8db223a8',
    'Risoluzione n. 57 del 26_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589634/RIS_n_57_del_26_10_2023.pdf/dae38be3-cbcd-d847-24e6-e1e18d84dd42',
    'Risoluzione n. 56 del 16_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589634/Risoluzione+56_2023.pdf/a90e6923-7737-da0e-3ad4-212103ac6691',
    'Risoluzione n. 55 del 3_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5589634/Risoluzione++n.+55+del+3+ottobre+2023+familiari+a+carico+.pdf/e2d7f390-2660-59ca-7dd5-b2cb784215b1',
    'Risoluzione n. 54 del 22_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519472/RIS_n_54_del_22_09_2023_corrige.pdf/524bc482-b1c0-cbbe-ae19-e7b3e234bea9',
    'Risoluzione n. 53 del 22_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519472/RIS_n_53_del_22_09_2023.pdf/76f6e866-b1c8-7334-1fd8-8e42fbf9d3a7',
    'Risoluzione n. 52 del 18_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5519472/RIS_n_52_del_18_09_2023.pdf/bafeadd9-aea1-7cbe-ae7a-e85a9c33787d',
    'Risoluzione n. 51 del 9_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476622/Risoluzione+51+detassazione+lavoro+notturno+9.08.23.pdf/8d2cf4e6-86e2-a9ac-3e11-145ddd8f8bca',
    'Risoluzione n. 50 del 9_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476622/Risoluzione+codici+tributo+criptoattivit%C3%A0+09.08.23.pdf/35aa3956-cfda-7cda-8b24-b3eb01e3c3c5',
    'Risoluzione n. 49 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/Ris.+49+del+31+luglio+2023+.pdf/51fe8d4b-9ab3-340e-b03e-986ff4ba638b',
    'Risoluzione n. 48 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/Risoluzione+48+del+31+luglio+2023.pdf/b456f525-0dd2-cf91-57a1-1ef1d53a1479',
    'Risoluzione n. 47 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/Risoluzione+47+del+31+luglio+2023.pdf/1e975d5a-1105-2307-e4e1-7d0f8d8de66e',
    'Risoluzione n. 46 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/Risoluzione+n.+46+del+31+luglio+2023.pdf/e40909e0-65d5-6c01-bb5c-7b2542b1bf18',
    'Risoluzione n. 45 del 26_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/RIS_n_45_del_26_07_2023.pdf/18d839c2-28e2-3913-10a2-8064778b612d',
    'Risoluzione n. 44 del 25_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/Risoluzione+BI+N_44_2023.pdf/4cbc7f5d-43af-b678-e307-90ecf36354c7',
    'Risoluzione n. 43 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/RIS_n_43_del_13_07_2023.pdf/637502da-832e-c249-bfb3-c47b60b8e42a',
    'Risoluzione n. 42 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/RIS_n_42_del_13_07_2023.pdf/68147c4b-1677-9cea-3945-170fd4214cb0',
    'Risoluzione n. 41 del 7_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/RIS_n_41_del_07_07_2023.pdf/a32e7412-fb57-78db-d262-ed246cb99760',
    'Risoluzione n. 40 del 7_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/Risoluzione+IVA+agevolata+acquisto+auto+n.+40+del+2023.pdf/07c388a9-5b06-ec76-b3f2-2bb99446a6d1',
    'Risoluzione n. 39 del 5_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409676/RIS_n_39_del_05_07_2023.pdf/835b2094-cae9-e78a-bef7-0bac20b8b501',
    'Risoluzione n. 38 del 30_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/Risoluzione+n.+38+del+30+giugno+2023+Regime+impatriati+sportivi+definitivo.pdf/d10b559c-83f9-934e-2b09-0300f8ef530e',
    'Risoluzione n. 37 del 28_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_37_del_28_06_2023.pdf/a2039bed-63b3-4d73-10ec-940ba52538bf',
    'Risoluzione n. 36 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_36_del_26_06_2023.pdf/675f7a4a-a1ab-1533-16a2-32c31005a0a3',
    'Risoluzione n. 35 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_35_del_26_giugno_2023.pdf/fc6b846d-a9ab-cbba-1f0b-bfb09ef09f93',
    'Risoluzione n. 34 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_34_del_26_06_2023.pdf/0e8d1e62-d8cb-f3ba-9242-9a4b176ddfb8',
    'Risoluzione n. 33 del 23_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_33_del_23_06_2023.pdf/cbeab799-33d4-e045-0402-009924eb9c25',
    'Risoluzione n. 32 del 22_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_32_del+22_06_2023.pdf/35bb3689-d2a3-17d4-7920-291f22d54192',
    'Risoluzione n. 31 del 22_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_31_del_22_06_2023.pdf/ba9ec98b-2be0-4ee8-0afc-9278d5a33d1b',
    'Risoluzione n. 30 del 22_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_30_del_22_06_2023.pdf/3d22822b-a719-0912-3c9c-dbca41b3387a',
    'Risoluzione n. 29 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_29_del_20_06_2023.pdf/87e0e44c-93c2-941d-e160-8e17ea14023e',
    'Risoluzione n. 28 del 19_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/Risoluzione+n+28+del+2023.pdf/a974d1ab-0628-fc83-8e5f-50967a874043',
    'Risoluzione n. 27 del 19_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/Risoluzione+n+27+del+2023.pdf/311f865a-bffe-5223-1601-d9ee1c7ff124',
    'Risoluzione n. 26 del 14_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5361482/RIS_n_26_del_14_06_2023.pdf/e4aa2edd-1571-c5bd-e141-7bbf2cc0bd55',
    'Risoluzione n. 25 del 24_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/RIS_n_25_del_24_05_2023.pdf/5e69813b-e5da-eeaf-d340-54128a406bc4',
    'Risoluzione n. 24 del 24_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/RIS_n_24_del_24_05_2023.pdf/82b44997-d9aa-0d71-6807-cf52728a3eea',
    'Risoluzione n. 23 del 19_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/RIS_n_23_del_19_05_2023.pdf/46bd49ee-df72-67c6-f098-451b3be6f045',
    'Risoluzione n. 22 del 12_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/F392_Montagna+sulla+Strada+del+Vino_BZ.pdf/c888f235-b5ca-3eda-f7a9-074844804042',
    'Risoluzione n. 21 del 10_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/Risoluzione+n.+21_10.05.2023.pdf/fc80faec-e451-2438-77ab-4ad16f52c02b',
    'Risoluzione n. 20 del 10_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/Risoluzione+n.+20_10.05.2023.pdf/d84a0e29-ce8a-512f-79fe-18fb2f9da395',
    'Risoluzione n. 19 del 2_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256664/RIS_n_19_del_02_05_2023.pdf/3f9991d7-ab8f-c5cf-c537-aaafe1ed7b81',
    'Risoluzione n. 18 del 28_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187530/RIS_n_18_del_28_04_2023.pdf/96110a7f-16ef-2056-4cdb-d3e88d7edab2',
    'Risoluzione n. 17 del 6_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187530/RIS_n_17_del_06_04_2023.pdf/9ab08950-8f46-a0be-a422-638e714523e3',
    'Risoluzione n. 16 del 17_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081196/RIS_n_16_del_17_03_2023.pdf/c67e3439-99bb-d62c-35d6-c537f205150a',
    'Risoluzione n. 15 del 14_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081196/RIS_n_15_del_14_03_2023.pdf/0a407490-0aee-0396-d879-60fbf0043034',
    'Risoluzione n. 14 del 6_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081196/RIS_n_14_del_06_03_2023.pdf/a4f232f9-997e-f973-65aa-0ef54f24f772',
    'Risoluzione n. 13 del 2_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081196/RIS_n_13_del_02_03_2023.pdf/0fbde8e4-4eeb-e67e-75fd-3379186fdf15',
    'Risoluzione n. 12 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081196/Risoluzione_12_2023.pdf/15aebc06-8e7b-b4e3-d047-f0c3fdaac816',
    'Risoluzione n. 11 del 24_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/RIS_n_11_del_24_02_2023.pdf/d3b2fc68-4d44-b647-dd8f-d6aeaa2e7955',
    'Risoluzione n. 10 del 24_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/RIS_n_10_del_24_02_2023.pdf/f3d4b61b-7651-4f17-a52f-f5127f99ec03',
    'Risoluzione n. 9 del 20_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/RIS_n_09_del_20_02_2023.pdf/f50d5c9c-17ca-fa9d-2a29-0c4aece3b012',
    'Risoluzione n. 8 del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/RIS_n_08_del_14_02_2023.pdf/9eb9f8b1-ea89-6443-88f9-e367e921ddfd',
    'Risoluzione n. 7 del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/Ris_n_7_del_14_02_2023.pdf/b51a082f-bc99-1ed3-ccbe-dd1d4a670995',
    'Risoluzione n. 6 del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/RIS_n_6_del_14_02_2023.pdf/410e9c91-6fa2-0b2c-851f-571560ae3dde',
    'Risoluzione n. 5 del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/Risoluzione+registrazione+atti+soggetti+esteri+privi+di+CF+pub.pdf/6995eec2-66a1-0b6c-0361-296ed2d0a3a1',
    'Risoluzione n. 4 del 6_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/Risoluzione+4+del+6+febbraio+2023.pdf/d8493c76-94ce-f2d0-531b-c63c093c582f',
    'Risoluzione n. 3 del 3_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988606/Risoluzione+sale+and+lease+back.pdf/eda61b99-c82b-be73-7d40-0f57f7e2c0bc',
    'Risoluzione n. 2 del 30_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913751/RIS_n_02_del_30_01_2023.pdf/1d1d4d54-28fd-c3e8-2b4d-2983185e7fe3',
    'Risoluzione n. 1 del 5_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913751/Risoluzione+Istituzione+Comune+Moransengo+-+Accessibile_.pdf/055fcc03-c33a-2d90-4432-62fa94ce723a',
    'Risoluzione n. 48 del 19_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390991/RIS_n_48_del_19_09_2024.pdf/6585bf03-7065-fea6-2bf2-b0af49c464db',
    'Risoluzione n. 47 del 19_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390991/risoluzione+n.+47+del+19+settembre+2024.pdf/f19aa4ae-a777-2c41-b33c-940db5969945',
    'Risoluzione n. 46 del 18_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390991/RIS_n_46_del_18_09_2024.pdf/4072fedf-d41b-9e82-41a9-8989a2062d2e',
    'Risoluzione n. 45 del 2_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390991/Risoluzione+45+del+2.9.2024.pdf/0b232a4b-051b-8658-7699-c6d240147f48',
    'Risoluzione n. 44 del 2_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314635/RIS_n_44_del_02_08_2024.pdf/c31fe1e0-591c-c22f-43cd-fbd6486ca3ae',
    'Risoluzione n. 43 del 30_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241346/RIS_n_43_del_30_07_2024.pdf/709334a9-ee0a-a617-d257-70fbd777583d',
    'Risoluzione n. 42 del 30_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241346/RIS_n_42_del_30_07_2024.pdf/ced2cc8d-cd18-7023-174a-8ac38d660534',
    'Risoluzione n. 41 del 24_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241346/RIS_n_41_del_24_07_2024.pdf/32802121-2e00-c7f8-881b-1fc63213ac40',
    'Risoluzione n. 40 del 23_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241346/Risoluzione+%281%29.pdf/f8dc495d-fcb1-5afc-bb35-86b2a33197f9',
    'Risposta n. 487 del 29_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+487_2023.pdf/b1fc514f-144a-86b2-1c41-f6ac1c4b3a1b',
    'Risposta n. 486 del 29_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+486_2023.pdf/ca9bbe10-37ca-2420-8159-391d694bf7ea',
    'Risposta n. 485 del 29_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+485_2023.pdf/9a4b49e7-cc76-d11e-9b05-4b055a0ea555',
    'Risposta n. 484 del 29_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+484_2023.pdf/19cad2f5-3851-910f-0b76-7fbe2a34b901',
    'Risposta n. 483 del 29_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+483_2023.pdf/cc08ed93-6f7e-3220-f5f7-5a24cb9de959',
    'Risposta n. 482 del 22_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+482_2023.pdf/9b0d6ba2-46c3-75de-f44e-0a188e6acc2a',
    'Risposta n. 481 del 22_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+481_2023.pdf/679b22d6-1c8b-e375-118c-eef3b89a8054',
    'Risposta n. 480 del 22_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+480_2023.pdf/d41117f0-a0e9-dd5a-f8ab-102f6443bdbf',
    'Risposta n. 479 del 18_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+479_2023.pdf/af99c16f-e2c6-4e03-6796-c18d45e1dbba',
    'Risposta n. 478 del 18_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+478_2023.pdf/051e5783-1348-4b0a-5ef9-0122a989456c',
    'Risposta n. 477 del 15_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+477_2023.pdf/7f652a7a-190d-cdc8-74dd-38da963ccb43',
    'Risposta n. 476 del 15_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+476_2023.pdf/f850578d-6f92-8e4f-22c5-3437a5a9fe51',
    'Risposta n. 475 del 11_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+475_2023.pdf/971bb065-61ed-ed75-767a-c94bc1d14f45',
    'Risposta n. 474 del 11_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+474_2023.pdf/e3799884-555b-191e-f95d-d0138cc9a8dd',
    'Risposta n. 473 del 11_12_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5718720/Risposta+n.+473_2023.pdf/f05e9d05-6ff2-3e31-ecc0-63e6cb71a680',
    'Risposta n. 472 del 30_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+472_2023.pdf/84a2bb04-4bd8-ab1d-68f3-6cf3529422bd',
    'Risposta n. 471 del 29_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+471_2023.pdf/d3825426-35d3-10b1-dd71-0040557cfbee',
    'Risposta n. 470 del 29_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+470_2023.pdf/e18ee728-96ca-f3ec-31b8-6731ab653e32',
    'Risposta n. 469 del 28_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+469_2023.pdf/11cccb3a-6a15-8dc9-096c-8474969404c6',
    'Risposta n. 468 del 28_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+468_2023.pdf/15e4ebee-eeb9-608d-626d-ed1c36ac629a',
    'Risposta n. 467 del 24_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+467_2023.pdf/3f0bf850-2e14-e3c5-985e-dcc1d4960128',
    'Risposta n. 466 del 23_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+466_2023.pdf/960a1346-f7b1-6c0b-c28c-8aad737eb8cb',
    'Risposta n. 465 del 21_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+465_2023.pdf/aae9b0fd-735d-9ce6-d4ce-4f70ddbfffc5',
    'Risposta n. 464 del 21_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+464_2023.pdf/737e4bcf-3fc4-b9f6-0997-a80b44685771',
    'Risposta n. 463 del 16_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+463_2023.pdf/c1e77ec5-6aac-c2f8-8a2f-5f0659de86cb',
    'Risposta n. 462 del 15_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+462_2023.pdf/3dcd2f60-d3a2-4e6e-3b26-f83dd4c20898',
    'Risposta n. 461 del 14_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+461_2023.pdf/4716c2a8-46bc-943f-076d-1e4dfe4336af',
    'Risposta n. 460 del 13_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+460_2023.pdf/9fdc9cbd-e2ee-51bb-0e01-81680d2d22cf',
    'Risposta n. 459 del 10_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+459_2023.pdf/3867af17-d850-7672-2eb0-925733585f4a',
    'Risposta n. 458 del 10_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+458_2023.pdf/e6f59885-2e2d-35da-7e65-632c75f48766',
    'Risposta n. 457 del 10_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+457_2023.pdf/367ebfde-6e34-4df7-cc3b-a399d9cf03bd',
    'Risposta n. 456 del 10_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+456_2023.pdf/47348f14-bdff-0831-0eba-3fd673b8b091',
    'Risposta n. 455 del 8_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+455_2023.pdf/53e63ee4-a3e8-5c0d-ec86-fd0449dd6946',
    'Risposta n. 454 del 7_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+454_2023.pdf/eacde63e-edba-0f26-99cd-648f4272e6aa',
    'Risposta n. 453 del 6_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5671381/Risposta+n.+453_2023.pdf/f68f13e9-e8e4-f6d1-b95a-dff26687656f',
    'Risposta n. 452 del 2_11_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913739/Risposta+n.+452_2023.pdf/6468640f-0e09-4168-0161-033b8ebe71c9',
    'Risposta n. 451 del 27_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+451_2023.pdf/d168b649-777b-c0a9-aa02-3393dad8d39f',
    'Risposta n. 450 del 20_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+450_2023.pdf/ce44c21a-a012-1dc9-17bf-46983c91b685',
    'Risposta n. 449 del 20_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+449_2023.pdf/b46a9e5a-0fd5-cfed-cf6b-5fd4dd72a62f',
    'Risposta n. 448 del 18_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+448_2023.pdf/402b7fb5-1ef9-3673-945c-d73056c1b940',
    'Risposta n. 447 del 13_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+447_2023.pdf/6ab21ea9-fc29-d983-da1d-5a56e1691166',
    'Risposta n. 446 del 9_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+446_2023.pdf/f462fd75-d94f-d81b-618d-deb8ce9bd374',
    'Risposta n. 445 del 9_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5612116/Risposta+n.+445_2023.pdf/a2e9a7e7-430f-0c52-27db-74e4c0f9f67a',
    'Risposta n. 444 del 2_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+444_2023.pdf/803cddc7-32bb-129d-7e03-cb040dd06b9d',
    'Risposta n. 443 del 2_10_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+443_2023.pdf/9244b04e-ef06-3aa9-258c-0ce1820e6d8e',
    'Risposta n. 442 del 29_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+442_2023.pdf/848a51ff-a012-346f-105c-79dc4d3eb9ea',
    'Risposta n. 441 del 29_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+441_2023.pdf/d6e5739e-8678-7ada-7cf6-97c631524d82',
    'Risposta n. 440 del 28_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+440_2023.pdf/4911f38d-8aa3-ca1c-d13d-dfbbe42f6631',
    'Risposta n. 439 del 28_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+439_2023.pdf/1663bbec-ad37-5207-4b67-0c88a3878afa',
    'Risposta n. 438 del 28_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+438_2023.pdf/aab06190-c456-8835-2706-8cdd54007eae',
    'Risposta n. 437 del 26_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+437_2023.pdf/fc493a76-7fb3-9929-12a4-22c77b85434e',
    'Risposta n. 436 del 26_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+436_2023.pdf/5a40d8ce-2d2b-f19e-a534-7337c416912b',
    'Risposta n. 435 del 26_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+435_2023.pdf/12e0427a-8f20-b1dc-94a6-18435b0da4b8',
    'Risposta n. 434 del 26_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+434_2023.pdf/61e1a5c0-2153-ad0a-7604-9744f87daa4b',
    'Risposta n. 433 del 20_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+433_2023.pdf/5eb0721c-227f-9284-a2b3-4390be07bf78',
    'Risposta n. 432 del 19_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+432_2023.pdf/1ddc8de9-f08f-e9e2-e8ce-65184f9e3f70',
    'Risposta n. 431 del 18_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+431_2023.pdf/a11a9fd2-b0f4-0f5d-a0cc-75ff4f8c555e',
    'Risposta n. 430 del 18_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+430_2023.pdf/d84501f6-462e-cd9c-12d6-2052730ff1af',
    'Risposta n. 429 del 18_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+429_2023.pdf/1853720a-d151-e570-682d-87fddff41cd0',
    'Risposta n. 428 del 12_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+428_2023.pdf/112f4168-3238-b26c-ee09-df0979176d15',
    'Risposta n. 427 del 11_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+427_2023.pdf/e9a2ced1-438d-8b64-6522-f1db4af0d7c3',
    'Risposta n. 426 del 11_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+426_2023.pdf/54cc823c-16fb-f512-0204-a6dd2c513856',
    'Risposta n. 425 del 8_09_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5521452/Risposta+n.+425_2023.pdf/8d1ecc7b-571c-4d39-5da9-775721fc652c',
    'Risposta n. 424 del 31_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+424_2023.pdf/32e06a96-3b1a-e5ad-6b09-d61d10449444',
    'Risposta n. 423 del 30_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+423_2023.pdf/215dba12-93cf-c526-837c-a8fac31fa174',
    'Risposta n. 422 del 30_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+422_2023.pdf/3b057998-bc12-d733-dac2-354cabce1555',
    'Risposta n. 421 del 25_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+421_2023.pdf/bda96fa6-1db0-14e4-0379-897c2a396012',
    'Risposta n. 420 del 25_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+420_2023.pdf/6a8e82f5-a586-7702-2e93-8839e10a7e16',
    'Risposta n. 419 del 25_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+419_2023.pdf/302bea5f-c931-9bf9-8e78-f3d26a357bd5',
    'Risposta n. 418 del 16_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+418_2023.pdf/2131958a-8b97-680c-69a8-c0d0f7282e2f',
    'Risposta n. 417 del 4_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+417_2023.pdf/16780c63-2974-18ae-be4e-027f11868b9f',
    'Risposta n. 416 del 4_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+416_2023.pdf/2598b379-68b6-3878-000f-901d3d8a8a25',
    'Risposta n. 415 del 3_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+415_2023.pdf/3998503a-d64a-a215-ae07-81a4fa780c5d',
    'Risposta n. 414 del 3_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+414_2023.pdf/768d9388-0611-cdaf-82ed-a2d4df61a897',
    'Risposta n. 413 del 3_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+413_2023.pdf/c1aff229-9e96-6fb4-0278-f1d6d9f372a6',
    'Risposta n. 412 del 2_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+412_2023.pdf/e85ca171-da27-7ab3-7aa2-4ac3c4436c9f',
    'Risposta n. 411 del 2_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+411_2023.pdf/d5954818-71fe-6458-8368-fd096ff93b19',
    'Risposta n. 410 del 1_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+410_2023.pdf/58571221-9ec2-71f6-3203-3b01dd61bc51',
    'Risposta n. 409 del 1_08_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5476626/Risposta+n.+409_2023.pdf/a54dd253-32d5-922d-d3c5-3793348dd8ae',
    'Risposta n. 408 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+408_2023.pdf/279fbc8e-fce9-9dc5-665e-f778e7b770f5',
    'Risposta n. 407 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+407_2023.pdf/b0966aa5-6602-3465-89c2-1dbdefebcf66',
    'Risposta n. 406 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+406_2023.pdf/1a8a1be6-1781-0fe8-28e1-e43c049ddce9',
    'Risposta n. 405 del 31_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+405_2023.pdf/b9d5820b-ffdd-8a20-d2f7-bd6d6d1478c3',
    'Risposta n. 404 del 28_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+404_2023.pdf/57c9ebaa-52c9-f8c9-37c3-306af78e759a',
    'Risposta n. 403 del 28_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+403_2023.pdf/0e10b795-ff5e-a886-2376-ba598d2a945a',
    'Risposta n. 402 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+402_2023.pdf/a40762a3-8bed-411e-c958-0b7c8f236c3d',
    'Risposta n. 401 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+401_2023.pdf/f07747d9-c165-b52e-31f8-aa1810cbb9ae',
    'Risposta n. 400 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+400_2023.pdf/68e206c4-fd0b-c807-cca1-c81f95599130',
    'Risposta n. 399 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+399_2023.pdf/ca84a971-04c8-2dbf-f01c-d918ad1dd8a8',
    'Risposta n. 398 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+398_2023.pdf/999d6020-9227-6d0d-ec21-51f5ac4e1b10',
    'Risposta n. 397 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+397_2023.pdf/17af03b6-4645-f5db-f7cb-f5dd91b0515e',
    'Risposta n. 396 del 27_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+396_2023.pdf/2deeb688-1014-a119-20fb-9d4cb59cb620',
    'Risposta n. 395 del 25_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+395_2023.pdf/0796eeec-be0a-f447-8622-706849f94494',
    'Risposta n. 394 del 25_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+394_2023.pdf/d8754f2d-f079-d23c-e806-b76fb34d86c0',
    'Risposta n. 393 del 25_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+393_2023.pdf/5e7e677d-6f0e-df2f-0ab4-53839be9359d',
    'Risposta n. 392 del 24_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+392_2023.pdf/ad227bbe-3e92-d728-13ff-95c5da29c288',
    'Risposta n. 391 del 19_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+391_2023.pdf/d13c534d-b9a8-16a4-6d0f-93acaff90bae',
    'Risposta n. 390 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+390_2023.pdf/e5cb0f5f-aa63-4af0-57fa-ab5341165cae',
    'Risposta n. 389 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+389_2023.pdf/0af34968-01c8-4f13-4151-e3d034dbcee7',
    'Risposta n. 388 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+388_2023.pdf/1e2839b0-2d40-91a5-a1f2-91585406f7b2',
    'Risposta n. 387 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+387_2023.pdf/2d398668-821b-2830-0f18-0fa3aa1edaad',
    'Risposta n. 386 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+386_2023.pdf/a0d046d8-5766-8bfc-a59b-1672d3f68a28',
    'Risposta n. 385 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+385_2023.pdf/c9feffc0-8819-7775-79a3-f415fe4c56a8',
    'Risposta n. 384 del 13_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+384_2023.pdf/8117df9e-d95b-c2b1-3db7-e2ea87ede602',
    'Risposta n. 383 del 12_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+383_2023.pdf/e36b7744-346b-7bc1-5d89-c3f904e9413f',
    'Risposta n. 382 del 12_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+382_2023.pdf/16b9f46f-040d-3ef4-c324-9b9f19c0aef9',
    'Risposta n. 381 del 12_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+381_2023.pdf/445a0a5e-0135-2aba-ff5b-587a776abff0',
    'Risposta n. 380 del 11_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+380_2023.pdf/356fc7c4-26d8-dd15-984d-15ee567bf4ea',
    'Risposta n. 379 del 11_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+379_2023.pdf/e765dd12-4c5f-de5a-a0bd-05537fc46873',
    'Risposta n. 378 del 11_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+378_2023.pdf/73f05928-d998-fcfc-f3a9-7d6102789e00',
    'Risposta n. 377 del 10_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+377_2023.pdf/69ba15e9-efd2-dfb9-752f-5b20158983e6',
    'Risposta n. 376 del 10_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+376_2023.pdf/39198c73-47da-abeb-563f-40f0e5e87c9d',
    'Risposta n. 375 del 10_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+375_2023.pdf/d7e86b72-ad04-6eef-d3e0-6f8b4bb910c0',
    'Risposta n. 374 del 10_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+374_2023.pdf/43cd4fec-68f4-f77e-6874-6970eb79ebc0',
    'Risposta n. 373 del 10_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.373bis.pdf/3bb7cedf-b96e-a530-6169-b378a55750db',
    'Risposta n. 372 del 7_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+372_2023.pdf/e290c2dd-e628-dc6a-59ec-869aff6c5d8c',
    'Risposta n. 371 del 7_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+371_2023.pdf/c6d41811-ee80-ef15-460f-7753e94d62a0',
    'Risposta n. 370 del 4_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+370_2023.pdf/9cb2326f-5f9f-7190-4ede-e648dd27a3a7',
    'Risposta n. 369 del 4_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+369_2023.pdf/f540a55b-536d-765b-d51b-4281b57717a7',
    'Risposta n. 368 del 4_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+368_2023.pdf/9fae9c13-0f88-a108-b739-46fda04509e0',
    'Risposta n. 367 del 4_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+367_2023.pdf/4a2c4e18-4c2a-db9b-d085-15ae2ae80749',
    'Risposta n. 366 del 4_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+366_2023.pdf/4012830c-dcf7-1852-0765-2432aea1020b',
    'Risposta n. 365 del 3_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5409668/Risposta+n.+365_2023.pdf/51a13789-50a5-69a0-5c51-226ed011fa94',
    'Risposta n. 364 del 30_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+364_2023.pdf/b65b2bbe-80ba-c0b4-6d47-f04b41a8d134',
    'Risposta n. 363 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+363_2023.pdf/0bea96d3-0d70-fe0f-b861-f3e541e3c850',
    'Risposta n. 362 del 26_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+362_2023.pdf/bede7fa5-099e-e02a-09a2-710e0c2275b2',
    'Risposta n. 361 del 23_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+3612023+all%27interpello.pdf/ab232a5b-8770-b1a7-faf0-9b9dd6cf9dce',
    'Risposta n. 360 del 23_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+3602023+all%27interpello.pdf/a74caa41-cd6a-e72d-b96f-99fa376f9d68',
    'Risposta n. 359 del 23_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+3592023+all%27interpello.pdf/a11f4c56-267c-b4a7-cdc6-dbd1c665faa3',
    'Risposta n. 358 del 23_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+358_2023.pdf/66e02d5b-1ef4-ce23-2ad5-10cbee5cceef',
    'Risposta n. 357 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+357_2023.pdf/3c702ace-37b3-a5e0-f715-8e5ee19fc0aa',
    'Risposta n. 356 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+356_2023.pdf/202ec2b0-e572-2063-8f91-1108ab1ad7f6',
    'Risposta n. 355 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+355_2023.pdf/63503014-fada-31e3-b485-1b9bb3362364',
    'Risposta n. 354 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+354_2023.pdf/949d3646-1d41-baea-049a-53ba09ba838b',
    'Risposta n. 353 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+353_2023.pdf/b5e7265e-971f-06fc-344a-f1221bc7edd6',
    'Risposta n. 352 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+352_2023.pdf/3266dab2-7fc5-8f46-4636-64b9c6977b7b',
    'Risposta n. 351 del 20_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+351_2023.pdf/95d5c0d6-1a29-cb74-e708-887a14ee3191',
    'Risposta n. 350 del 19_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+3502023+all%27interpello.pdf/64121f43-7c67-4c7a-7714-3423f5f360ff',
    'Risposta n. 349 del 19_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+349_2023.pdf/0bcf11fe-204b-55ad-3d3b-e45c7a553ffb',
    'Risposta n. 348 del 14_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+348_2023.pdf/e8f361c6-48c2-769b-6dd9-a10720da899d',
    'Risposta n. 347 del 14_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+347_2023.pdf/07d3c9cc-cc56-e826-5ee1-b7c0d965eb4b',
    'Risposta n. 346 del 14_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+346_2023.pdf/fb34f177-9b76-a1f0-1a26-300e1f04b5b4',
    'Risposta n. 345 del 13_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+345_2023.pdf/6514dcaf-17a4-abf1-0d5f-610fc9b1a50c',
    'Risposta n. 344 del 6_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/RISPOSTA+344_2023.pdf/33c3fcc1-0ac8-0650-278a-64328f04b885',
    'Risposta n. 343 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+343_2023.pdf/d3070ca5-6a11-6eff-f1e0-10b9119a1b5f',
    'Risposta n. 342 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+342_2023.pdf/4adab7a6-1f36-adcc-e80a-b73b6c1736e0',
    'Risposta n. 341 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+341_2023.pdf/288fa3ca-02ce-8957-407c-e5903715502d',
    'Risposta n. 340 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+340_2023.pdf/7e66c063-54f4-ffea-a1da-6718444fdd17',
    'Risposta n. 339 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+339_2023.pdf/6a187c6e-f899-59ec-b59b-8deac64549db',
    'Risposta n. 338 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+338_2023.pdf/17661035-8902-764d-275c-0d25ebcd2c48',
    'Risposta n. 337 del 5_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+337_2023.pdf/4f12e998-2f5d-8f52-41fe-f744760a9c68',
    'Risposta n. 336 del 1_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+336_2023.pdf/365a78f8-14b5-22de-88ed-b6cbf6bda206',
    'Risposta n. 335 del 1_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+335_2023.pdf/c6d31174-f4cc-380e-2392-3aed14648c52',
    'Risposta n. 334 del 1_06_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5329468/Risposta+n.+334_2023.pdf/2bf60326-660b-2d71-7d4e-5c77881823bd',
    'Risposta n. 333 del 4_07_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+333_2023.pdf/42e8465b-2d81-38b6-da3b-ecb8bf3bc2bc',
    'Risposta n. 332 del 29_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+332_2023.pdf/4909f60c-42ac-336b-c5cb-114ddd9943ce',
    'Risposta n. 331 del 24_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+331_2023.pdf/1e01a56b-be03-95e5-126e-bf0252c1cf44',
    'Risposta n. 330 del 22_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+330_2023.pdf/d9f12bb0-3bce-e8ad-2697-775f0953dd03',
    'Risposta n. 329 del 15_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+329_2023.pdf/29b5723e-3eba-aa32-5545-101ede6e8697',
    'Risposta n. 328 del 15_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+328_2023.pdf/22d5bf1d-b992-1d90-a4f3-ca7eb1c38c9c',
    'Risposta n. 327 del 10_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+327_2023.pdf/20d30738-ddf0-dee5-381d-88026f22aac1',
    'Risposta n. 326 del 10_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+326_2023.pdf/02585c37-a0e6-bf12-53e7-1eed3f7ae39e',
    'Risposta n. 325 del 9_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+325_2023.pdf/819ccd25-1dbe-218a-4a1f-1e12ba63d58a',
    'Risposta n. 324 del 9_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+324_2023.pdf/f21a4c54-c98c-2379-e27c-9eb1ac0d9776',
    'Risposta n. 323 del 9_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+323_2023.pdf/d0b85493-d2f0-21e2-4482-9b65b12a20fd',
    'Risposta n. 322 del 9_05_2023.pdf':'https://www.agenziaentrate.gov.it/',
    'Risposta n. 321 del 9_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+321_2023.pdf/1cb1e99d-2982-7657-79ab-cff464d14d16',
    'Risposta n. 320 del 9_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+320_2023.pdf/db2bb7fc-2293-44f2-da8b-ae9816cc92ba',
    'Risposta n. 319 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+319_2023.pdf/7e1d9376-e4a6-c72c-4474-2f0ebb2b1bd4',
    'Risposta n. 318 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+318_2023.pdf/0832af59-3183-4200-d216-1934b44d1d55',
    'Risposta n. 317 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+317_2023.pdf/c32d0057-af0e-5bad-a4d6-95eb0e65c51f',
    'Risposta n. 316 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+316_2023.pdf/afeb00bf-64a4-0443-7fb6-087a17cdbf76',
    'Risposta n. 315 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+315_2023.pdf/816b9fa3-2fcd-4c60-8a36-24f2c44fcf65',
    'Risposta n. 314 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+314_2023.pdf/f8cef47b-f6e1-00ff-473d-daf898deaf9e',
    'Risposta n. 313 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+313_2023.pdf/13478dce-425d-5d54-7269-de5be0075385',
    'Risposta n. 312 del 8_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+312_2023.pdf/ed101697-83d2-734b-1ab7-0eed5b3b2e0f',
    'Risposta n. 311 del 3_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+311_2023.pdf/97213b57-0e85-402e-3f27-417dd82ad182',
    'Risposta n. 310 del 3_05_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5256668/Risposta+n.+310_2023.pdf/2ca8027e-616b-ed7a-1cdf-f313abf7f24e',
    'Risposta n. 309 del 28_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+309_2023.pdf/1ba770bb-e30e-6503-09ac-d7501771a333',
    'Risposta n. 308 del 28_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+308_2023.pdf/60acd2d4-930e-71dd-dfe5-8ce8616f61b8',
    'Risposta n. 307 del 27_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+307_2023.pdf/89ec6b94-f60d-371b-cd34-052d11687201',
    'Risposta n. 306 del 24_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+306_2023.pdf/93fef520-f58d-5f99-f3bd-b7a514ab1850',
    'Risposta n. 305 del 24_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+305_2023.pdf/b4ddc3ee-e458-4cfd-a571-a7af299681e4',
    'Risposta n. 304 del 24_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+304_2023.pdf/b6987ccd-5d42-6b4f-e85a-5d4273f655d2',
    'Risposta n. 303 del 21_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+303_2023.pdf/728ca907-bcd4-faff-6381-a62969a6c826',
    'Risposta n. 302 del 21_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+302_2023.pdf/4a11584b-54ff-c2db-a04d-8b7ae1a6f7ce',
    'Risposta n. 301 del 21_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+301_2023.pdf/76029b7e-9156-0a3a-0fa3-5d7714e965f9',
    'Risposta n. 300 del 21_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+300_2023.pdf/7909ca15-7bdc-9ded-7894-4cd7c5519ff2',
    'Risposta n. 299 del 19_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+299_2023.pdf/1cfc4cc3-995d-f288-e5e8-aeaa7441beb4',
    'Risposta n. 298 del 19_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+298_2023.pdf/c7557e01-4b42-b0be-8b07-5583319dc957',
    'Risposta n. 297 del 18_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+297_2023.pdf/1b640e8d-038e-43f3-d180-e08f9a78b883',
    'Risposta n. 296 del 14_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+296_2023.pdf/1e3241c4-6c9e-c68d-658c-3ae88779a083',
    'Risposta n. 295 del 14_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+295_2023.pdf/42a3b697-cfe6-3c1e-5c9b-36f841f93fac',
    'Risposta n. 294 del 14_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+294_2023.pdf/e1a3b846-436d-2928-205f-084d1cdbb9bd',
    'Risposta n. 293 del 14_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+293_2023.pdf/2b90b728-345f-76d5-262a-60287c499b94',
    'Risposta n. 292 del 11_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+292_2023_1.pdf/00169303-afa5-1c06-04dc-3c17143b150a',
    'Risposta n. 291 del 11_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+291_2023.pdf/da2a8da7-af5e-1f07-16df-8fd170a6838c',
    'Risposta n. 290 del 11_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+290_2023.pdf/4cf6adb8-1a56-ff61-7edf-fd80e6ca9eb0',
    'Risposta n. 289 del 11_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+289_2023.pdf/82e63f09-dcbd-c7e9-b6f7-838ff5d2ee2b',
    'Risposta n. 288 del 7_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+288_2023.pdf/b6625ab2-a769-5df9-ae91-18ef74c8b7fc',
    'Risposta n. 287 del 7_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+287_2023.pdf/fc8ac6eb-d62f-0017-6633-13f5cac7c0c8',
    'Risposta n. 286 del 6_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+286_2023.pdf/6c99e774-ca31-3dab-bd40-db4f3bdf3874',
    'Risposta n. 285 del 6_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+285_2023.pdf/ddab137e-a4ee-b6f1-16d2-c10e5a8c52fe',
    'Risposta n. 284 del 5_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+284_2023.pdf/66551d18-0d0b-e852-e1fd-93d31e3481d7',
    'Risposta n. 283 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+283_2023.pdf/a2e3fd23-dff0-a1d2-cec1-05064f9e2824',
    'Risposta n. 282 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+282_2023.pdf/c57bad74-31ed-5ceb-21fd-6c16dfd1f1fb',
    'Risposta n. 281 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+281_2023.pdf/27ea725b-55e9-e744-7ebc-ec8777eb08a4',
    'Risposta n. 280 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+280_2023.pdf/a4cb52c7-1bca-9575-8365-6f82c714e1e1',
    'Risposta n. 279 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+279_2023.pdf/98ca7464-e068-0471-5f90-8c731df182fd',
    'Risposta n. 278 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+278_2023.pdf/275cfcf0-84b3-9070-5d8c-d305995cb20f',
    'Risposta n. 277 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+277_2023.pdf/629ae346-40ba-d383-26ed-674a66f4f575',
    'Risposta n. 276 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+276_2023.pdf/69e9332c-fec2-b508-e0e1-86c1b87eb897',
    'Risposta n. 275 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+275_2023.pdf/2b747423-eed2-199b-f83f-ba94799c2e51',
    'Risposta n. 274 del 4_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+274_2023.pdf/cd44c3c1-4edd-43a1-7597-417f5f672681',
    'Risposta n. 273 del 3_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+273_2023.pdf/ba8f677d-3c50-5458-ef0d-1972cd9a913f',
    'Risposta n. 272 del 3_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+272_2023.pdf/16a6e94f-c243-3345-1887-c66de02ed9c6',
    'Risposta n. 271 del 3_04_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5187534/Risposta+n.+271_2023.pdf/2e0d99b9-105c-99ca-d7fc-60284f891c25',
    'Risposta n. 270 del 31_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+270_2023.pdf/a4c29711-f023-3d84-046b-3a2cb6871df4',
    'Risposta n. 269 del 30_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+269_2023.pdf/fdf9d969-52d2-892b-0d96-ca4d2b1872c0',
    'Risposta n. 268 del 29_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+268_2023.pdf/3fa0328c-a723-f8f1-fd39-2ccadbfc4191',
    'Risposta n. 267 del 27_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+267_2023.pdf/868c9fae-2160-7957-a4ce-46a9136d7bab',
    'Risposta n. 266 del 22_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+266_2023.pdf/0431a013-ca8d-1db1-e473-f9fc511829dd',
    'Risposta n. 265 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+265_2023.pdf/18081bc5-2afe-3942-3e2f-19d1f6ad4c27',
    'Risposta n. 264 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+264_2023.pdf/f86f5ae6-7e7d-1780-3ad2-5a6c48a86432',
    'Risposta n. 263 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+263_2023.pdf/10b4b235-2055-b1e5-f066-0fb2f09be392',
    'Risposta n. 262 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+262_2023.pdf/7c3b080c-46f7-8d49-38ad-babbad75d1f1',
    'Risposta n. 261 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+261_2023.pdf/a4daa2a0-4862-6c18-f0ee-56edaa0b3f1d',
    'Risposta n. 260 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+260_2023.pdf/f1a57df8-e1fe-b5ac-d9d5-43e2b7a94db2',
    'Risposta n. 259 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+259_2023.pdf/d3bb5dfa-5e8f-d147-79c0-093a6b51c8fa',
    'Risposta n. 258 del 21_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+258_2023.pdf/9be89047-84cd-afed-8163-7c494d726119',
    'Risposta n. 257 del 20_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+257_2023.pdf/4ef98845-6ad9-a0ec-51ba-b5ff42b78063',
    'Risposta n. 256 del 17_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+2562023+all%27interpello.pdf/eddf0495-b440-4adc-1627-f6aa6f9aaf90',
    'Risposta n. 255 del 17_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+255_2023.pdf/25aa15f7-d918-ac90-8b6d-59c29f0bd6c4',
    'Risposta n. 254 del 17_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+254_2023.pdf/d466806e-f957-a0be-6adc-987f1c441b96',
    'Risposta n. 253 del 17_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+253_2023.pdf/57c95dcd-229d-a7f4-5f78-4055686b96eb',
    'Risposta n. 252 del 17_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+252_2023.pdf/1ab3b84a-2796-68a2-1cd0-0f9f4912079f',
    'Risposta n. 251 del 16_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+251_2023+%281%29.pdf/9472275c-72d0-4829-db1c-d502fbbcfe84',
    'Risposta n. 250 del 16_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+250_2023.pdf/12fb03b2-dae8-b1ff-4e86-9e3cc0fccd5d',
    'Risposta n. 249 del 13_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+249_2023.pdf/dc3786ad-817b-ab1f-f6b4-aa302b53027c',
    'Risposta n. 248 del 13_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+248_2023.pdf/1c8eedf6-5ea6-c130-3d88-26bb539b16d2',
    'Risposta n. 247 del 8_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+247_2023.pdf/025d1b3d-bfd4-5201-ee9d-1ec3df3461bb',
    'Risposta n. 246 del 8_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+246_2023.pdf/73353de3-ef29-7a53-81db-1d454895b40b',
    'Risposta n. 245 del 8_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+245_2023.pdf/51664ac6-2f06-25e7-0e62-36fb78b230c9',
    'Risposta n. 244 del 8_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+244_2023.pdf/0785d440-0d9e-df19-d587-a1b717e1afa2',
    'Risposta n. 243 del 7_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+243_2023.pdf/d806f427-0a3e-bf24-082c-956145d5bcd1',
    'Risposta n. 242 del 6_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+242_2023.pdf/a5043091-d3e7-01e9-49ed-f3c88325bd22',
    'Risposta n. 241 del 6_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+241_2023.pdf/8b70a925-32c6-bc05-2a9d-bc5d283194ff',
    'Risposta n. 240 del 6_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+240_2023.pdf/2b9930d1-6350-0178-da80-b39fc6516851',
    'Risposta n. 239 del 6_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+239_2023.pdf/8e90aeaa-35ac-2618-2e72-b1a9a78fb41b',
    'Risposta n. 238 del 3_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+238_2023.pdf/d53f2a63-3dc1-9227-6c1c-99e87b3df731',
    'Risposta n. 237 del 2_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+237_2023.pdf/2678bd06-014d-6a45-3a2c-01d3395009c0',
    'Risposta n. 236 del 2_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+236_2023.pdf/51683a23-75fb-a595-405b-94e8a724dd54',
    'Risposta n. 235 del 2_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+235_2023+%281%29.pdf/49d03d3f-8d08-31c8-d365-6c48740b0638',
    'Risposta n. 234 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+234_2023.pdf/00d7e745-f59d-644d-44db-31186a8a89aa',
    'Risposta n. 233 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+233_2023.pdf/e40af1ba-6932-010b-8d25-43efe9ca0730',
    'Risposta n. 232 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+232_2023.pdf/a14273a0-47ef-f49c-c836-28857d39cd90',
    'Risposta n. 231 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+231_2023.pdf/aba33a76-2867-0bdd-ce94-9a464a7183a8',
    'Risposta n. 230 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+230_2023.pdf/90207174-409a-f62a-1790-22ae82ec59aa',
    'Risposta n. 229 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+229_2023.pdf/6da30e20-ab96-c3ed-8142-29b199801c52',
    'Risposta n. 228 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+228_2023.pdf/ca8ce5f7-25e1-aa5b-005b-4b0c28571ac8',
    'Risposta n. 227 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+227_2023.pdf/3b62e2eb-1b57-28be-c108-cf251fee0025',
    'Risposta n. 226 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+226_2023.pdf/573317de-eb0a-ed43-d464-315cde7299d8',
    'Risposta n. 225 del 1_03_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5081408/Risposta+n.+225_2023.pdf/2b702e9a-fc0e-8de6-ebb5-12bb95782320',
    'Risposta n. 224 del 24_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Principio+di+diritto+6_2023.pdf/418a6c4c-f4b4-4ed7-92ba-102ebc07c806',
    'Risposta n. 223 del 22_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+223_2023.pdf/97e455b7-c6f0-c40a-535f-6d3edaa224a9',
    'Risposta n. 222 del 22_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+222_2023.pdf/11df272e-8433-ed36-e670-0d63b5715bef',
    'Risposta n. 221 del 22_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+221_2023.pdf/98bf2558-703c-5603-7b28-05fbc4713bd9',
    'Risposta n. 220 del 22_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+220_2023.pdf/2d045fd6-0e90-ba47-706d-59ec98a17572',
    'Risposta n. 219 del 21_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+219_2023.pdf/16e7caa7-9f9f-8f1e-963b-36c49d5e387d',
    'Risposta n. 218 del 16_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+218_2023.pdf/9669c7f7-9c31-2ab0-4839-442880d604a0',
    'Risposta n. 217 del 16_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+217_2023.pdf/2c92a3b7-7972-99c3-c164-6e106c4839d2',
    'Risposta n. 216 del 15_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+216_2023.pdf/f8058066-31c1-a3b5-c8c1-cfae892224a0',
    'Risposta n. 215 del 15_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+215_2023.pdf/616226b0-a460-7087-cc39-95d3ded0316c',
    'Risposta n. 214 del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+214_2023.pdf/e639e8a3-b42a-f320-4373-1613eb5b3098',
    'Risposta n. 213 del 14_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+213_2023.pdf/beaa8518-31cd-7728-cea7-1be23e1b11c3',
    'Risposta n. 212 del 13_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+212_2023.pdf/603d5e78-f264-ba4c-4e39-3b29d0c3057e',
    'Risposta n. 211 del 13_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+211_2023.pdf/4b0c69bc-0a76-8cbd-791f-ccc96ff98543',
    'Risposta n. 210 del 9_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+210_2023.pdf/4751af19-6aa4-241d-9d64-44101478a669',
    'Risposta n. 209 del 8_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+209_2023.pdf/824d65eb-6049-82d6-a95e-d8b049b48a42',
    'Risposta n. 208 del 8_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+208_2023.pdf/e28c9a49-2d4c-c4c2-43c4-caa8a4f43f1b',
    'Risposta n. 207 del 8_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+207_2023.pdf/8eae5ae9-957c-b1c5-d7d9-6d9c65d8cb29',
    'Risposta n. 206 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+206_2023.pdf/baa9c379-3f0c-fa54-90aa-44d11217e426',
    'Risposta n. 205 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+205_2023.pdf/619bfe2b-2d9a-96ed-c07d-2d9f8eb443e4',
    'Risposta n. 204 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+204_2023.pdf/5189c15d-4fe7-f043-606b-2843bc00df74',
    'Risposta n. 203 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+203_2023.pdf/92205aa6-9eaa-3f0f-a6b4-3abed3e9deaa',
    'Risposta n. 202 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+202_2023.pdf/5ef11848-7c34-9230-2466-04ba15b4f813',
    'Risposta n. 201 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+201_2023.pdf/bd7779b3-057c-7171-db13-94d1da8bd124',
    'Risposta n. 200 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+200_2023.pdf/99850351-d168-2c0f-77b1-8011ff7aff59',
    'Risposta n. 199 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+199_2023.pdf/8983a977-756a-2b39-d8d5-ca957f9f62bf',
    'Risposta n. 198 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+198_2023.pdf/51a3c274-0086-61dd-de7c-22a3a197c36c',
    'Risposta n. 197 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+197_2023.pdf/8251e0c0-90bf-7263-2c9e-630bde935b13',
    'Risposta n. 196 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+196_2023.pdf/2469f473-ab1a-de59-2ad9-2a3717b70c45',
    'Risposta n. 195 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+195_2023.pdf/f4231e3a-e258-581e-ff80-9d1024390b64',
    'Risposta n. 194 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+194_2023+%281%29.pdf/0856a90e-989d-77b3-b713-64311117e05d',
    'Risposta n. 193 del 7_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+193_2023.pdf/7d93273d-f1d8-bf28-94e5-308ca2e732b7',
    'Risposta n. 192 del 6_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+192_2023.pdf/566890ad-b07c-3574-3524-68574ea91619',
    'Risposta n. 191 del 6_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+191_2023.pdf/1662469d-a8dc-24d7-538f-b611a08934bb',
    'Risposta n. 190 del 6_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+190_2023.pdf/eb10c718-1ff1-e3c3-c1ab-dac0ef3bc95c',
    'Risposta n. 189 del 3_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+189_2023.pdf/124ec0fe-b659-7184-998b-20c9e8888255',
    'Risposta n. 188 del 2_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+188_2023.pdf/16124714-192f-7d3d-fba5-71b07f2efe74',
    'Risposta n. 187 del 1_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+187_2023.pdf/c3eb450b-cc06-68f8-e21a-1ca3f4c074b6',
    'Risposta n. 186 del 1_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+186_2023.pdf/bbe41996-1962-5b66-0ce5-c21ebe0de89e',
    'Risposta n. 185 del 1_02_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4988698/Risposta+n.+185_2023.pdf/dc3daea0-c432-cce1-2708-07ddec4d836d',
    'Risposta n. 184 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+184_2023.pdf/8938b1d4-49c6-ce80-245c-c8b6dabd9759',
    'Risposta n. 183 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+183_2023.pdf/16bd535c-6de2-0f0c-067e-e7ecb589a6f5',
    'Risposta n. 182 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+182_2023.pdf/2bb17f06-4a18-1d9a-60e7-d1b8abc9f717',
    'Risposta n. 181 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+181_2023.pdf/91fe2ee0-6fd7-7340-24f4-cf5477e650c9',
    'Risposta n. 180 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+180_2023.pdf/1519040d-8b27-64c8-5f51-43b862dd3b77',
    'Risposta n. 179 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+179_2023.pdf/ce4cbc00-0053-bcf0-0e79-1490d2f3d3da',
    'Risposta n. 178 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+178_2023.pdf/cb765cf9-2f18-c22e-4612-924f6976fe14',
    'Risposta n. 177 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+177_2023.pdf/eacb3e3a-ba91-044a-2ea3-467a0cc586f3',
    'Risposta n. 176 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/rispsota+176_2023.pdf/90a989a6-7cbf-2964-65ae-a5dcd6d16356',
    'Risposta n. 175 del 31_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+175_2023.pdf/2790bc02-712b-6a51-fd33-f17f6c6abebf',
    'Risposta n. 174 del 27_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+174_2023.pdf/f62ff791-0770-120e-3141-56d4e9124e2d',
    'Risposta n. 173 del 27_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+173_2023.pdf/d87f3410-f03a-8bef-1289-298050043922',
    'Risposta n. 172 del 27_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+172_2023.pdf/2105b526-6f58-72bd-a5cc-8721c7875f9b',
    'Risposta n. 171 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+171_2023.pdf/30b3594b-23a7-3e77-77d4-8a1432b903a4',
    'Risposta n. 170 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+170_2023.pdf/f6ed631a-fdf0-5a8f-4780-e0724196f8b1',
    'Risposta n. 169 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+169_2023.pdf/680598c6-81b3-ccd4-f61f-bd9c76846427',
    'Risposta n. 168 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+168_2023+rett.pdf/69567582-4c8c-0cda-0655-efe10d3882bd',
    'Risposta n. 167 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+167_2023.pdf/b9c67c14-86ca-ff53-9906-7f2230b93324',
    'Risposta n. 166 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+166_2023.pdf/3ff912bf-6047-0257-2feb-0f0c2397f864',
    'Risposta n. 165 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+165_2023.pdf/67b24cfd-9b45-3aba-8b52-491762474c8b',
    'Risposta n. 164 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+164_2023.pdf/95a90804-07a6-ab43-0bf8-6727cd334c3c',
    'Risposta n. 163 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+163_2023.pdf/5a9d3fe1-43e8-8fd2-2c29-f82840e10428',
    'Risposta n. 162 del 26_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+162_2023.pdf/5a5f8929-34a9-405d-899e-586e0f0e5c7f',
    'Risposta n. 161 del 25_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+161_2023.pdf/04bf28c5-37f8-bedf-8a21-9faa7f475acd',
    'Risposta n. 160 del 25_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+160_2023+%281%29.pdf/73f4f7b4-f476-205a-9c78-8b5e974f9453',
    'Risposta n. 159 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+159_2023.pdf/bbdacd69-360a-7bae-f02c-2df8c59e09f0',
    'Risposta n. 158 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_158_2023.pdf/64b253fe-58c9-b03f-f6d6-4d2c291d3513',
    'Risposta n. 157 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_157_2023.pdf/985a6256-2565-35d0-cfca-2dd6dd2e8d09',
    'Risposta n. 156 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_156_2023.pdf/7c5245b5-c46b-463e-7a00-0b4a8747d3ea',
    'Risposta n. 155 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_155_2023.pdf/7df216a7-4258-2839-1451-a0d16079ed49',
    'Risposta n. 154 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_154_2023.pdf/9dd6ec39-255f-fa83-ebbc-9dc6b4a67d50',
    'Risposta n. 153 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_153_2023.pdf/0d6c7f25-2aae-098f-9b7d-bb7b39d6143c',
    'Risposta n. 152 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_152_2023.pdf/4cd609fc-99a9-2a9e-3d2e-e1fb872a831c',
    'Risposta n. 151 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_151_2023.pdf/9f0315ec-4de6-bb86-9fa8-70082d2ad85c',
    'Risposta n. 150 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_150_2023.pdf/56f86f56-204b-9a1c-3bc9-6c620391a201',
    'Risposta n. 149 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_149_2023.pdf/08fc78ab-6eac-7695-40e8-329a85973b09',
    'Risposta n. 148 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_148_2023.pdf/563fabc7-b529-5db6-706c-6ee1fbb4d960',
    'Risposta n. 147 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_147_2023.pdf/8243a59f-2d8c-9c4e-5179-3404e1aaca91',
    'Risposta n. 146 del 24_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta_n_146_2023.pdf/0e83bfaa-e5fc-e941-ca16-0363d580bc8b',
    'Risposta n. 145 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+145_2023.pdf/9dd55f99-6a50-0168-d682-8f66f7e4c297',
    'Risposta n. 144 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+144_2023.pdf/53be9e22-f39d-3a76-0363-cb0b61b0cc4f',
    'Risposta n. 143 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+143_2023.pdf/6853cb9a-b8be-a44b-d61f-8d51b57f6a65',
    'Risposta n. 142 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+142_2023.pdf/a9b18f0b-d236-e422-858d-ef4845267e7a',
    'Risposta n. 141 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+141_2023.pdf/6620f3f1-4c6a-d277-1188-1219fbe91ee2',
    'Risposta n. 140 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+140_2023+%281%29.pdf/2222a1ef-f298-53bf-aff8-9712e726502d',
    'Risposta n. 139 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+139_2023.pdf/4d3370ae-1c6a-1749-4189-ad76040d002c',
    'Risposta n. 138 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+138_2023+%283%29.pdf/9d6a8646-2fba-44ab-7cd6-5f2bc93f32ad',
    'Risposta n. 137 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+137_2023.pdf/7e6001f8-0c09-130c-160d-5294641412a5',
    'Risposta n. 136 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+136_2023.pdf/59057331-5669-f39e-c2cc-a50bb4b1d095',
    'Risposta n. 135 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+135_2023.pdf/4581b0ec-9622-71da-b4e6-71aa31195fbe',
    'Risposta n. 134 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+134_2023.pdf/3a83d23a-c0b3-3665-b89c-1a3022060e08',
    'Risposta n. 133 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+133_2023.pdf/7ae04750-0858-8761-2ec9-f221fc4d47cd',
    'Risposta n. 132 del 23_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+132_2023.pdf/3fb518d9-3cd8-493d-6357-fa6393e1c116',
    'Risposta n. 131 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+131_2023.pdf/b87bd947-f08e-84a1-e4b7-fa0198cee630',
    'Risposta n. 130 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+130_2023.pdf/f07a60d0-4337-83e5-ca31-e0f18c081ce4',
    'Risposta n. 129 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+129_2023.pdf/df9c2036-47c1-cba4-4469-e6ac1ae3fd82',
    'Risposta n. 128 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+128_2023.pdf/38d17f3e-8366-90dd-8e15-c8bf9f31b063',
    'Risposta n. 127 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+127_2023.pdf/2125f683-d04e-273f-cbcb-b6cb172cc3c4',
    'Risposta n. 126 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+126_2023.pdf/16bc9d13-92ce-1147-beaf-cf86437834a2',
    'Risposta n. 125 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+125_2023.pdf/81d92a51-d464-3c8d-17ee-49e276178fbf',
    'Risposta n. 124 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+124_2023.pdf/0b0f4dc5-19c1-8fca-50b6-fba0d62d2015',
    'Risposta n. 123 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+123_2023.pdf/94d327f7-0580-dce3-a6ad-178387d6cf2a',
    'Risposta n. 122 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+122_2023.pdf/e91e4e47-a175-0725-0347-82f05e9e4b21',
    'Risposta n. 121 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+121_2023.pdf/74b74dcb-27ce-b732-91af-323385664970',
    'Risposta n. 120 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+120_2023.pdf/f9169c04-e51a-8d81-6620-dd2f64f87313',
    'Risposta n. 119 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+119_2023.pdf/0e4158bf-6f6e-9ad8-2a69-5da9e394b47e',
    'Risposta n. 118 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+118_2023.pdf/87d52029-2e3b-ed60-7a49-f5af14d6059a',
    'Risposta n. 117 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+117_2023.pdf/69a172f7-21d8-179c-7589-21e57dc8d5a6',
    'Risposta n. 116 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+116_2023.pdf/691ae858-1f73-9cd3-4784-00d1a4bcb5ba',
    'Risposta n. 115 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+115_2023.pdf/ceb853a4-9006-8e9d-7c21-f117e8e7548c',
    'Risposta n. 114 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+114_2023.pdf/8260e057-56fd-a38d-8cad-0d27b48c68e0',
    'Risposta n. 113 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+113_2023.pdf/91f81db6-62db-0ef9-02c9-93aa8b75d4ae',
    'Risposta n. 112 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+112_2023.pdf/aa925b5a-d3df-b1c6-82a7-692a0994db74',
    'Risposta n. 111 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+111_2023.pdf/e2f5ffd3-e143-40a9-65a4-5463a327fcd4',
    'Risposta n. 110 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+110_2023.pdf/432b0c2e-f854-e742-e247-ba6f68e86780',
    'Risposta n. 109 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+109_2023.pdf/fa5dac31-61a2-6afb-b31e-1ff628e0da95',
    'Risposta n. 108 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+108_2023.pdf/393e376b-5377-8bbe-3043-255ebff83e4d',
    'Risposta n. 107 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+107_2023.pdf/e8c5d9bf-b934-7511-de93-52bfc20830c3',
    'Risposta n. 106 del 20_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+106_2023.pdf/8891ea74-bde2-e079-436a-900ae284b17c',
    'Risposta n. 105 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+105_2023.pdf/a24d2f8c-fe72-3e04-04d0-2dccb52918a7',
    'Risposta n. 104 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+104_2023.pdf/d3d04f34-29e2-5ea0-2ab8-61879f03bbd5',
    'Risposta n. 103 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+103_2023.pdf/d5ef20f3-5f2f-4578-9bc3-982d3bd2f8b3',
    'Risposta n. 102 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+102_2023.pdf/3f2d22d1-1ce6-ae07-436b-086873637505',
    'Risposta n. 101 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+101_2023.pdf/9820bc66-d474-3598-bca2-508a2bdc83f1',
    'Risposta n. 201 del 11_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+201_2024.pdf/c61bbdd5-971b-7ea6-943c-d3ff1c6ae80f',
    'Risposta n. 200 del 11_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+200_2024.pdf/1579c1a4-c9df-c64b-4371-d4ea0cf11922',
    'Risposta n. 199 del 10_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+199_2024.pdf/b3969ba0-ffed-c87a-0870-c2feba85f4c3',
    'Risposta n. 198 del 10_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+198_2024.pdf/55a7316e-b5b2-8b3f-9811-cb2b7426b60d',
    'Risposta n. 197 del 10_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+197_2024.pdf/88a42c3d-e5e5-e384-eaf5-3889d678923d',
    'Risposta n. 196 del 10_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+196_2024.pdf/05ee5abb-9f99-f568-fc6c-5af03133694c',
    'Risposta n. 195 del 9_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/pubblicazione_SC_956_551_2024_per+pubblicazione+09_10_2024_pubb+195_2024.pdf/044c6290-366f-1203-6f74-a47d921f08c2',
    'Risposta n. 194 del 8_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+194_2024.pdf/b2fe6b3e-461c-22d4-a64c-5ee39ab906a0',
    'Risposta n. 193 del 4_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+193_2024.pdf/f5cf5a76-7e1d-25c1-3560-efdbbd18a794',
    'Risposta n. 192 del 4_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+192_2024.pdf/29098b56-547f-763b-b547-7a262761be01',
    'Risposta n. 191 del 3_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+191_2024.pdf/8d82af5e-1c01-2376-0da7-25039a3c2787',
    'Risposta n. 190 del 1_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+190_2024.pdf/1d403651-bd8b-bd9d-a581-826e09f6169c',
    'Risposta n. 189 del 1_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+189_2024.pdf/53de1ff7-0267-035d-33aa-d5709422725f',
    'Risposta n. 188 del 1_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+188_2024.pdf/bedba39c-5be9-c6c0-8ccf-f7ee8b8bbe90',
    'Risposta n. 187 del 1_10_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6458344/Risposta+n.+187_2024.pdf/d277d0aa-88da-a115-a4fa-1038239cbae8',
    'Risposta n. 186 del 26_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+186_2024.pdf/42da0aca-24dc-ba6b-d45e-184fbd5d47ab',
    'Risposta n. 185 del 18_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+185_2024.pdf/9ebe3b0e-a6be-556f-7ed8-ba10a2543823',
    'Risposta n. 184 del 16_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+184_2024+%281%29.pdf/3f708e1f-ac0d-fb73-85e1-b70ec6fa9032',
    'Risposta n. 183 del 12_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+183_2024.pdf/e3a7326a-40f1-0a38-f781-47d58e659fa0',
    'Risposta n. 182 del 12_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+182_2024.pdf/46754567-0253-1ace-56e7-2f8a74e5cf6b',
    'Risposta n. 181 del 12_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+181_2024.pdf/78fd4f80-d1c1-3a2b-c7de-50b0f959e9ec',
    'Risposta n. 180 del 12_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+180_2024.pdf/acab5fe9-e9dd-237e-5458-c2c8f6e489eb',
    'Risposta n. 179 del 12_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6390987/Risposta+n.+179_2024.pdf/a06d653d-57bf-ccdd-2d80-b94c923dc3db',
    'Risposta n. 178 del 2_09_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781145/Risposta+n.+178_2024.pdf/addd19d3-c174-9dc2-973f-656993c0293f',
    'Risposta n. 177 del 29_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+177_2024.pdf/8d09e2ab-07bd-1581-c7a0-4452682d0910',
    'Risposta n. 176 del 21_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+176_2024.pdf/81d4cd6a-e5b0-a7c5-996e-4b0626574d80',
    'Risposta n. 175 del 21_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+175_2024.pdf/829ca536-d91c-07a9-034a-0a70886f9258',
    'Risposta n. 174 del 21_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+174_2024.pdf/f2013dc1-acb4-2459-77e9-bac69cc74e74',
    'Risposta n. 173 del 20_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+173_2024.pdf/44093167-4bd8-56dd-e88b-4d38b868655e',
    'Risposta n. 172 del 20_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+172_2024.pdf/02f30f35-ce7c-54a2-fdd1-4c99b1eddeb8',
    'Risposta n. 171 del 20_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+171_2024.pdf/9dc13ff5-609c-5361-68d4-dc89044ce15a',
    'Risposta n. 170 del 20_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+170_2024.pdf/ff583076-ef8e-969b-3fa2-b0fff893dc21',
    'Risposta n. 169 del 12_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+169_2024.pdf/2ab35fb1-6273-11f9-6865-2a8aa7378a37',
    'Risposta n. 168 del 5_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+168_2024.pdf/3913407e-bf78-e36f-7b61-903785428a40',
    'Risposta n. 167 del 1_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+167_2024.pdf/7a847eb4-9d77-8fe5-8ca9-8aba45bb7626',
    'Risposta n. 166 del 1_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+166_2024.pdf/6637bac9-3cba-6842-1969-0c86f4aee77d',
    'Risposta n. 165 del 1_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+165_2024.pdf/b810ea94-494d-d387-a9b3-fb2323801df4',
    'Risposta n. 164 del 1_08_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6314639/Risposta+n.+164_2024.pdf/5f82b0b2-014e-ea38-bb60-dc2b8e87ac68',
    'Risposta n. 163 del 29_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+163_2024.pdf/82d10d88-3da7-9b5a-7876-e2155d55e088',
    'Risposta n. 162 del 29_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+162_2024.pdf/745f8dc0-dae3-fc91-7e8e-bdaec8e0e876',
    'Risposta n. 161 del 26_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+161_2024.pdf/7f19da83-2c8f-e61c-892e-7db536df9d07',
    'Risposta n. 160 del 24_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+160_2024.pdf/acaed3f9-d7c2-c8ac-4599-932b17ae8e74',
    'Risposta n. 159 del 22_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+159_2024.pdf/2a06bb59-75f0-ee43-7555-34b2771ffc0a',
    'Risposta n. 158 del 18_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+158_2024+%28002%29.pdf/3707226e-7dc1-3c00-f72b-f777f2ecbf38',
    'Risposta n. 157 del 17_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+157_2024.pdf/ec13349a-d107-4a8d-cfb5-b95623c622ca',
    'Risposta n. 156 del 16_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+156_2024.pdf/d96415d9-7458-02bf-ba79-516aa4d1cdd5',
    'Risposta n. 155 del 15_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+155_2024.pdf/bc31da84-b0aa-0013-efca-f895aaa45cd9',
    'Risposta n. 154 del 15_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+154_2024.pdf/0cfc29ea-90a5-20a3-1ad3-12952386bf82',
    'Risposta n. 153 del 15_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+153_2024.pdf/64ed4526-55fa-43e3-c5f2-36f58e65796d',
    'Risposta n. 152 del 15_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+152_2024.pdf/f4f2251e-eef9-d95d-4f4b-f71cfaae2d26',
    'Risposta n. 151 del 11_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+151_2024.pdf/dfdb58bc-826f-3f93-c8b2-dee9c948b1e8',
    'Risposta n. 150 del 11_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+150_2024.pdf/e9008faf-03dd-23c5-d673-824789d632e1',
    'Risposta n. 149 del 11_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+149_2024.pdf/0954cbc2-ddb7-d5d7-c285-23a0b7e2bcf4',
    'Risposta n. 148 del 11_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+148_2024.pdf/f555bbe4-b7e9-4ec4-991a-6167fd4e24ea',
    'Risposta n. 147 del 11_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+147_2024.pdf/f1dc7edf-3261-2f40-b846-94078a083fde',
    'Risposta n. 146 del 9_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+146_2024.pdf/c6551715-f584-5009-8479-0ac8c434cb06',
    'Risposta n. 145 del 4_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+145_2024.pdf/17504c9c-87af-475b-cca6-c54968bbef9f',
    'Risposta n. 144 del 3_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+144_2024.pdf/e0d2f285-74b0-97fb-6b85-0d6edaa1aa4a',
    'Risposta n. 143 del 2_07_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6241342/Risposta+n.+143_2024.pdf/a4c5f0d3-2464-2fb3-e998-997e6ea02759',
    'Risposta n. 142 del 24_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+142_2024.pdf/91294b41-54c0-8492-16c6-25236c25b381',
    'Risposta n. 141 del 24_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+141_2024.pdf/749e2ab7-a2f1-424b-47ac-b0da7d4ef91a',
    'Risposta n. 140 del 24_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+140_2024.pdf/b4964b94-e50b-cbb6-d69c-46f8001372ce',
    'Risposta n. 139 del 21_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+139_2024.pdf/a2c1dd9f-4043-60c8-856f-cff927b225dd',
    'Risposta n. 138 del 20_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+138_2024.pdf/751aeece-f265-abe1-3b9a-cc1176ae17c5',
    'Risposta n. 137 del 20_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+137_2024.pdf/6b3abf18-7c79-c7ed-d11e-545ed1d8c2eb',
    'Risposta n. 136 del 20_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5825043/Risposta+n.+136_2024.pdf/89898130-20a1-8deb-4dd5-564a6d8789a2',
    'Risposta n. 135 del 18_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5825043/Risposta+n.+135_2024.pdf/bc759394-9ce0-82df-2c23-dda688f8d235',
    'Risposta n. 134 del 18_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+134_2024.pdf/d463968d-9b1b-df00-48a5-34da7d670f17',
    'Risposta n. 133 del 17_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+133_2024.pdf/f5905916-ca68-f6bc-9943-a17fca0047bb',
    'Risposta n. 132 del 12_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+132_2024.pdf/31d348e5-e9b5-269c-eda7-c212cc6e4809',
    'Risposta n. 131 del 7_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+131_2024.pdf/7d4b1da1-c037-e207-42bb-abab067bb477',
    'Risposta n. 130 del 6_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+130_2024.pdf/1ed9e919-e63d-04d9-5ed3-253f9c79ff56',
    'Risposta n. 129 del 5_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+129_2024.pdf/8bcec98d-1b64-d4d8-1dd8-2d4ee1e9f786',
    'Risposta n. 128 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+128_2024.pdf/404c56df-9529-87b4-3c56-c7565ce9ed8d',
    'Risposta n. 127 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+127_2024.pdf/6690433b-1bc6-9bca-0135-2caa7ea503af',
    'Risposta n. 126 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+126_2024.pdf/0df5e380-bf6f-a3e1-cc4f-dda04ae3fc09',
    'Risposta n. 125 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+125_2024.pdf/fbc80d8c-c56a-42b7-0ae4-e306283d5010',
    'Risposta n. 124 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+124_2024.pdf/e94420f4-d5d7-a5ce-dc7c-229dfbf174c4',
    'Risposta n. 123 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+123_2024.pdf/bb4dc8db-97b8-e1e7-9eed-52677e834c0a',
    'Risposta n. 122 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+122_2024.pdf/88fba4e2-293a-4231-9917-64ba2596663a',
    'Risposta n. 121 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+121_2024.pdf/5068cb7e-860e-5960-a379-e39b6222442a',
    'Risposta n. 120 del 3_06_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6193302/Risposta+n.+120_2024.pdf/687451dd-bc4d-b786-124f-27dcfb786795',
    'Risposta n. 119 del 31_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+119_2024.pdf/0d268dd1-47cf-337b-a413-64895d36153a',
    'Risposta n. 118 del 30_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+118_2024.pdf/82b09178-f089-e2c3-a98b-e2c7374500db',
    'Risposta n. 117 del 28_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+117_2024.pdf/dc661e9d-675d-a4d5-d6e8-602211ee803b',
    'Risposta n. 116 del 24_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+116_2024.pdf/82a17a73-1fd4-1d17-fcc7-3a6f8e4e7d5b',
    'Risposta n. 115 del 23_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+115_2024.pdf/f321e208-5dd9-e282-9557-1faa1276b88b',
    'Risposta n. 114 del 23_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+114_2024.pdf/9d972ab3-83ed-9390-5841-213376e0a18c',
    'Risposta n. 113 del 23_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+113_2024.pdf/d7716f42-b442-9667-b783-82612578e0a6',
    'Risposta n. 112 del 23_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+112_2024.pdf/b6d4ee08-1696-8231-3b46-b9de61552ee1',
    'Risposta n. 111 del 21_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+111_2024.pdf/5fafb912-bc42-1388-d4ad-35bae50064b9',
    'Risposta n. 110 del 21_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+110_2024.pdf/2fcd9e4b-6286-d314-83c2-ddecd5a5bf74',
    'Risposta n. 109 del 21_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+109_2024.pdf/5ec77287-79e1-c313-0589-f6d3efe427bd',
    'Risposta n. 108 del 17_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+108_2024.pdf/04444a65-ad24-c783-6645-3e793e819e87',
    'Risposta n. 107 del 16_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+107_2024.pdf/a3bdd6b7-b32b-6263-30eb-817ae77991ce',
    'Risposta n. 106 del 16_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+106_2024.pdf/31119fe9-542e-3910-95a4-1ed78c940adf',
    'Risposta n. 105 del 16_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+105_2024.pdf/7361beab-6a4c-9993-83da-dba1c995fed5',
    'Risposta n. 104 del 13_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+104_2024.pdf/6cf6bf2e-5198-676d-22b9-d0a279701e1e',
    'Risposta n. 103 del 13_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+103_2024.pdf/0ba65758-2c84-667e-f90e-c22b8508898d',
    'Risposta n. 101 del 10_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+101_2024.pdf/b7b7bb7f-5134-7016-cbbc-3d191d449d6f',
    'Risposta n. 102 del 13_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+102_2024.pdf/e4cc18c1-b722-005f-7ec6-10221c2f9a7a',
    'Risposta n. 100 del 3_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+100_2024.pdf/3ffd9eb9-a304-8d82-6839-e9d2016c0f7b',
    'Risposta n. 99 del 2_05_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6101204/Risposta+n.+99_2024.pdf/d91d38ef-aa94-8596-41ad-26b1eb14fe84',
    'Risposta n. 98 del 23_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+98_2024.pdf/03cb7804-7866-d076-c23a-e6ec90910b61',
    'Risposta n. 97 del 23_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+97_2024.pdf/7e689e82-4288-c7bd-723f-ed914f5b4b27',
    'Risposta n. 96 del 23_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+96_2024.pdf/2aa41e39-ccb7-a636-d520-2098214ff23c',
    'Risposta n. 95 del 19_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+95_2024.pdf/8680386e-dd1c-866c-642e-eeb559d8592b',
    'Risposta n. 94 del 17_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+94_2024.pdf/f39e78df-62ab-3c07-16d2-67c6fa543f69',
    'Risposta n. 93 del 16_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+93_2024.pdf/93b0383b-4717-8907-8354-828bd96d16f5',
    'Risposta n. 92 del 16_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+92_2024.pdf/50d5bd09-8562-5331-0f50-c86343d9aa8a',
    'Risposta n. 91 del 12_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+91_2024.pdf/b37c75c4-79a2-4c7b-3f73-b36b05f8ca39',
    'Risposta n. 90 del 11_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+90_2024.pdf/4cdc0e05-2171-6bf0-1401-e14206fe7ee2',
    'Risposta n. 89 del 11_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+89_2024.pdf/169c97c9-2a04-1e95-f7ac-d1b0e36d7807',
    'Risposta n. 88 del 8_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+88_2024.pdf/f0e4cf5c-4fa8-df71-b8e2-54d2a6acb2d4',
    'Risposta n. 87 del 8_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+87_2024.pdf/cfc9ce2e-9f12-779c-750e-f7bfa0453795',
    'Risposta n. 86 del 4_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+86_2024.pdf/f6c04eff-c531-c34a-450e-5299058c07af',
    'Risposta n. 85 del 2_04_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/6021756/Risposta+n.+85_2024.pdf/d8c7a4ed-4803-c107-28ba-3da14517aa88',
    'Risposta n. 84 del 29_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+84_2024.pdf/9e2a243d-b815-531f-de0f-f1cfb84c4cce',
    'Risposta n. 83 del 28_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+83_2024.pdf/1b863620-2597-70a3-79de-a1f69ec8ce76',
    'Risposta n. 82 del 28_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+82_2024.pdf/17982c54-f8f6-628f-b37c-34b628559be0',
    'Risposta n. 81 del 28_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+81_2024.pdf/8e499684-bc6e-e78b-f4cd-fdce55ba7eef',
    'Risposta n. 80 del 25_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+80_2024.pdf/4bd95451-0061-9a89-2c4f-b494d533bb26',
    'Risposta n. 79 del 25_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+79_2024.pdf/95768f10-a71f-7cb3-7198-6b299b2ccb82',
    'Risposta n. 78 del 22_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+78_2024.pdf/6bdaaf21-1e35-00f2-2047-a94b776d26e3',
    'Risposta n. 77 del 22_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+77_2024.pdf/18a740b8-8b9d-9bbd-1755-06bcba932592',
    'Risposta n. 76 del 22_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+76_2024.pdf/f0933165-e52e-a519-8ca9-85d3f5162f23',
    'Risposta n. 75 del 21_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+75_2024.pdf/c35b606c-ebc8-6b37-2471-4a066ba91f34',
    'Risposta n. 74 del 21_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+74_2024.pdf/aebf169d-73ae-0eec-ea3a-01af22e9bd4f',
    'Risposta n. 73 del 21_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+73_2024.pdf/fdeb5e42-ad76-85f4-72c7-81ddb0378999',
    'Risposta n. 72 del 18_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+72_2024.pdf/d02ebe16-bbcc-b172-8601-235261988fe8',
    'Risposta n. 71 del 14_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+71_2024.pdf/3883a33b-7872-e6c7-6534-419332cb2d58',
    'Risposta n. 70 del 13_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+70_2024.pdf/4ba16803-6532-bd0b-e450-ca441a144b3e',
    'Risposta n. 69 del 12_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+69_2024.pdf/1f32f719-271d-ec42-b944-2ed9a2bb468d',
    'Risposta n. 68 del 12_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+68_2024.pdf/2f1a753c-7c2a-a655-712f-fc4bc9ed6479',
    'Risposta n. 67 del 12_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+67_2024.pdf/169ef923-d793-f417-e801-521007903333',
    'Risposta n. 66 del 11_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+66_2024.pdf/0b581664-ac4d-1383-59b6-2f889e5bfa21',
    'Risposta n. 65 del 11_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+65_2024.pdf/2b91dcf1-1cfe-1609-875e-7122f82b2a80',
    'Risposta n. 64 del 8_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+64_2024.pdf/eb24fc21-5938-db31-d7c7-47a57f73cab5',
    'Risposta n. 63 del 8_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+63_2024.pdf/affc1723-c615-1f50-7f1f-47dfadb31dfa',
    'Risposta n. 62 del 7_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+62_2024.pdf/380f8b23-1980-39b8-cdea-06d4a44b5e3c',
    'Risposta n. 61 del 6_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+61_2024.pdf/d0c46e4b-5505-f701-ef1b-7dd634a12526',
    'Risposta n. 60 del 5_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+60_2024.pdf/7a296c98-771a-fcbd-5f3f-112db3c0a1c2',
    'Risposta n. 59 del 5_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+59_2024.pdf/8da4ae84-e377-62c9-259f-e01af34150f3',
    'Risposta n. 58 del 4_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5946162/Risposta+n.+58_2024.pdf/d27c0412-9f5b-120e-4cd5-0381427d640e',
    'Risposta n. 57 del 1_03_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+57_2024.pdf/dbc6caf9-d2d2-41f0-a02c-e73b080f12b8',
    'Risposta n. 56 del 29_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+56_2024.pdf/a94e5c47-4720-9550-ff2f-99f3455b95d9',
    'Risposta n. 55 del 28_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+55_2024+%282%29.pdf/509cde22-f6b6-c3e5-041b-1b0f8e0838a9',
    'Risposta n. 54 del 28_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/risposta+54+2024.pdf/75fdda6b-66cd-c204-5737-437405494d1a',
    'Risposta n. 53 del 27_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+53_2024.pdf/00b84e08-750c-ac19-7694-8a633808c409',
    'Risposta n. 52 del 23_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+52_2024.pdf/947b5ea7-dcf0-659f-b17a-f83ef869bc45',
    'Risposta n. 51 del 22_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+51_2024.pdf/f029a70c-5c01-17fc-f9bd-f804a67ce3cd',
    'Risposta n. 50 del 22_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+50_2024.pdf/e050632e-6c9b-36f6-153f-2a4e4f33a461',
    'Risposta n. 49 del 22_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+49_2024.pdf/dbbeaf1e-22e3-f40b-cbe3-1adf5d73855c',
    'Risposta n. 48 del 22_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+48_2024.pdf/956650d6-1e5e-7faf-91c2-c3324b011ff0',
    'Risposta n. 47 del 21_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+47_2024.pdf/103fb4b7-1d00-b2e3-dc5d-100b39bfefbb',
    'Risposta n. 46 del 21_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+46_2024.pdf/1196ec07-4725-fa83-e71d-854e91c63a74',
    'Risposta n. 45 del 19_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+45_2024.pdf/42d7fe7c-9cd8-baec-772c-365eac09e3c8',
    'Risposta n. 44 del 16_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+44_2024.pdf/09b606fe-b6d0-9c86-126d-3582505c15eb',
    'Risposta n. 43 del 15_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+43_2024.pdf/5c652da8-58c3-2509-4530-e061f4ab096d',
    'Risposta n. 42 del 9_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+42_2024.pdf/94064a46-ebfa-7fe0-36f5-160537926d2b',
    'Risposta n. 41 del 9_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+41_2024.pdf/7c34f35c-698a-7eed-4b13-b8c4f010c4a7',
    'Risposta n. 40 del 9_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+40_2024.pdf/6ec5a79e-3ba5-43fe-fc43-6d6b7a6f28fa',
    'Risposta n. 39 del 9_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+39_2024.pdf/664a64e0-6830-9967-41a1-1f1d2075dd44',
    'Risposta n. 38 del 8_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+38_2024.pdf/307b1550-4128-38e4-9685-c025ef824512',
    'Risposta n. 37 del 8_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+37_2024.pdf/f50be3fd-68e8-37fb-478d-72276f8a8015',
    'Risposta n. 36 del 8_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+36_2024.pdf/c33e694a-d4a2-82b6-98b5-ec67d3dfe156',
    'Risposta n. 35 del 8_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+35_2024.pdf/877fba48-8eec-4275-7ee5-dffcc109fa5a',
    'Risposta n. 34 del 8_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+34_2024.pdf/2c327875-05d3-51b3-b41b-e20ec921993c',
    'Risposta n. 33 del 8_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+33_2024.pdf/f334d694-d05a-86f4-8eef-1f19e3f89392',
    'Risposta n. 32 del 7_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+32_2024.pdf/23eda674-a7e6-f69f-28f5-8634a7d3de68',
    'Risposta n. 31 del 7_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+31_2024.pdf/2f07218f-eff6-e49c-40c1-5eca2812245d',
    'Risposta n. 30 del 7_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+30_2024.pdf/87d9d20f-8c53-bb43-7099-af0a8cb722a6',
    'Risposta n. 29 del 2_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+29_2024.pdf/1d176e0c-a6ba-d6c0-8638-62004279887a',
    'Risposta n. 28 del 2_02_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5866231/Risposta+n.+28_2024.pdf/06e4acd7-9020-f94f-720d-9dcdd8f4b011',
    'Risposta n. 27 del 31_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+27_2024.pdf/359d26a2-d53e-a582-e91d-78b4c7ffdae8',
    'Risposta n. 26 del 30_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+26_2024.pdf/65200b4a-502d-c88b-e2fb-524d888cb6ad',
    'Risposta n. 25 del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+25_2024.pdf/179d525f-eb34-45e9-5486-ccdd10a177b3',
    'Risposta n. 24 del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+24_2024.pdf/be11431f-6688-5d9c-481c-743b955da31c',
    'Risposta n. 23 del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+23_2024.pdf/739d6e1c-c1b3-f4e8-59e7-5723c4835a2a',
    'Risposta n. 22 del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+interpello+n+22+del+2024.pdf/9bf34bdd-46dd-5926-34b7-561c15accc4b',
    'Risposta n. 21 del 29_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+21_2024.pdf/23c677b2-3697-71b5-0519-b9e44d17e870',
    'Risposta n. 20 del 26_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+20_2024.pdf/a1ebe1a5-8197-6945-f0a0-253a46cd9a93',
    'Risposta n. 19 del 26_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+19_2024.pdf/33d65944-8f05-4ce2-f170-c2c8bf5111b5',
    'Risposta n. 18 del 26_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+18_2024.pdf/85106010-874b-76de-4220-4965d5435dab',
    'Risposta n. 17 del 26_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+17_2024.pdf/e9d6c1d9-1fa6-52a6-a74e-46394adf37eb',
    'Risposta n. 16 del 26_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+16_2024.pdf/07dc278f-de3f-7179-e558-8dea90786408',
    'Risposta n. 15 del 24_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+15_2024.pdf/ead47504-fdc3-2cde-8607-392be74a1c61',
    'Risposta n. 14 del 24_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+14_2024.pdf/8d325de2-c5cd-2620-415b-a16f3b1168db',
    'Risposta n. 13 del 23_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+13_2024.pdf/9048ee00-bb09-56ec-be9a-eaff5396636d',
    'Risposta n. 12 del 22_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+12_2024.pdf/3a92de01-92f3-efb3-31c4-04df519c117d',
    'Risposta n. 11 del 22_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+11_2024.pdf/65b36a10-13d4-b899-a308-3cbd5b4685bd',
    'Risposta n. 10 del 17_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+10_2024.pdf/284b62f3-0488-1c68-bcb8-8235037b4a88',
    'Risposta n. 9 del 16_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+9_2024.pdf/c978f5f3-c24d-3372-c615-a4d1b9770bf6',
    'Risposta n. 8 del 12_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+8_2024.pdf/70da0cf5-62b9-aa14-ca00-c3408ad3c86a',
    'Risposta n. 7 del 12_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+7_2024.pdf/3bb7c228-089e-85de-4b79-addde5bf180e',
    'Risposta n. 6 del 12_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+6_2024.pdf/0223cf4a-608f-9032-9620-af77b97177a0',
    'Risposta n. 5 del 11_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+5_2024.pdf/8e2e7e25-cfcf-9176-91e6-af1ca5cd36e5',
    'Risposta n. 4 del 9_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+4_2024.pdf/ae6d4526-efee-7a4b-043b-0b1e34bbb7c0',
    'Risposta n. 3 del 9_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+3_2024.pdf/1371b5ea-981c-85ff-4aba-3fa332b63c1d',
    'Risposta n. 2 del 8_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+2_2024.pdf/4b747813-d5be-7bee-4211-bd4e0ef1e6c3',
    'Risposta n. 1 del 5_01_2024.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/5781149/Risposta+n.+1_2024.pdf/d17851bd-31d8-27f4-9bee-0c4b24ac9600',
    'Risposta n. 100 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+100_2023.pdf/e9e57bc3-3131-d30d-d119-2ad02ef4a4d5',
    'Risposta n. 99 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+99_2023.pdf/51bd10ba-56d8-addf-f180-e38dab3e81ce',
    'Risposta n. 98 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+98_2023.pdf/b85de7ed-7609-b612-cfc5-4dd9df4f43c3',
    'Risposta n. 97 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+97_2023.pdf/ed87d52d-4e69-78bc-99d9-5617f007e27f',
    'Risposta n. 96 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+96_2023.pdf/641578a8-e9b5-9443-0ed6-bc5f95694b05',
    'Risposta n. 95 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+95_2023.pdf/596d727f-9f02-31e2-10d1-eedaf474e4ae',
    'Risposta n. 94 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+94_2023.pdf/62c00aa6-6575-f44e-2bce-adade171af62',
    'Risposta n. 93 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+93_2023.pdf/6a55005c-4a62-7c95-86ce-cb0b36b8b6d1',
    'Risposta n. 92 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+92_2023.pdf/5372db75-9ed7-a1ab-decc-1be0111e772f',
    'Risposta n. 91 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+91_2023.pdf/e3b0bf2a-8bd5-a25f-86c8-a82322dd8613',
    'Risposta n. 90 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+90_2023.pdf/0702f990-06dc-545b-2028-6b2f956a32b8',
    'Risposta n. 89 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+89_2023.pdf/68c21bf9-fc0c-ba6f-d2fe-48e48eccfff0',
    'Risposta n. 88 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+88_2023.pdf/65d7de07-7466-9fa6-b553-1ac449f39bd8',
    'Risposta n. 87 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+87_2023.pdf/97cb0333-a54a-9b46-cd81-2648ad1a47bf',
    'Risposta n. 86 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+86_2023.pdf/fe7ffbdb-70ae-81e9-6eda-aebd538cdf00',
    'Risposta n. 85 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+85_2023.pdf/c1f9c173-71a4-b1f7-feb9-a5a20103eb02',
    'Risposta n. 84 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+84_2023.pdf/3b4d17f3-9108-8c0f-6b2f-bba6bcdb8a69',
    'Risposta n. 83 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+83_2023.pdf/e17404df-56ab-627b-08ef-bffe5f9f6aa7',
    'Risposta n. 82 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+82_2023.pdf/cf2a56f5-34cc-6880-b76f-ab39ea5831a3',
    'Risposta n. 81 del 19_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+81_2023.pdf/2bc47601-0fa4-8bef-ab79-44b4c263525a',
    'Risposta n. 80 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+80_2023.pdf/675bb91b-356c-f1cb-4069-6f87ab0f0808',
    'Risposta n. 79 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+79_2023.pdf/d661fa45-9378-5d83-6360-9c9c83b066eb',
    'Risposta n. 78 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+78_2023.pdf/d0242a1e-a34f-ba17-58d3-9bd4e2f47d8a',
    'Risposta n. 77 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+77_2023.pdf/277b055c-f217-d9ee-cdae-87c45dcb602b',
    'Risposta n. 76 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+76_2023.pdf/c0d39504-dadf-54d0-a947-0eefaf34a9f6',
    'Risposta n. 75 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+75_2023.pdf/44d42e32-48af-9108-f7e4-ccf38a2987f6',
    'Risposta n. 74 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+74_2023+%281%29.pdf/dfc312e5-44b3-40cb-a062-9344b8b82183',
    'Risposta n. 73 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+73_2023.pdf/2e43ae99-97d4-4ef0-5df3-8ca331eaac30',
    'Risposta n. 72 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+72_2023.pdf/a5d06dff-1dce-7732-298f-aea5ea0c6e6e',
    'Risposta n. 71 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+71_2023.pdf/3b84c6e9-2c3a-84fb-1b53-028b3052f70e',
    'Risposta n. 70 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+70_2023.pdf/6bcf62de-9a40-d122-3ea6-138aa8f7c85a',
    'Risposta n. 69 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+69_2023.pdf/cbbbc8da-cf51-a3c3-fdad-e09fe2a4286e',
    'Risposta n. 68 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+68_2023.pdf/3a3ee89d-a32d-de07-a379-9934772cd809',
    'Risposta n. 67 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+67_2023.pdf/f472736f-1bfd-3953-7339-a122fd15d880',
    'Risposta n. 66 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+66_2023.pdf/73515568-cac3-4312-6433-a7ab2cce4889',
    'Risposta n. 65 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+65_2023.pdf/5194e642-acb5-a6f3-1bae-b90c885936cf',
    'Risposta n. 64 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+64_2023.pdf/2c1d9b42-f01f-19a2-88ff-e1737f3d33af',
    'Risposta n. 63 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+63_2023.pdf/97a4bbd9-1c7e-46f3-8b5f-a411ce285201',
    'Risposta n. 62 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+62_2023.pdf/3d306a9d-a878-fa69-1e37-606b3df81664',
    'Risposta n. 61 del 18_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+61_2023.pdf/bd6db755-057f-6e72-853d-9b977bfc3024',
    'Risposta n. 60 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+60_2023.pdf/3681c69a-d3c4-1dd1-9edd-483eba670f6c',
    'Risposta n. 59 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+59_2023.pdf/ca89cfe2-a294-3989-1c42-9f5468466bd2',
    'Risposta n. 58 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+58_2023.pdf/13e7084a-1c34-c1ba-08a6-236ab1d1f0e7',
    'Risposta n. 57 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+57_2023.pdf/a786fd7e-bd8f-5795-f875-45065fbc9086',
    'Risposta n. 56 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+56_2023.pdf/92328b04-3493-1113-1d07-e09ff1c6964f',
    'Risposta n. 55 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+55_2023.pdf/e5c7e222-8f5c-5ed6-9a84-50fbba783d92',
    'Risposta n. 54 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+54_2023.pdf/b3ef0097-6d21-5aad-62c2-f98cc0016630',
    'Risposta n. 53 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+53_2023.pdf/68ad4a33-0572-a73c-ddd4-0484b301c121',
    'Risposta n. 52 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+52_2023.pdf/aca30bd0-81a8-abfd-4cac-de5e28397d1c',
    'Risposta n. 51 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+51_2023.pdf/d1802596-aec3-11b3-1db1-d0e05977f7bf',
    'Risposta n. 50 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+50_2023.pdf/2baad9a1-4998-61a7-1554-426232be1f4d',
    'Risposta n. 49 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+49_2023.pdf/0ce8c4f9-07c4-53a5-4273-2c37baf701d4',
    'Risposta n. 48 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+48_2023.pdf/92e900a5-ec9a-29b6-dc7e-e96cab411984',
    'Risposta n. 47 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+47_2023.pdf/ab6dbfcb-f60f-e383-e107-33a0d94bfe8b',
    'Risposta n. 46 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+46_2023.pdf/2149700a-0c38-0561-1f54-e5be4cd8ae88',
    'Risposta n. 45 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+45_2023.pdf/6cec55f1-c1ac-8848-fcf0-d306f8ca17e6',
    'Risposta n. 44 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+44_2023.pdf/aca99fbc-366c-2ae7-a6d2-e40df1e386ab',
    'Risposta n. 43 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+43_2023.pdf/a4322bdd-8d5f-bcfb-444c-b5204283d903',
    'Risposta n. 42 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+42_2023.pdf/213e40ec-ecdb-7832-4e71-e502dbd05a88',
    'Risposta n. 41 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+41_2023.pdf/30dbf052-33db-57da-9d16-1e665487087a',
    'Risposta n. 40 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+40_2023.pdf/a5bcccf0-b335-cc9d-df61-eb952afad93f',
    'Risposta n. 39 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+39_2023.pdf/46a8e958-4723-e4d3-458e-cb0936eea6e7',
    'Risposta n. 38 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+38_2023.pdf/6a0fccb6-e1a2-44ef-6c0c-42b51d5554a7',
    'Risposta n. 37 del 17_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+37_2023.pdf/c61004fb-01c9-4390-27ac-82dcded290f6',
    'Risposta n. 36 del 16_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+36_2023.pdf/6669d117-db50-07b1-ff1a-c679ba975e4d',
    'Risposta n. 35 del 16_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+35_2023.pdf/a75196d7-5ee9-1652-76c8-ffdba70c4f2a',
    'Risposta n. 34 del 16_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+34_2023.pdf/16675055-5dfa-f418-958e-749470549870',
    'Risposta n. 33 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+33_2023.pdf/4cb7e10a-4cf1-dfba-b5df-e00f267596cd',
    'Risposta n. 32 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+32_2023.pdf/e6a26bf9-8472-fb7f-ec26-af0e6be38c2d',
    'Risposta n. 31 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+31_2023.pdf/cef1edef-3892-e9ef-390e-a42075ae1768',
    'Risposta n. 30 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+30_2023.pdf/28eb5f76-5fc2-de0f-20b1-3e052858d92b',
    'Risposta n. 29 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+29_2023.pdf/010bd6a6-4bb1-1740-cfcf-721b0206ec50',
    'Risposta n. 28 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+28_2023.pdf/e67f3c31-68a6-7356-9ad3-de1565c3715a',
    'Risposta n. 27 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+27_2023.pdf/882e3b88-d8c2-0f01-78c7-fa920d5208ea',
    'Risposta n. 26 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+26_2023.pdf/a93d2839-a97b-86d5-d5c7-131396d71bba',
    'Risposta n. 25 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+25_2023.pdf/b7e979ae-1cc1-15f4-ec0e-7072b849246e',
    'Risposta n. 24 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+24_2023.pdf/2f41e5fc-e61d-6ec9-9174-9abdf463faca',
    'Risposta n. 23 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+23_2023.pdf/6d4f5de1-1347-e9f2-b9b7-7046db204be0',
    'Risposta n. 22 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+22_2023+%281%29.pdf/b11b6629-27c5-934e-353a-5e8793d75344',
    'Risposta n. 21 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+21_2023.pdf/39c65bc6-246e-6496-e8fd-6ca5b0406b02',
    'Risposta n. 20 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+20_2023.pdf/4b170adb-0f0f-2e52-751a-673c4856813a',
    'Risposta n. 19 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+19_2023.pdf/ab7a2e6a-8548-7163-981d-bc6a4f9bc586',
    'Risposta n. 18 del 13_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+18_2023.pdf/3c90586e-0bea-8ab9-fb64-f9964e45d2bc',
    'Risposta n. 17 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+17_2023.pdf/bc624505-ebcc-6487-8ac8-f24c9df935e8',
    'Risposta n. 16 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+16_2023.pdf/d4a62040-7c17-0fe8-33c3-711635969204',
    'Risposta n. 15 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+15_2023.pdf/4206c16f-c7aa-af6a-a385-10554f0c8bd7',
    'Risposta n. 14 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+14_2023+%281%29.pdf/bf064f2e-2647-919e-e021-0ccbd2ff2098',
    'Risposta n. 13 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+13_2023.pdf/afca113b-3c80-b969-8c0b-9f75f05d728a',
    'Risposta n. 12 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+12_2023.pdf/c3655274-eefb-72de-9f07-4ed59c8637ff',
    'Risposta n. 11 del 12_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+11_2023.pdf/c8c3c39e-f7bf-982f-efb7-1548f65dac38',
    'Risposta n. 10 del 11_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+10_2023.pdf/9f4cf376-fefa-6b72-0115-2ceae885a800',
    'Risposta n. 09 del 11_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+9_2023.pdf/e1905c20-b0fa-ed19-dbd1-487d9acb9f14',
    'Risposta n. 8 del 10_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+8_2023.pdf/b740ab74-e3b0-f6f8-0a48-0cbe775b4f7a',
    'Risposta n. 7 del 10_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+7_2023.pdf/d3a773b9-af3d-a626-df52-9d293212ef6d',
    'Risposta n. 6 del 10_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+6_2023.pdf/e685b9b0-35bb-b08d-8937-7a2c3f2b8a7b',
    'Risposta n. 5 del 4_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+5_2023.pdf/d1c8b283-8687-ae7c-8765-e8067e1bd2da',
    'Risposta n. 4 del 4_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+4_2023.pdf/3e2d0d18-47ee-18a0-0f22-71b68ec054ca',
    'Risposta n. 3 del 4_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+3_2023.pdf/f08d1d43-7ac2-16f8-607a-4d07a63a329f',
    'Risposta n. 2 del 4_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+2_2023.pdf/332f5be5-9357-31c6-8615-8acd2f68ec89',
    'Risposta n. 1 del 4_01_2023.pdf':'https://www.agenziaentrate.gov.it/portale/documents/20143/4913743/Risposta+n.+1_2023.pdf/3d6dbe07-56ce-8588-658c-004c334ec2cc'
}

# Function to send feedback email
def send_email(feedback, conversation):
    to_email = "work.paolopiacenti@gmail.com"
    subject = "RAG Feedback - Tax bot"

    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject

    # Construct the email body
    email_body = f"User Feedback:\n{feedback}\n\nConversation History:\n{conversation}"
    message.attach(MIMEText(email_body, "plain"))

    try:
        # Sending the mail using Gmail's SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, email_password)  # Use the app password loaded from env variable
        text = message.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        st.success("Feedback submitted and email sent successfully!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")


# Function to make API request
def get_bot_response(question, session_id):
    url = "https://chat-api-1087014169033.europe-west1.run.app/ask"
    headers = {"Content-Type": "application/json"}
    data = {
        "question": question,
        "session_id": session_id
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Initialize session state for the conversation and feedback
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'feedback_given' not in st.session_state:
    st.session_state['feedback_given'] = False
if 'feedback_text' not in st.session_state:
    st.session_state['feedback_text'] = ""
if 'input_key' not in st.session_state:
    st.session_state['input_key'] = str(uuid.uuid4())  # Use a unique key for each session

# Chat display function with chat bubbles
def display_chat():
    # Container to hold chat history and autoscroll
    chat_container = st.empty()
    with chat_container.container():
        for message in st.session_state['history']:
            if message["type"] == "user":
                st.markdown(f"""
                    <div class='message-row'>
                        <div class='icon'>
                            <img src='https://img.icons8.com/color/48/000000/user-male-circle--v1.png' width='40' />
                        </div>
                        <div class='message user-message'>
                            {message['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class='message-row'>
                        <div class='icon'>
                            <img src='https://img.icons8.com/color/48/000000/robot-2.png' width='40' />
                        </div>
                        <div class='message bot-message'>
                            {message['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        # Scroll to the latest message
        st.markdown(f"<div id='chat-end'></div>", unsafe_allow_html=True)
        st.markdown(f"<script>document.getElementById('chat-end').scrollIntoView();</script>", unsafe_allow_html=True)

# Inject CSS for sticky input and chat bubble styling with dark mode support
st.markdown("""
    <style>
    .message-row {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .icon {
        flex-shrink: 0;
        margin-right: 10px;
    }
    .message {
        padding: 10px;
        border-radius: 10px;
        max-width: 80%;
    }
    .user-message {
        background-color: #daf7dc;
        color: #000; /* Ensure text is readable */
        text-align: left;
        animation: fadeIn 0.5s;
    }
    .bot-message {
        background-color: #f0f0f5;
        color: #000; /* Ensure text is readable */
        text-align: left;
        animation: fadeIn 0.5s;
    }
    @media (prefers-color-scheme: dark) {
        .user-message {
            background-color: #2e7d32; /* Darker green for dark mode */
            color: #fff; /* White text for contrast */
        }
        .bot-message {
            background-color: #424242; /* Darker gray for dark mode */
            color: #fff; /* White text for contrast */
        }
        .fixed-input {
            background-color: #333; /* Darker input box in dark mode */
            color: #fff; /* White text */
        }
    }
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
    }
    .fixed-input {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: white;
        padding: 10px;
        z-index: 999;
        border-top: 2px solid #ccc;
    }
    </style>
    """, unsafe_allow_html=True)


# Title
st.title("🤖 Assistente AI Diritto Tributario")

# Introductory paragraph
st.markdown("""
**Ciao!** ti presentiamo un _prototipo_ del nostro Assistente AI sul ***Diritto Tributario***.
Questo Bot è in grado di basare le proprie risposte sulle *Circolari*, sui *Provvedimenti*, sulle *Risoluzioni*, e sulle
*Risposte* del ministero per gli anni 2023 e 2024.

*Note*: Questo bot va inteso come un prototipo, e non è garantita la presenza esaustiva delle fonti tantomento la correttezza delle risposte

**Creato con passione dall'** [**Ing. Paolo Piacenti**](https://www.linkedin.com/in/paolopiacenti/) e dall'[Avv. Francesco Venezia](https://it.linkedin.com/in/avvocato-francesco-venezia)

""")

# Display chat history
display_chat()

# Create a fixed input box at the bottom of the screen
input_container = st.container()

# Input for user's query (Submit on ENTER)
with input_container:
    user_input = st.text_input(
        "Ask a question",
        key=st.session_state['input_key'],
        placeholder="Type your message here...",
        on_change=lambda: st.session_state.update({"send_button": True}),
        args=()
    )

# Process the input when the button or ENTER key is pressed
if "send_button" in st.session_state and st.session_state['send_button']:
    # Add user message to the conversation
    if user_input:
        st.session_state['history'].append({"type": "user", "content": user_input})

        # Show a loading spinner while waiting for bot response
        with st.spinner("🤖 Bot is thinking..."):
            time.sleep(1)  # Simulate a short delay for effect
            try:
                # Call the chatbot API to get the response
                result = get_bot_response(user_input, st.session_state.session_id)
                answer = result['answer']
                sources = result['sources']

                # If the answer is not "I don't know.", include sources as clickable links
                if answer.lower() != "i don't know.":
                    # Remove duplicate sources
                    sources = list(set(sources))
                    if sources:
                        sources_text = "\n\n**Sources:**\n" + "\n".join([f"- [{source}]({source_mapping.get(source, '#')})" for source in sources])
                        answer += sources_text

                # Add bot message to the conversation
                st.session_state['history'].append({"type": "bot", "content": answer})

            except Exception as e:
                st.error(f"An error occurred: {e}")

        # Clear the input field after submission
        st.session_state['input_key'] = str(uuid.uuid4())  # Generate a new key to reset the input field
        st.session_state['send_button'] = False  # Reset the send button state

        # Rerun to update the displayed conversation
        st.experimental_rerun()

# Sidebar for feedback submission
with st.sidebar:
    st.subheader("End Session and Provide Feedback")

    # Show feedback input if feedback not already given
    if not st.session_state['feedback_given']:
        st.session_state['feedback_text'] = st.text_area("Please provide your feedback:", value=st.session_state['feedback_text'])

        # Submit feedback button
        if st.button("Submit Feedback", key="feedback_button"):
            if st.session_state['feedback_text']:
                # Construct the conversation history as a string
                conversation = "\n".join([f"{msg['type'].capitalize()}: {msg['content']}" for msg in st.session_state['history']])

                # Send the email with the feedback and conversation
                send_email(st.session_state['feedback_text'], conversation)

                # Mark feedback as given
                st.session_state['feedback_given'] = True
            else:
                st.warning("Please enter some feedback before submitting.")
    else:
        st.info("Feedback already submitted. Thank you!")
