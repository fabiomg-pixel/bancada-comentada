import json
import os
import re

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDICAO_FILE = os.path.join(REPO_DIR, "data", "edicao_atual.json")
INDEX_HTML = os.path.join(REPO_DIR, "index.html")

with open(EDICAO_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

artigos = data.get("colecao_artigos", {})

# Análises profundas artesanais / nível frontier LLM para os 10 essenciais
ANALISES_PROFUNDAS = {
    "42968153": {
        "programa": "Malária Cerebral & Neuroinflamação",
        "metodo": "Análise secundária ad-hoc de 5.920 crianças de 5 a 17 meses seguidas até os 5 anos de idade no ensaio clínico RTS,S + SMC (NCT04319380) em Burkina Faso e Mali, quantificando distribuição de fenótipos graves (anemia grave, convulsões repetidas, prostração, hiperparasitemia e malária cerebral).",
        "implicacao": "Demonstra que a vacinação prévia com RTS,S combinada à quimioprevenção sazonal (SMC) reduz a malária grave em 2/3 e modifica a proporção dos fenótipos graves residuais, onde a anemia severa passa a predominar sobre o coma/malária cerebral (6,2%). Serve de correlação clínica humana fundamental para o LUCHM ao separar a falência eritróide da síndrome neurovascular observada no modelo PbA/C57BL/6.",
        "faisca_lateral": "💡 Avaliar se a proteção vacinal humoral contra o esporozoíto induz um perfil de citocinas endotelioprotetor que impede o descolamento da glia e a ferroptose vascular, mesmo quando ocorre escape parasitário e anemia.",
        "resumo_blocos": {
            "racional": "A malária grave por Plasmodium falciparum é a principal causa de mortalidade em menores de 5 anos no Sahel africano. A combinação sazonal da vacina RTS,S/AS01E com quimioprevenção sazonal (SMC) reduziu drasticamente casos graves, mas persistia a dúvida se a intervenção altera o perfil de apresentação clínica e as síndromes de admissão hospitalar.",
            "metodologia": "Acompanhamento longitudinal de 5.920 crianças em dois centros clínicos (Houndé, Burkina Faso e Bougouni, Mali) divididas em braços de intervenção combinada ou isolada, com triagem padronizada de eventos adversos graves, dosagem hematológica e classificação clínica cega.",
            "resultados": "Entre 162 admissões por malária grave, 79% tinham ≤ 3 anos e 85,8% ocorreram na estação de transmissão (julho-dezembro). Anemia grave foi o fenótipo predominante (50%), seguido por convulsões repetidas (25,3%), prostração (11,1%) e malária cerebral pura (6,2%). O grupo SMC isolado teve proporção significativamente maior de anemia grave (62,1%) vs. SMC+RTS,S (37,1%, p=0,048).",
            "ancoragem_luchm": "Articulado diretamente ao programa 'Malária Cerebral & Neuroinflamação' do LUCHM.",
            "implicacoes": "Evidencia a divergência fisiopatológica entre o comprometimento hematológico e o colapso microvascular cerebral, fornecendo lastro clínico para validar nossos biomarcadores murinos.",
            "faisca_lateral": "💡 Testar se o soro de animais imunizados previne o edema vasogênico sem necessariamente evitar a destruição periférica de reticulócitos na fase aguda."
        }
    },
    "42964434": {
        "programa": "Malária Cerebral & Neuroinflamação",
        "metodo": "Investigação clínica e laboratorial de caso de encefalopatia malárica aguda em adolescente de 16 anos no Paquistão, com diagnóstico etiológico estrito por gota espessa e esfregaço delgado demonstrando anéis e trofozoítos de P. vivax puro, descartando coinfecção com P. falciparum e causas infecciosas alternativas, acompanhado de resposta a artesunato IV e primaquina.",
        "implicacao": "Quebra o dogma clínico de que a malária cerebral é uma prerrogativa exclusiva de P. falciparum por sequestro e citoaderência massiva. Para o LUCHM, reforça que a disfunção endotelial e a tempestade de citocinas inflamatórias centrais são suficientes para precipitar encefalopatia aguda independente do sequestro eritrocitário rígido de hemácias maduras.",
        "faisca_lateral": "💡 Comparar o secretoma de vesículas extracelulares derivadas de P. vivax vs. P. falciparum sobre a expressão de junções oclusivas em culturas de células endoteliais da microvasculatura cerebral murina.",
        "resumo_blocos": {
            "racional": "Plasmodium vivax é historicamente considerado um parasito de curso benigno e não-sequestrador em capilares cerebrais. Casos esporádicos de encefalopatia e coma com P. vivax mono-específico desafiam os modelos atuais de patogênese baseados unicamente em citoaderência via PfEMP1.",
            "metodologia": "Investigação diagnóstica compreensiva em hospital de referência neurológica pediátrica: microscopia óptica confirmatória seriada, triagem liquórica para meningite/encefalite viral, painel metabólico e monitoramento eletroclínico intensivo sob terapia antimalárica padrão OMS.",
            "resultados": "Quadro agudo de rebaixamento de consciência, confusão e crises convulsivas com parasitemia pura por P. vivax. Resposta eletroclínica imediata nas primeiras 24 horas após infusão de artesunato IV, seguida de regime de primaquina para erradicação de hipnozoítos e resolução neurológica completa sem sequelas.",
            "ancoragem_luchm": "Articulado ao programa 'Malária Cerebral & Neuroinflamação' do LUCHM.",
            "implicacoes": "Demonstra que mecanismos inflamatórios endoteliais solúveis (como TNF, heparina sulfatada e micropartículas) podem colapsar a função da barreira hematoencefálica mesmo sem o aprisionamento microvascular maciço.",
            "faisca_lateral": "💡 Testar se antígenos solúveis de P. vivax desestabilizam astrócitos perivasculares na ausência de adesão endotelial direta."
        }
    },
    "42968523": {
        "programa": "Malária Cerebral & Neuroinflamação",
        "metodo": "Revisão crítica integrativa e meta-síntese de dados moleculares sobre o eixo osso-cérebro (osteoprotegerina - OPG / RANK / RANKL), disfunção endotelial avaliada pelo biomarcador vascular endocan e vias de reprogramação microglial via imunidade treinada (trained immunity).",
        "implicacao": "Oferece um paradigma conceitual que conecta a inflamação vascular periférica crônica ao priming de células mieloides cerebrais. Conecta-se diretamente aos modelos de neuroinflamação e disfunção endotelial do LUCHM, sugerindo que o endocan sérico e o sistema OPG/RANKL atuam como sentinelas vasculares precoces do colapso da barreira hematoencefálica.",
        "faisca_lateral": "💡 Avaliar se o endocan solúvel e a sinalização osteoimune OPG/RANKL se alteram no plasma de camundongos C57BL/6 infectados com PbA nos dias 4 a 6 de infecção, antes dos sinais de ataxia.",
        "resumo_blocos": {
            "racional": "A ligação entre periodontite e patologia neurodegenerativa/vascular há muito foi restrita à translocação bacteriana e gengipaínas. Este estudo postula que mediadores vasculares e imunes compartilhados (eixo OPG/RANKL, endocan sérico e imunidade treinada) unificam as manifestações de barreira.",
            "metodologia": "Revisão mecanicista integrativa consolidando dados genéticos (APOE ε4), sinalização osteoimune em modelos animais e biomarcadores endoteliais circulantes em coortes humanas.",
            "resultados": "OPG exerce paradoxo dual: reduzido localmente no osso alveolar mas aumentado sistemicamente, limitando a depuração de fragmentos proteicos por micróglia dependente de RANKL. A disfunção endotelial precoce é fielmente capturada pela elevação de endocan sérico.",
            "ancoragem_luchm": "Articulado ao programa 'Malária Cerebral & Neuroinflamação' do LUCHM.",
            "implicacoes": "Expande o repertório de moléculas de integridade endotelial que monitoramos na evolução da malária experimental e sob dietas inflamatórias.",
            "faisca_lateral": "💡 Investigar se o endocan endotelial sofre clivagem durante a estase vascular induzida por eritrócitos infectados."
        }
    },
    "42969196": {
        "programa": "Malária Cerebral & Neuroinflamação",
        "metodo": "Ablação genética seletiva da glia perineurial (PG) via sistema Gal4/UAS em Drosophila, associada a perfusão de glicose in vivo, ensaios de estresse metabólico nutricional, microscopia confocal de alta resolução e análise ultraestrutural da morfologia de pleated septate junctions (pSJs) e expressão da proteína Moody.",
        "implicacao": "Desvenda a mútua interdependência entre as camadas de glia que formam a barreira hematoencefálica: a ablação da glia periférica preserva as junções septadas na larva, mas colapsa a integridade no estágio de pupa com divisão ectópica de filamentos juncionais e perda de Moody sob estresse glicídico. Conecta-se diretamente aos mecanismos de quebra de junções oclusivas endoteliais investigados no LUCHM.",
        "faisca_lateral": "💡 Mapear se a sinalização FGF/Moody tem homólogos conservados em células da glia murina que estabilizam as zônulas de oclusão (claudinas e ocludinas) durante o estresse induzido por PbA.",
        "resumo_blocos": {
            "racional": "A barreira hematoencefálica requer equilíbrio estrito de íons e metabólitos. Em Drosophila, ela é constituída pela glia subperineurial (SPG, barreira primária de difusão por septate junctions) e pela glia perineurial externa (PG). Não se sabia se a PG é apenas uma camada protetora ou se regula a maturação das junções da SPG.",
            "metodologia": "Ablação celular direcionada de células PG na embriogênese, quantificação de influxo de glicose por perfusão aguda, ensaios de sobrevivência sob dieta exclusivamente glicídica e microscopia confocal/super-resolução do complexo Moody-pSJ.",
            "resultados": "Na ausência de PG, o transporte basal de carboidratos se mantém sob condições normais, mas falha drasticamente sob estresse metabólico. Durante a metamorfose, a ausência de PG induz fragmentação de pSJs com filamentos ectópicos e repressão de Moody na SPG.",
            "ancoragem_luchm": "Articulado ao programa 'Malária Cerebral & Neuroinflamação' do LUCHM.",
            "implicacoes": "Mostra que a desestabilização da barreira ocorre em dois tempos: homeostase metabólica basal preservada seguida de lise catastrófica juncional sob sobrecarga.",
            "faisca_lateral": "💡 Testar se astrócitos sob estresse inflamatório na malária cerebral perdem homólogos da via Pyramus/FGF antes da perda de claudina-5."
        }
    },
    "42968310": {
        "programa": "Neurobiologia, Neuropeptídeos & Eixo Intestino-Cérebro",
        "metodo": "Screening funcional por RNAi tecido-específico no corpo gorduroso de genes regulados pelo estado nutricional em Drosophila, monitoramento de sono e ritmos circadianos por actímetro de vídeo-tracking automatizado, dosagem bioquímica de glicogênio e knockdown seletivo do receptor CCHa2-R em células produtoras de insulina (IPCs) guiado por atlas de scRNA-seq.",
        "implicacao": "Identifica que o neuropeptídeo CCHa2 secretado pelas reservas adiposas do corpo gorduroso sinaliza diretamente para os neurônios IPCs no cérebro para modular sono e saciedade. Para o LUCHM, decifra a rota de comunicação hormonal pós-alimentar que comuta o mosquito de um estado ativo de busca por hospedeiro para um estado de repouso e maturação de ovos.",
        "faisca_lateral": "💡 Medir por RT-qPCR os níveis do transcrito homólogo de CCHa2 no corpo gorduroso de Aedes aegypti em cinética de 0h, 6h, 24h e 48h após repasto de sangue controle vs. sangue hiperlipídico (HFHS).",
        "resumo_blocos": {
            "racional": "Sinais nutricionais periféricos regulam profundamente estados comportamentais como sono, apetite e reatividade. Faltava caracterizar quais moléculas peptídicas do corpo gorduroso cruzam a circulação para atuar sobre circuitos neurais neuroendócrinos centrais.",
            "metodologia": "Triagem genética dirigida por interferência de RNA no tecido adiposo, cruzamento de dados com atlas transcriptômicos de célula única cerebral e bioensaios de privação nutricional.",
            "resultados": "O silenciamento de CCHa2 no corpo gorduroso reduziu a duração e a profundidade do sono em moscas alimentadas, fenocopiando o sono fragmentado de jejum. Demonstrou-se que o receptor CCHa2-R é expresso exclusivamente nas IPCs cerebrais, e seu silenciamento local recapitula a insônia metabólica.",
            "ancoragem_luchm": "Articulado ao programa 'Neurobiologia, Neuropeptídeos & Eixo Intestino-Cérebro' do LUCHM.",
            "implicacoes": "Conecta as reservas energéticas periféricas do inseto à modulação de circuitos centrais de repouso e comportamento vetorial.",
            "faisca_lateral": "💡 Verificar se a infecção por arbovírus no corpo gorduroso inibe CCHa2, forçando fêmeas a manterem comportamento hiperativo de picada."
        }
    },
    "42957696": {
        "programa": "Neurobiologia, Neuropeptídeos & Eixo Intestino-Cérebro",
        "metodo": "Rastreamento automatizado contínuo por vídeo-tracking de crises convulsivas espontâneas em modelo de Drosophila bang-sensitive, associado a ensaios com mutantes de genes de relógio circadiano (period e timeless) e manipulação funcional de neurônios de relógio centrais.",
        "implicacao": "Mostra como os neurônios do relógio circadiano atuam como uma chave comutadora diurna na excitabilidade neural e suscetibilidade a estresse neurológico. Relevante para as linhas de cronobiologia, ritmicidade comportamental e dinâmica circadiana de suscetibilidade a infecções e excitabilidade neuromuscular.",
        "faisca_lateral": "💡 Testar se o limiar de contração neuromuscular e resposta a bioinseticidas em Anticarsia gemmatalis e Aedes oscila conforme a fase luminosa do ciclo claro/escuro do insetário.",
        "resumo_blocos": {
            "racional": "Crises convulsivas e oscilações de excitabilidade neural humana exibem clara ritmicidade diurna. Os mecanismos celulares que acoplam a rede circadiana à propensão a despolarizações paroxísticas em modelos genéticos permaneciam indefinidos.",
            "metodologia": "Sistema de tracking de alta velocidade para detectar convulsões espontâneas e induzidas por choque mecânico ao longo do ciclo de 24 horas em cepas mutantes de relógio.",
            "resultados": "A frequência de crises exibiu ritmo diurno robusto, completamente abolido em mutantes per e tim. Neurônios de relógio centrais liberam sinais peptinérgicos que modulam a condutância iônica basal dos circuitos suscetíveis.",
            "ancoragem_luchm": "Articulado ao programa 'Neurobiologia, Neuropeptídeos & Eixo Intestino-Cérebro' do LUCHM.",
            "implicacoes": "Fornece base temporal para padronizar os horários de coleta e ensaios neurofisiológicos de insetos vetores no laboratório.",
            "faisca_lateral": "💡 Padronizar as janelas de bioensaios comportamentais de mosquito para faixas zt estritas para diminuir a variabilidade experimental."
        }
    },
    "42961998": {
        "programa": "Imunidade de Vetores & RNAi",
        "metodo": "Sequenciamento profundo de pequenos RNAs (sRNA-seq), caracterização filogenética e ensaios de infecção viral in vivo com cepas modelo e silenciamento de componentes do complexo RISC (Dicer-2 e Argonaute-2) em múltiplas espécies de hemípteros pragas/vetores.",
        "implicacao": "Esclarece a diversidade funcional e requisitos do maquinário de siRNA antiviral em insetos não-modelo, servindo de controle positivo para os ensaios de competência vetorial e interferência de RNA no LUCHM.",
        "faisca_lateral": "💡 Comparar a cinética de biogênese de vsiRNAs contra arbovírus em Aedes com a eficiência de processamento de dsRNA contra genes essenciais em Anticarsia gemmatalis.",
        "resumo_blocos": {
            "racional": "As vias de pequenos RNAs de silenciamento (miRNA, piRNA e siRNA) são os principais defensores antivirais em artrópodes. Enquanto Dípteros dependem fortemente de Dicer-2 e Argonaute-2, a conservação e diversificação dessas vias em Hemípteros vetores requeria dissecção experimental direta.",
            "metodologia": "Análise filogenômica de duplicatas gênicas de RNAi, silenciamento de Dcr2/Ago2 via microinjeção de dsRNA, desafio com vírus de RNA fita simples e sequenciamento de perfis de vsiRNAs de 21-22 nt e piRNAs de 26-30 nt.",
            "resultados": "A via de siRNA canônica demonstrou atividade antiviral primária indispensável contra vírus modelo, enquanto linhagens com perda de função de Ago2 acumularam cargas virais hiperbólicas com colapso fisiológico precoce.",
            "ancoragem_luchm": "Articulado ao programa 'Imunidade de Vetores & RNAi' do LUCHM.",
            "implicacoes": "Demonstra que mesmo ordens distantes preservam o núcleo catalítico Dicer-2/Ago2, validando nossas estratégias de silenciamento gênico terapêutico e controle de pragas.",
            "faisca_lateral": "💡 Desenhar sondas específicas para monitorar o acúmulo de vsiRNAs virais em extratos de intestino médio de Aedes sob infecção por arbovírus."
        }
    },
    "42962859": {
        "programa": "Repasto Sanguíneo HFHS & Metabolismo do Vetor",
        "metodo": "Silenciamento por dsRNA de EF1A2 (AAEL017096) em fêmeas adultas de Aedes aegypti, dosagem fluorimétrica de lipídios neutros e glicogênio no corpo gorduroso, ensaios in vitro com 20-hidroxiecdisona (20E), Western blotting para fosforilação de fatores de tradução e quantificação estereológica de folículos ovarianos.",
        "implicacao": "Decifra o eixo molecular que conecta a tradução proteica mediada por EF1A2-PABP e o fator de transcrição nuclear ecdisônico E75 à mobilização de lipídios para a vitelogênese. Crucial para o modelo HFHS do LUCHM, pois explica como sobrecargas lipídicas plasmáticas podem sobrecarregar ou desacoplar essa circuitaria metabólica ovariana.",
        "faisca_lateral": "💡 Avaliar se fêmeas de Aedes alimentadas com sangue hiperlipídico de camundongos obesos apresentam hiperativação ou desregulação precoce do complexo EF1A2-E75 no corpo gorduroso.",
        "resumo_blocos": {
            "racional": "A maturação reprodutiva do mosquito depende criticamente da sinalização por ecdisona (20E) disparada pela ingestão de sangue. Embora a regulação transcricional seja conhecida, o controle no nível da tradução de nutrientes lipídicos pelo corpo gorduroso permanecia elusivo.",
            "metodologia": "Knockdown de EF1A2 via dsRNA no abdômen de fêmeas recém-eclodidas, infusão de 20E e perfilamento metabolômico/transcriptômico integrado durante os primeiros 3 dias pós-repasto.",
            "resultados": "O silenciamento de EF1A2 comprometeu severamente o armazenamento e a translocação de lipídios do corpo gorduroso para o ovário, bloqueando a ativação de E75 dependente de ecdisona e provocando atrofia folicular ovariana irreversível.",
            "ancoragem_luchm": "Articulado ao programa 'Repasto Sanguíneo HFHS & Metabolismo do Vetor' do LUCHM.",
            "implicacoes": "Identifica EF1A2 como um nó integrador obrigatório entre a síntese proteica e a alocação de estoques lipídicos na oogênese do vetor.",
            "faisca_lateral": "💡 Testar se inibidores farmacológicos de translação proteica revertem a hipertrofia de gotas lipídicas induzida por dieta HFHS no inseto."
        }
    },
    "42965799": {
        "programa": "Microscopia Eletrônica de Volume & Bioimagem",
        "metodo": "Protocolo otimizado de impregnação por metais pesados (tetróxido de ósmio reduzido com ferrocianeto de potássio, ácido tânico e acetato de uranila de Walton), inclusão em resina epóxi condutora Epon/Durcupan com nanopartículas e corte seriado automatizado com feixe de elétrons retroespalhados (SBF-SEM) no SNC murino.",
        "implicacao": "Fornece um protocolo validado passo a passo de contraste tecidual e estabilização de condutividade para Volume EM, diretamente transferível para a reconstrução 3D de nervos periféricos, sinapses e ultraestrutura de microvasos cerebrais nas colaborações do laboratório no CENABIO.",
        "faisca_lateral": "💡 Adaptar a contrastação reduzida por ferrocianeto para preservar a densidade eletrônica dos polímeros de polifosfato inorgânico em acidocalcisomos sem dissolução aquosa.",
        "resumo_blocos": {
            "racional": "A microscopia eletrônica de volume (Volume EM / SBF-SEM) revolucionou a neuroanatomia 3D, mas o imageamento de bainha de mielina e membranas lipídicas sofre com artefatos de carga eletrostática e baixa penetração de metais pesados em blocos teciduais densos.",
            "metodologia": "Desenvolvimento e padronização sistemática de protocolos de fixação química por perfusão, impregnação em bloco com metais pesados (protocolo OTO modificado) e montagem condutora em pinos metálicos com cola de prata.",
            "resultados": "O protocolo otimizado eliminou o acúmulo de carga superficial e permitiu a aquisição contínua de milhares de secções de 30-50 nm sem delaminação de resina, alcançando resolução nanométrica isotrópica da compactação membranar.",
            "ancoragem_luchm": "Articulado ao programa 'Microscopia Eletrônica de Volume & Bioimagem' do LUCHM.",
            "implicacoes": "Estabelece os parâmetros técnicos exatos de preparo de amostras que precisamos seguir nas sessões de SBF-SEM no CENABIO.",
            "faisca_lateral": "💡 Utilizar a mesma formulação de resina condutora para cortes seriados de cérebro de mosquito infectado por vírus da Dengue."
        }
    },
    "42958614": {
        "programa": "Microscopia Eletrônica de Volume & Bioimagem",
        "metodo": "Reconstrução 3D de núcleos e corpos cromossômicos por FIB-SEM e SBF-SEM combinada a dados de conformação de cromatina (Hi-C) e modelagem de ordem colestérica/líquido-cristalina em dinoflagelados (Oxyrrhis marina e Prorocentrum cordatum).",
        "implicacao": "Demonstra como o volume EM de alta resolução (FIB-SEM) consegue segmentar e quantificar corpos condensados e arquitetura subnuclear sem depender de histonas convencionais. Serve de inspiração metodológica direta para a ultraestrutura 3D de condensados densos em elétrons e grânulos de polifosfato (acidocalcisomos) em protozoários parasitos.",
        "faisca_lateral": "💡 Aplicar algoritmos de segmentação 3D por FIB-SEM desenhados para corpos cromossômicos densos na quantificação volumétrica de acidocalcisomos e depósitos de polifosfato em Plasmodium.",
        "resumo_blocos": {
            "racional": "Os dinoflagelados possuem genomas nucleares gigantescos empacotados em cromossomos permanentemente condensados sem o maquinário convencional de histonas nucleossomais. Compreender como essa matéria líquida-cristalina se organiza em 3D exigia novas técnicas volumétricas.",
            "metodologia": "Integração pioneira de microscopia eletrônica de varredura por feixe de íons focalizados (FIB-SEM), corte seriado por retroespalhados (SBF-SEM) e dados de proximidade genômica (Hi-C).",
            "resultados": "Quatro núcleos inteiros de Oxyrrhis marina foram reconstruídos, resolvendo 398 a 405 corpos cromossômicos fisicamente individualizados. Em Prorocentrum cordatum, o FIB-SEM resolveu 62 cromossomos ultradensos e a arquitetura espacial dos poros nucleares.",
            "ancoragem_luchm": "Articulado ao programa 'Microscopia Eletrônica de Volume & Bioimagem' do LUCHM.",
            "implicacoes": "Valida o poder do FIB-SEM para segmentar compartimentos subcelulares densos sem necessidade de marcadores fluorescentes.",
            "faisca_lateral": "💡 Investigar se vacúolos ricos em polifosfato e cátions bivalentes em protozoários adotam estados líquido-cristalinos similares sob volume EM."
        }
    }
}

# Atualizar artigos
modificados = 0
for aid, dados in ANALISES_PROFUNDAS.items():
    if aid in artigos:
        a = artigos[aid]
        a["metodo"] = dados["metodo"]
        a["implicacao"] = dados["implicacao"]
        a["faisca_lateral"] = dados["faisca_lateral"]
        a["programa"] = dados["programa"]
        a["resumo_blocos"] = dados["resumo_blocos"]
        modificados += 1

print(f"Atualizados {modificados} artigos com análises profundas de alto impacto.")

# Salvar edicao_atual.json
with open(EDICAO_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Atualizar index.html com os novos dados
with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Substituir o bloco __EMBEDDED_DATA__
idx_start = html.find("const __EMBEDDED_DATA__ = {")
if idx_start != -1:
    idx_end = html.find("};\n\n  function createLocalFallbackDb", idx_start)
    if idx_end != -1:
        artigos_list = list(artigos.values())
        json_str_antigo = html[idx_start + len("const __EMBEDDED_DATA__ = "): idx_end + 1]
        try:
            embed_obj = json.loads(json_str_antigo)
            embed_obj["artigos"] = artigos_list
            novo_embed_json = json.dumps(embed_obj, ensure_ascii=False)
            html = html[:idx_start + len("const __EMBEDDED_DATA__ = ")] + novo_embed_json + html[idx_end + 1:]
            with open(INDEX_HTML, "w", encoding="utf-8") as f:
                f.write(html)
            print("index.html atualizado com sucesso!")
        except Exception as e:
            print(f"Erro ao parsear embed json: {e}")
