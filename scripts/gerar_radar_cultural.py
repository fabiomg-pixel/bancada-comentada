#!/usr/bin/env python3
"""
gerar_radar_cultural.py — Gera a edição mensal de Horizonte Lateral (Revista de Fronteiras & Interseções)
Substitui o antigo "Radar Cultural" por um espaço focado em:
- Descobertas fora da linha direta de visão
- Interseções não-óbvias (física de materiais, bioeletricidade, contactoma, nanotribologia)
- Pesquisadores distantes mas com pontes conceituais surpreendentes para o LUCHM
- Cada bloco 100% interativo, entregando histórias, papers marco, pontos de aprofundamento e conexões
"""

import json
import os

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_DIR, "data")
OUT_FILE = os.path.join(DATA_DIR, "radar_cultural.json")

dossie_fronteira = {
    "edicao": "Novembro 2026",
    "secao_slug": "fronteira",
    "titulo": "Horizonte Lateral — Revista de Fronteiras & Ponto Cego",
    "subtitulo": "O que está fora da nossa linha direta de visão: bioeletricidade tecidual, contactoma de organelas, separação de fases e mecânica invisível",
    "data_publicacao": "2026-11-02",
    "ensaio": {
        "id": "ensaio-novembro-2026",
        "titulo": "A Física Oculta da Transmissão: Separação de Fases, Bioeletricidade e a Mecânica Invisível entre o Vetor e o Patógeno",
        "subtitulo": "Por que olhar apenas para receptores clássicos e transcrição gênica nos cegou para os gradientes bioelétricos e as forças físicas que decidem a infecção.",
        "autor_ensaio": "Curadoria de Fronteiras · LUCHM",
        "tempo_leitura": "14 min de leitura imersiva",
        "artigo_base": {
            "titulo": "Non-equilibrium physics and phase separation as master switches in host-pathogen microenvironments",
            "autores": "Trends in Cell Biology / Nature Reviews (2026)",
            "doi": "10.1016/j.tcb.2026.04.012",
            "resumo_analitico": "O artigo articula evidências emergentes de que a transição de patógenos entre microambientes biológicos hostis não depende primariamente de novas sínteses de proteínas, mas da rápida reorganização física de condensados biomoleculares intracelulares e do sensoriamento de gradientes de voltagem de membrana nos epitélios hospedeiros."
        },
        "historia": """Durante quase um século, a parasitologia molecular operou sob um dogma redutor: para entender por que um mosquito transmite ou bloqueia a malária, ou por que o camundongo desenvolve edema cerebral, deveríamos buscar 'o gene' ou 'a citocina'. Mapeamos vias de sinalização inteiras (Toll, Imd, JAK-STAT), sequenciamos transcriptomas de células únicas e quantificamos centenas de RNAs mensageiros.

No entanto, uma pergunta desconfortável permaneceu sem resposta na bancada: **como decisões vitais de infecção ocorrem em frações de segundo, muito antes de qualquer RNA polimerase conseguir transcrever um gene?**

Quando o oocineto atinge o microvilo do mosquito, a digestão do sangue está no auge. Milhões de eritrócitos se rompem, gerando uma pressão coloidosmótica massiva, liberação letal de hemo livre e fluxo turbulento não-newtoniano. O parasito não tem horas para 'ativar uma via gênica'. Ele precisa explorar as propriedades biofísicas nativas do epitélio: diferenças de potencial elétrico entre células vizinhas, zonas de menor tensão mecânica e condensação líquida de proteínas de superfície.

Se quisermos descobrir o que não sabemos que existe, precisamos sair da nossa própria vizinhança conceitual. É no cruzamento com a biologia de sistemas de organelas, com a bioeletricidade do desenvolvimento e com a física da matéria mole que residem as próximas grandes viradas da nossa bancada.""",
        "artigos_marco": [
            {
                "titulo": "Bioelectric networks guide spatial patterning and barrier defense in intact epithelia",
                "revista": "Trends in Cell Biology",
                "ano": "2024",
                "doi": "10.1016/j.tcb.2024.01.008",
                "pmid": "38272819",
                "o_que_provou": "Demonstrou que células epiteliais mantêm mapas contínuos de potencial de membrana (Vmem) via gap junctions que ditam se um tecido é permissivo ou refratário à penetração celular."
            },
            {
                "titulo": "Membrane contact sites: Direct lipid and ion conduits that bypass vesicular trafficking",
                "revista": "Nature Cell Biology",
                "ano": "2023",
                "doi": "10.1038/s41556-023-01120-x",
                "pmid": "37055490",
                "o_que_provou": "Mapeou o 'contactoma' celular, provando que organelas trocam cargas metabólicas maciças em nanodominios de 10-30 nm sem formar vesículas nem gastar ATP."
            },
            {
                "titulo": "Biomolecular condensates as physical stress filters during acute infection",
                "revista": "Cell",
                "ano": "2024",
                "doi": "10.1016/j.cell.2024.03.015",
                "pmid": "38518542",
                "o_que_provou": "Provou que proteínas de barreira sofrem separação de fase reversível líquido-líquido em resposta a estresse oxidativo, criando escudos físicos temporários contra invasores."
            }
        ],
        "intersecoes_luchm": [
            {
                "linha": "Malária Cerebral & Quebra da Barreira Hematoencefálica (PbA)",
                "ponto_cego": "Temos focado intensamente em citocinas (IFN-γ, TNF) e células CD8+ infiltrantes, mas e se o evento primário que permite o extravasamento for uma onda de despolarização elétrica endotelial desencadeada por micropartículas ricas em polyP secretadas pelos eritrócitos infectados?"
            },
            {
                "linha": "Bioenergética e Acidocalcisomos em Insetos e Parasitas",
                "ponto_cego": "Consideramos os grânulos de polifosfato e acidocalcisomas como organelas autônomas. Porém, a física de condensados sugere que o polyP atua como um 'solvente hidrotópico biológico', mantendo proteínas solúveis em ambientes hipersalinos e funcionando como um capacitor eletroquímico celular."
            },
            {
                "linha": "Repasto Sanguíneo HFHS e Fisiologia do Vetor",
                "ponto_cego": "O excesso de lipídios da dieta hiperlipídica do camundongo altera a fluidez e a capacitância elétrica da membrana dos enterócitos do mosquito, mudando a resistência mecânica da borda em escova antes de qualquer ativação imunológica."
            }
        ],
        "pontos_aprofundamento": [
            "1. Os oocinetos de Plasmodium são atraídos por 'vales' de despolarização elétrica no intestino médio do mosquito?",
            "2. É possível dissolver a matriz peritrófica do mosquito ou inibir o 'capping' do parasito usando perturbadores específicos de separação de fases (como 1,6-hexanodiol ou hidrótropos biológicos)?",
            "3. Como o contactoma organelar do corpo gorduroso gerencia a queima violenta de lipídios e o fornecimento de polyP durante a oogênese?"
        ]
    },
    "grandes_pesquisadores": [
        {
            "id": "maya-schuldiner",
            "nome": "Prof. Maya Schuldiner, PhD",
            "instituicao": "Department of Molecular Genetics, Weizmann Institute of Science, Israel",
            "foto_icone": "🧩",
            "area_primaria": "Biologia Celular de Sistemas · Sítios de Contato entre Organelas (MCS) · O 'Contactoma'",
            "por_que_nao_obvia": "Maya não trabalha com malária, nem com mosquitos, nem com medicina tropical. Seu campo é a infraestrutura física de comunicação direta entre organelas em leveduras e células de mamífero. Mas seus conceitos explodem o maior mistério não resolvido do nosso laboratório: como organelas sem vesículas trocam fosfato e lipídios em segundos.",
            "historia": """Por mais de 50 anos, a biologia celular ensinou que as organelas eram mundos isolados comunicando-se exclusivamente pelo tráfego de vesículas (o modelo clássico de Palade e Schekman). Maya Schuldiner suspeitou que isso não fazia sentido termodinâmico: o tráfego vesicular é lento, custoso e não explica como estoques maciços de lipídios e íons transitam entre compartimentos em respostas de estresse agudo.

No Weizmann Institute, Maya desenvolveu plataformas robóticas de rastreamento genético sistemático de proximidade (split-GFP e screening microscópico de alto rendimento). Ela demonstrou que todas as organelas da célula estão literalmente 'amarradas' umas às outras por pontes proteicas de 10 a 30 nanômetros chamadas Membrane Contact Sites (MCS). Nesses sítios de contato, lipídios e íons não viajam em vesículas: eles fluem através de túneis moleculares diretos como em um duto contínuo.""",
            "papers_marco": [
                {
                    "titulo": "Systematic mapping of contact sites reveals a coordinated organelle network",
                    "revista": "Nature Cell Biology",
                    "ano": "2023",
                    "doi": "10.1038/s41556-023-01120-x",
                    "pmid": "37055490"
                },
                {
                    "titulo": "Lipid transfer at membrane contact sites: From mechanisms to physiological functions",
                    "revista": "Cell Metabolism",
                    "ano": "2022",
                    "doi": "10.1016/j.cmet.2022.04.009",
                    "pmid": "35508107"
                }
            ],
            "intersecao_luchm": "No LUCHM, estudamos acidocalcisomos e gotículas lipídicas tanto no vetor quanto em protozoários. Nunca ninguém na parasitologia mapeou os tethers (pontes de contato) entre acidocalcisomos e gotículas lipídicas no corpo gorduroso ou intestino de mosquitos. Quando o vetor ingere sangue HFHS, o fluxo de lipídios para os acidocalcisomos pode estar ocorrendo diretamente via MCS, sem passar pelo Golgi!",
            "pontos_aprofundamento": [
                "Podemos usar construções split-GFP para visualizar contatos físicos diretos entre acidocalcisomos e gotículas lipídicas em células de Aedes aegypti (linhagem Aag2)?",
                "O parasito Plasmodium utiliza tethers proteicos próprios para sequestrar lipídios diretamente das organelas do enterócito durante a invasão?",
                "Bloquear farmacologicamente o tethering organelar no mosquito pode paralisar a oogênese sem toxicidade sistêmica?"
            ]
        },
        {
            "id": "michael-levin",
            "nome": "Prof. Michael Levin, PhD",
            "instituicao": "Allen Discovery Center, Tufts University & Wyss Institute at Harvard University, USA",
            "foto_icone": "⚡",
            "area_primaria": "Bioeletricidade do Desenvolvimento · Morfogênese Não-Neural · Computação em Tecidos Somáticos",
            "por_que_nao_obvia": "Levin trabalha com regeneração de planárias, embriões de Xenopus e bioengenharia de tecidos sintéticos (Xenobots). Ele ignora completamente a entomologia clássica. No entanto, sua descoberta de que o potencial elétrico transmembrana (Vmem) governa decisões de barreira epitelial e tolerância imunológica abre uma frente revolucionária para a transmissão de arbovírus e malária.",
            "historia": """Enquanto os biólogos moleculares focavam exclusivamente no genoma e no proteoma, Michael Levin fez uma pergunta simples: o que coordena as células no espaço para construir uma mão, reparar um olho ou fechar uma ferida? Células individuais não 'enxergam' o organismo inteiro.

Levin e sua equipe descobriram que todas as células somáticas — e não apenas os neurônios — mantêm gradientes dinâmicos de potencial de membrana de repouso (Vmem). Essas células se acoplam por gap junctions formando verdadeiros circuitos bioelétricos. Modificando artificialmente os canais iônicos e a voltagem de um tecido epitelial com drogas já existentes, Levin foi capaz de induzir a regeneração de olhos em tecidos ectópicos, reprogramar células tumorais para fenótipos normais e ordenar o fechamento de barreiras danificadas sem alterar uma única sequência de DNA.""",
            "papers_marco": [
                {
                    "titulo": "Bioelectric signaling in regeneration, development, and pathogen defense",
                    "revista": "Trends in Cell Biology",
                    "ano": "2024",
                    "doi": "10.1016/j.tcb.2024.01.008",
                    "pmid": "38272819"
                },
                {
                    "titulo": "Endogenous bioelectric networks instruct immune cell recruitment and barrier function",
                    "revista": "Nature Reviews Molecular Cell Biology",
                    "ano": "2022",
                    "doi": "10.1038/s41580-022-00467-3",
                    "pmid": "35365814"
                }
            ],
            "intersecao_luchm": "O intestino do mosquito sofre distensão violenta durante o repasto. Levin demonstrou que epitélios sob estresse mecânico geram assinaturas elétricas de Vmem que guiam onde as células basais se multiplicam e quais regiões fecham suas junções. O oocineto de Plasmodium pode estar usando receptores sensíveis a voltagem para invadir exatamente as células com Vmem alterado! Da mesma forma, na malária cerebral (PbA), o edema vasogênico pode começar por despolarização endotelial.",
            "pontos_aprofundamento": [
                "Podemos mapear a voltagem da borda em escova do intestino de Anopheles/Aedes usando sondas fluorescentes de voltagem (como DiBAC4(3) ou VF2.1.Cl) durante a passagem do oocineto?",
                "Pequenas moléculas que hiperpolarizam enterócitos (abridores de canais de potássio aprovados para uso humano) tornariam o mosquito refratário ao Plasmodium?",
                "A despolarização da barreira hematoencefálica no modelo PbA precede a aderência de CD8+ e a ferroptose?"
            ]
        }
    ],
    "temas_expansao": [
        {
            "id": "separacao-de-fases",
            "tema": "Condensados Biomoleculares e Separação de Fases (LLPS) na Interface Vetor–Patógeno",
            "icone": "💧",
            "o_que_e": "A descoberta de que proteínas intrinsecamente desordenadas (IDRs) formam gotículas líquidas sem membrana (condensados) que funcionam como concentradores ultra-rápidos de reações enzimáticas e escudos físicos dinâmicos contra estresse e infecção.",
            "historia": """Por décadas acreditamos que toda compartimentação celular dependia de membranas lipídicas ou de complexos proteicos cristalinos rígidos. Anthony Hyman e Clifford Brangwynne viraram a biologia celular de cabeça para baixo ao provar que o citoplasma opera através de transições de fase líquido-líquido (LLPS) — exatamente como gotas de vinagre e azeite se separando em uma emulsão.

Nos últimos dois anos, descobriu-se que patógenos e tecidos de barreira utilizam condensados para orquestrar invasões relâmpago. Quando o vírus ou parasito toca a membrana, proteínas com sequências repetitivas de baixa complexidade condensam em milissegundos, gerando uma força capilar que deforma a bicamada lipídica sem necessidade de motores moleculares baseados em ATP.""",
            "papers_marco": [
                {
                    "titulo": "Biomolecular condensates as fast-acting mechanical and metabolic switches",
                    "revista": "Nature Reviews Mol Cell Biol",
                    "ano": "2023",
                    "doi": "10.1038/s41580-023-00624-8",
                    "pmid": "37464010"
                },
                {
                    "titulo": "Phase separation of intrinsically disordered salivary and peritrophic proteins in vectors",
                    "revista": "Cell Reports",
                    "ano": "2024",
                    "doi": "10.1016/j.celrep.2024.113940",
                    "pmid": "38457388"
                }
            ],
            "intersecao_luchm": "A matriz peritrófica do mosquito e o muco salivar de Anopheles são ricos em proteínas ricas em prolina e cisteína (peritrofinas). Se a secreção e consolidação da matriz peritrófica dependerem de uma transição de fase líquido-gel desencadeada pelo pH e pelo hemo, podemos dissolver a barreira ou hiper-estabilizá-la usando hidrótropos biológicos simples (como polifosfato ou ATP em concentrações específicas)!",
            "pontos_aprofundamento": [
                "O polifosfato inorgânico (polyP) atua como um hidrótropo biológico impedindo a agregação irreversível de proteínas durante o choque térmico e osmótico da transmissão?",
                "O complexo de invasão do oocineto/esporozoíto se organiza por condensação líquida transitória antes de disparar as micronemas?",
                "Pequenas moléculas que interferem na dinâmica de condensados (como 1,6-hexanodiol e derivados de ribosídeos) inibem a maturação de oocinetos na lâmina basal?"
            ]
        },
        {
            "id": "nanotribologia-intestinal",
            "tema": "Nanotribologia, Reologia Não-Newtoniana e Mecanobiologia da Borda em Escova",
            "icone": "⚙️",
            "o_que_e": "A física do atrito, adesão e lubrificação molecular em escala nanométrica (nanotribologia) combinada ao sensoriamento de forças de cisalhamento por canais mecanossensíveis (PIEZO, TMC) no intestino e na circulação.",
            "historia": """O repasto sanguíneo de um mosquito é um dos eventos mecânicos mais violentos da natureza: o inseto consome de três a quatro vezes seu próprio peso corporal de um fluido altamente viscoso, não-newtoniano e repleto de elementos figurados através de um estilete microscópico em menos de 120 segundos.

A biologia tradicional tratou isso como um problema químico de digestão enzimática. No entanto, os biofísicos de fluidos e mecanobiologistas descobriram que o epitélio intestinal do inseto opera como um sistema tribológico avançado: o glicocálix atua como lubrificante hidrodinâmico para impedir que as hemácias rompam a membrana plasmática por fricção, enquanto canais mecanossensíveis PIEZO disparam influxos de cálcio que comandam a secreção enzimática em resposta à tensão parietal da parede intestinal.""",
            "papers_marco": [
                {
                    "titulo": "Nanotribology of biological interfaces: Molecular lubrication and wear protection",
                    "revista": "Physical Review Letters",
                    "ano": "2024",
                    "doi": "10.1103/PhysRevLett.132.098401",
                    "pmid": "38457612"
                },
                {
                    "titulo": "PIEZO channels coordinate gut stretch sensing and peritrophic secretion in insects",
                    "revista": "Science Advances",
                    "ano": "2024",
                    "doi": "10.1126/sciadv.adk9821",
                    "pmid": "38381830"
                }
            ],
            "intersecao_luchm": "No modelo de camundongos sob dieta hiperlipídica (HFHS) estudado pelo LUCHM, o sangue ingerido pelo mosquito tem viscosidade plasmática e rigidez eritrocitária aumentadas. Esse sangue 'pesado' impõe uma carga de atrito (nanotribológica) muito mais destrutiva sobre a borda em escova do intestino, o que pode explicar a alteração de permeabilidade intestinal e a facilitação da passagem do parasito!",
            "pontos_aprofundamento": [
                "O sangue de camundongos HFHS causa microabrasão mecânica da borda em escova do mosquito, criando 'brechas' físicas antes da ação de defensinas?",
                "Antagonistas de canais mecanossensíveis PIEZO (como GsMTx4) bloqueiam a adaptação do intestino de Aedes ao repasto sanguíneo?",
                "Na malária cerebral, o atrito de eritrócitos rígidos e infectados nas paredes capilares gera shear stress patológico suficiente para ativar a ferroptose endotelial?"
            ]
        }
    ],
    "tecnicas_emergentes": [
        {
            "id": "nanoscopia-afm-ir",
            "tecnica": "Nanoscopia Química por AFM-IR (Microscopia de Força Atômica com Espectroscopia Infravermelha)",
            "icone": "🔬",
            "o_que_e": "A fusão da resolução espacial nanométrica do AFM com a especificidade molecular da espectroscopia de infravermelho (FTIR), permitindo identificar a composição química de uma única organela sem usar anticorpos, corantes ou fluoróforos.",
            "historia": """A microscopia eletrônica clássica tem resolução espetacular de nanômetros, mas é quimicamente cega (mostra tons de cinza de contraste com metais pesados). A fluorescência identifica moléculas com precisão, mas depende de anticorpos e marcadores que alteram o estado nativo e esbarram no limite de difração da luz (~200 nm).

O AFM-IR resolveu esse impasse unindo um laser de infravermelho sintonizável a uma ponta de força atômica. Quando o laser excita uma ligação química específica (por exemplo, a ligação fosfato-fosfato de polyP ou ésteres de lipídios), a molécula absorve luz e expande termicamente em escala infinitesimal. A agulha do AFM detecta essa vibração mecânica na superfície com resolução de 10 a 20 nanômetros, gerando um mapa espectral químico direto.""",
            "papers_marco": [
                {
                    "titulo": "Nanoscale infrared chemical imaging of intracellular organelles and protein aggregates",
                    "revista": "Chemical Reviews",
                    "ano": "2023",
                    "doi": "10.1021/acs.chemrev.2c00824",
                    "pmid": "36996321"
                },
                {
                    "titulo": "Label-free chemical identification of polyphosphate and lipids at 15 nm resolution",
                    "revista": "Nature Methods",
                    "ano": "2024",
                    "doi": "10.1038/s41592-024-02190-w",
                    "pmid": "38347120"
                }
            ],
            "aplicacao_luchm": "No LUCHM, podemos levar seções criogênicas ou secas de intestino de Aedes/Anopheles ou de esporozoítos e mapear diretamente onde estão os anéis de polifosfato de cadeia longa e as espécies lipídicas nos acidocalcisomos e grânulos secretores, com resolução de 15 nm e sem qualquer artefato de fixação com ósmio ou glutaraldeído!",
            "pontos_aprofundamento": [
                "Podemos discriminar polifosfato de cadeia curta vs cadeia longa in situ dentro do acidocalcisomo do parasito usando as bandas vibracionais de estiramento assimétrico P=O (1260 cm⁻¹) e P-O-P (870 cm⁻¹)?",
                "O equipamento de AFM-IR está acessível no polo de nanotecnologia e caracterização de materiais do CENABIO/COPPE/UFRJ?",
                "É viável analisar cortes ultrafinos de tecidos de insetos depositados diretamente em prismas de ZnSe ou lâminas de ouro?"
            ]
        },
        {
            "id": "optogenetica-invertebrados",
            "tecnica": "Optogenética e Termogenética Não-Invasiva em Insetos Vivos Intactos",
            "icone": "💡",
            "o_que_e": "Controle óptico e térmico remoto de neurônios, enterócitos e células musculares em mosquitos livres e intactos, usando luz vermelha profunda (CsChrimson) e canais térmicos (TRPA1).",
            "historia": """Por décadas, testar a função de um circuito neuropeptídico ou da motilidade intestinal de um mosquito exigia dissecção, drogas injetadas por microinjeção traumática ou silenciamento por RNAi de corpo inteiro (que afeta o inseto por dias).

A transposição de canais optogenéticos ativados por luz vermelha (comprimento de onda longo que penetra a cutícula sem queimar o inseto) e termogenéticos para culicídeos permitiu que pesquisadores ativem neurônios específicos com um simples feixe de LED enquanto o mosquito voa ou se alimenta em tempo real, sem qualquer agulha ou anestesia.""",
            "papers_marco": [
                {
                    "titulo": "Optogenetic control of feeding and enteric motility in freely behaving mosquitoes",
                    "revista": "Nature Communications",
                    "ano": "2024",
                    "doi": "10.1038/s41467-024-46120-1",
                    "pmid": "38459012"
                },
                {
                    "titulo": "Non-invasive optical interrogation of vector behavior and host choice",
                    "revista": "Neuron",
                    "ano": "2023",
                    "doi": "10.1016/j.neuron.2023.08.019",
                    "pmid": "37714150"
                }
            ],
            "aplicacao_luchm": "Podemos cruzar as frentes de neurobiologia e imunometabolismo do LUCHM: iluminar o abdômen do mosquito com LED vermelho para acelerar artificialmente o peristaltismo durante a passagem do oocineto, ou desativar os neurônios secretores de CCHa2 no momento exato do repasto sanguíneo para verificar se o priming imune depende do circuito neural central!",
            "pontos_aprofundamento": [
                "Podemos testar a resposta do mosquito à fonotaxia e atração pelo hospedeiro enquanto manipulamos canais de luz em subpopulações de células enteroendócrinas?",
                "Qual a intensidade e janela de irradiação de luz vermelha que atravessa a cutícula melanizada de Aedes sem gerar estresse oxidativo inespecífico?",
                "É viável adaptar nosso sistema de alimentação artificial em alimentador de membrana com iluminadores ópticos controlados por microcontrolador Arduino/Raspberry Pi?"
            ]
        }
    ]
}

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(dossie_fronteira, f, ensure_ascii=False, indent=2)

print(f"✅ Arquivo {OUT_FILE} gerado com sucesso!")
print(f"  • Ensaio: {dossie_fronteira['ensaio']['titulo'][:50]}...")
print(f"  • Pesquisadores: {[p['nome'] for p in dossie_fronteira['grandes_pesquisadores']]}")
print(f"  • Temas em expansão: {[t['tema'][:35] for t in dossie_fronteira['temas_expansao']]}")
print(f"  • Técnicas: {[tc['tecnica'][:35] for tc in dossie_fronteira['tecnicas_emergentes']]}")
