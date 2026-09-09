"""Product data for the produce portal.

Two kinds of field live here and they must not be confused:

  * AGRONOMY — varieties, growing states, harvest windows. These are public,
    well-established facts about Brazilian production and are safe to publish.
  * COMPANY   — organic status per line and packing formats. These are facts
    about Terra Fresca that only Daniel can supply. Anything still reading "TBC"
    is rendered on the page as "on request" rather than being guessed at.

Deliberately absent: annual tonnage. Terra Fresca represents farms rather than
owning production, so a company production figure would be meaningless, and a
national one quoted as if it were ours would be worse. Volume is presented as a
programme question, which is both honest and the right commercial answer.

Harvest months are 1-12. `peak` is the export window; `available` is when fruit
can be had at all, which is usually wider.
"""

REACH_NOTE = (
    "Terra Fresca is not tied to a fixed grower list. We represent farms across "
    "Brazil and build the supply base around the programme — which means volume, "
    "variety and window are negotiated against what the country can actually "
    "deliver in a given season, not against one estate's capacity."
)

ORGANIC_NOTE = (
    "Brazilian organic production is certified under the national SisOrg system "
    "administered by MAPA, and exporters generally hold additional certification "
    "recognised by the destination — EU organic for Europe, USDA NOP for the "
    "United States. Organic lines run at lower volume, need to be booked further "
    "ahead, and carry a premium over conventional."
)

PRODUCTS = [
    dict(
        slug="mango", name="Mango", latin="Mangifera indica", crate="crate-mango-cut",
        tag="Fruit", blurb="Brazil's flagship fresh fruit export, and the line most buyers start with.",
        varieties=["Tommy Atkins", "Palmer", "Keitt", "Kent"],
        states=["Bahia (São Francisco Valley)", "Pernambuco", "Ceará", "Rio Grande do Norte"],
        peak=[9, 10, 11, 12], available=[3, 4, 5, 9, 10, 11, 12],
        second_window="A secondary window runs roughly March to May.",
        organic="TBC",
        notes=("Tommy Atkins ships best and sells on appearance; Palmer eats better and is less "
               "forgiving of a broken cold chain; Keitt harvests later and extends the programme. "
               "Mango is chilling-sensitive — carried too cold it pits and develops off flavours."),
        link="/blog/brazilian-mango-varieties/",
    ),
    dict(
        slug="seedless-grape", name="Seedless Grape", latin="Vitis vinifera",
        crate="crate-grapegreen-cut", tag="Grape",
        blurb="Green, red and black seedless from an irrigated valley that can harvest twice a year.",
        varieties=["Sugraone", "Thompson Seedless", "Crimson Seedless", "Flame Seedless",
                   "Midnight Beauty", "Autumn Royal"],
        states=["Pernambuco (São Francisco Valley)", "Bahia"],
        peak=[10, 11, 12], available=[4, 5, 6, 10, 11, 12],
        second_window="A second, smaller harvest runs in autumn.",
        organic="TBC",
        variants=[
            dict(slug="green", name="Green Seedless Grape", crate="crate-grapegreen-cut",
                 varieties=["Sugraone", "Thompson Seedless", "Arra 15"],
                 blurb="Pale translucent green with a soft natural bloom — the volume colour.",
                 notes="The largest of the three colours by volume and the most widely listed."),
            dict(slug="red", name="Red Seedless Grape", crate="crate-grapered-cut",
                 varieties=["Crimson Seedless", "Flame Seedless", "Sweet Celebration"],
                 blurb="Deep crimson and translucent, firm berry, strong shelf presence.",
                 notes="Crimson holds condition well and is the workhorse of the red programmes."),
            dict(slug="black", name="Black Seedless Grape", crate="crate-grapeblack-cut",
                 varieties=["Midnight Beauty", "Autumn Royal", "Sable"],
                 blurb="Glossy purple-black with a dusty bloom and a large berry.",
                 notes="The premium colour in most markets, and the one most sensitive to rachis condition."),
        ],
        notes=("The valley's advantage is timing: it fills the gap between the end of "
               "northern-hemisphere supply and full southern-hemisphere volume. Allocation for the "
               "October window closes well before harvest. Ask about SO2 regime and rachis "
               "condition, not only brix and calibre."),
        link="/blog/sao-francisco-valley-seedless-grapes/",
    ),
    dict(
        slug="yellow-melon", name="Yellow Melon", latin="Cucumis melo",
        crate="crate-melon-cut", tag="Melon",
        blurb="Irrigated northeastern production with a long window and short transit to Europe.",
        varieties=["Amarelo", "Galia", "Cantaloupe", "Pele de Sapo"],
        states=["Rio Grande do Norte", "Ceará", "Bahia"],
        peak=[8, 9, 10, 11, 12, 1, 2, 3], available=[7, 8, 9, 10, 11, 12, 1, 2, 3],
        organic="TBC",
        notes=("Grown close to Pecém and Natal, which shortens both the inland leg and the ocean "
               "transit to Europe. Brix at harvest sets the ceiling on eating quality; nothing "
               "downstream raises it."),
    ),
    dict(
        slug="papaya", name="Papaya", latin="Carica papaya",
        crate="crate-papaya-cut", tag="Fruit",
        blurb="One of the genuinely year-round lines, and a good shelf-position anchor.",
        varieties=["Formosa", "Golden", "Sunrise Solo"],
        states=["Espírito Santo", "Bahia", "Ceará", "Rio Grande do Norte"],
        peak=list(range(1, 13)), available=list(range(1, 13)),
        organic="TBC",
        notes=("Available all year, though volume and price move with the wet season. Chilling-"
               "sensitive and easily bruised, so handling discipline at the packhouse matters more "
               "than for most lines."),
    ),
    dict(
        slug="tahiti-lime", name="Tahiti Lime", latin="Citrus latifolia",
        crate="crate-lime-cut", tag="Citrus",
        blurb="Seedless Persian lime, shipped year-round, with a price that moves with the rains.",
        varieties=["Tahiti (Persian) lime"],
        states=["São Paulo", "Minas Gerais", "Bahia"],
        peak=list(range(1, 13)), available=list(range(1, 13)),
        organic="TBC",
        notes=("Genuinely year-round, but volume tightens in the Brazilian wet season and price "
               "follows. Buyers who fix a flat twelve-month price without a review clause tend to "
               "discover this in February. Carried too cold, limes pit and the rind breaks down."),
    ),
    dict(
        slug="banana", name="Banana", latin="Musa spp.",
        crate="crate-banana-cut", tag="Fruit",
        blurb="Year-round, with strong domestic demand competing for the same volume.",
        varieties=["Prata", "Nanica (Cavendish)", "Maçã"],
        states=["São Paulo", "Minas Gerais", "Bahia", "Santa Catarina"],
        peak=list(range(1, 13)), available=list(range(1, 13)),
        organic="TBC",
        notes=("The classic chilling-sensitive product, carried notably warmer than most produce. "
               "Brazil's domestic market absorbs the large majority of national production, so "
               "export allocation needs to be agreed rather than assumed."),
    ),
    dict(
        slug="pineapple", name="Pineapple", latin="Ananas comosus",
        crate="crate-pineapple-cut", tag="Fruit",
        blurb="Available across the year from staggered plantings in several states.",
        varieties=["Pérola", "Smooth Cayenne"],
        states=["Pará", "Paraíba", "Minas Gerais", "Bahia"],
        peak=list(range(1, 13)), available=list(range(1, 13)),
        organic="TBC",
        notes=("Pérola is the dominant Brazilian variety and eats sweeter than Smooth Cayenne, "
               "which travels better. Chilling-sensitive; too cold produces internal browning."),
    ),
    dict(
        slug="watermelon", name="Watermelon", latin="Citrullus lanatus",
        crate="crate-watermelon-cut", tag="Melon",
        blurb="High-volume line from the northeast and centre-west with a long southern-summer window.",
        varieties=["Crimson Sweet", "Manchester", "Mini seedless"],
        states=["Rio Grande do Norte", "Bahia", "Goiás", "São Paulo"],
        peak=[9, 10, 11, 12, 1, 2, 3], available=[8, 9, 10, 11, 12, 1, 2, 3, 4],
        organic="TBC",
        notes=("Heavy and low value per kilo, so freight efficiency dominates the economics and the "
               "load port choice matters more than usual. Mini seedless formats carry better margin "
               "for retail."),
    ),
    dict(
        slug="avocado", name="Avocado", latin="Persea americana",
        crate="crate-avocado-cut", tag="Fruit",
        blurb="Hass and Breda through the southern-hemisphere autumn and winter.",
        varieties=["Hass", "Breda", "Margarida", "Fortuna"],
        states=["São Paulo", "Minas Gerais", "Paraná"],
        peak=[3, 4, 5, 6, 7, 8, 9], available=[2, 3, 4, 5, 6, 7, 8, 9, 10],
        organic="TBC",
        notes=("Hass is what most export programmes want; Breda is larger and serves different "
               "markets. Dry matter at harvest is the specification that predicts eating quality — "
               "ask for it, not just calibre."),
    ),
    dict(
        slug="ginger", name="Ginger", latin="Zingiber officinale",
        crate="crate-ginger-cut", tag="Root",
        blurb="Export-grade fresh root, mainly from the Atlantic forest belt in the south-east.",
        varieties=["Fresh root, export grade"],
        states=["Espírito Santo", "Santa Catarina", "Paraná", "São Paulo"],
        peak=[5, 6, 7, 8, 9, 10, 11], available=[4, 5, 6, 7, 8, 9, 10, 11, 12],
        organic="TBC",
        notes=("Curing after harvest determines shelf life more than anything in transit. Rhizome "
               "size and freedom from sprouting are the grading criteria buyers argue about."),
    ),
    dict(
        slug="potato", name="Potato & Roots", latin="Solanum · Ipomoea · Arracacia",
        crate="crate-sweetpotato-cut", tag="Vegetable",
        blurb="Sweet potato, table potato and mandioquinha — three different crops that buyers usually source together.",
        varieties=["Beauregard", "Asterix", "Ágata", "Mandioquinha"],
        states=["Rio Grande do Sul", "Minas Gerais", "São Paulo", "Paraná", "Espírito Santo"],
        peak=list(range(1, 13)), available=list(range(1, 13)),
        organic="TBC",
        variants=[
            dict(slug="sweet-potato", name="Sweet Potato", crate="crate-sweetpotato-cut",
                 varieties=["Beauregard", "Brazlândia Roxa", "Uruguaiana"],
                 blurb="Orange and purple-skinned batata doce, cured and export packed.",
                 notes=("Curing is the whole game: properly cured roots heal wounds, hold sugar and "
                        "travel well. Beauregard is the orange-fleshed variety most European and "
                        "North American retail expects.")),
            dict(slug="table-potato", name="Table Potato", crate="crate-potato-cut",
                 varieties=["Asterix", "Ágata", "Markies", "Cupido"],
                 blurb="Batata inglesa from the southern and south-eastern highlands.",
                 notes=("Ágata is the pale-skinned washing potato that dominates Brazilian retail; "
                        "Asterix is red-skinned and holds up better to processing and transport. "
                        "Dry matter drives cooking behaviour and should be specified.")),
            dict(slug="mandioquinha", name="Mandioquinha", crate="crate-baroa-cut",
                 varieties=["Amarela de Senador Amaral", "Branca"],
                 blurb="Arracacha, also called batata baroa or Peruvian carrot — a Brazilian staple.",
                 notes=("Distinctive deep-yellow flesh and a short shelf life, which makes cold "
                        "chain discipline decisive. A specialist line rather than a volume one, "
                        "and strong in Brazilian diaspora retail.")),
        ],
        notes=("Three botanically unrelated crops that share a shelf and a buyer. Sweet potato "
               "travels best of the three; mandioquinha is the most perishable and the most "
               "specialised. All are cured or conditioned after harvest, and how well that was done "
               "predicts arrival condition better than anything that happens in transit."),
    ),
    dict(
        slug="passion-fruit", name="Passion Fruit", latin="Passiflora edulis",
        crate="crate-passion-cut", tag="Fruit",
        blurb="Maracujá azedo — the yellow sour passion fruit, available most of the year.",
        varieties=["Maracujá azedo (yellow)", "Maracujá doce (sweet)"],
        states=["Bahia", "Ceará", "Espírito Santo", "Minas Gerais"],
        peak=[1, 2, 3, 4, 5, 11, 12], available=list(range(1, 13)),
        organic="TBC",
        notes=("Skin wrinkling is normal as the fruit loses water and is not a defect, but it is "
               "the thing retail rejects on, so transit humidity and timing matter. Air freight "
               "suits the premium end of this line."),
    ),
]

# Researched vegetable additions. Calendar promises are confirmed per programme.
PRODUCTS.extend([
    dict(
        slug="onion", name="Onion", latin="Allium cepa", crate="crate-onion-cut", tag="Vegetable",
        blurb="Yellow and red onions from Brazil, selected for firm bulbs, dry skins and the buyer's size specification.",
        varieties=["Yellow onions", "Red onions", "BRS Alfa São Francisco"],
        states=["Santa Catarina", "Minas Gerais", "Goiás", "Bahia", "Pernambuco", "São Paulo"],
        peak=[], available=[], organic="TBC",
        availability_note="Brazilian production spans several regions with different growing calendars. Confirm the current origin, colour, cultivar and delivery window for each order; a national growing pattern is not a promise of export stock.",
        notes="Specify skin colour, bulb diameter and intended use before choosing the cultivar. BRS Alfa São Francisco is a Brazilian cultivar reference for warmer growing regions; the cultivar supplied is confirmed per order. Look for firm bulbs with dry outer skins and well-dried necks. Careful curing, protection from bruising and dry, ventilated handling matter for arrival quality.",
        sources=[
            ("Embrapa — Cultivo da cebola no Nordeste (2025)", "https://www.infoteca.cnptia.embrapa.br/infoteca/handle/doc/1178254?locale=en"),
            ("Embrapa — BRS Alfa São Francisco", "https://www.embrapa.br/en/web/hortalicas/busca-de-solucoes-tecnologicas/-/produto-servico/10397/cebola-brs-alfa-sao-francisco"),
            ("Embrapa — Post-harvest handling of vegetables", "https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/921546/1/500perguntasposcolheitahortalicas.pdf"),
        ],
    ),
    dict(
        slug="yuca", name="Yuca (Cassava)", latin="Manihot esculenta", crate="crate-yuca-cut", tag="Root",
        blurb="Brazilian table yuca, also called mandioca, aipim or macaxeira, with brown skin and white or yellow flesh.",
        varieties=["White-fleshed table yuca — cultivar on request", "IAC 576-70 (yellow flesh)", "BRS 399 (yellow flesh)"],
        states=["São Paulo", "Paraná", "Mato Grosso do Sul", "Goiás", "Distrito Federal"],
        peak=[], available=[], organic="TBC",
        availability_note="The harvest window depends on planting date and cultivar. IAC 576-70 is commonly harvested 9–14 months after planting, while Embrapa recommends 8–12 months for BRS 399. Delivery dates and product format are confirmed against a harvesting and handling plan.",
        notes="This line is table cassava, distinct from varieties selected for industrial starch. Specify flesh colour, root size and fresh or processed format when requesting a quote. Fresh roots deteriorate quickly after harvest, so avoid broken roots and unnecessary handling delays. Packing, preservation method and transit time must be agreed together; any peeled or frozen format is confirmed on request.",
        sources=[
            ("IAC — Table cassava cultivar IAC 576-70", "https://www.iac.sp.gov.br/cultivares/inicio/Folders/Mandioca/IAC576-70.htm"),
            ("IAC — Table cassava growing regions and cultivars", "https://oagronomico.iac.sp.gov.br/?p=893"),
            ("Embrapa — Table cassava BRS 399", "https://www.embrapa.br/en/busca-de-solucoes-tecnologicas/-/produto-servico/6126/mandioca-de-mesa-brs-399"),
            ("Embrapa — Post-harvest deterioration of cassava", "https://www.embrapa.br/en/busca-de-publicacoes/-/publicacao/914714/deterioracao-fisiologica-pos-colheita-em-germoplasma-de-mandioca"),
        ],
    ),
])
_table_potato = next(v for p in PRODUCTS if p["slug"] == "potato" for v in p["variants"] if v["slug"] == "table-potato")
_table_potato.update(
    notes="Choose the potato for its intended cooking use as well as its skin colour and size. Embrapa sensory work found Ágata well suited to boiling and Asterix moderately suited to several preparations. Markies is also used for processing. Confirm dry matter, calibre and the supplied cultivar with each programme; avoid treating all table potatoes as interchangeable.",
    availability_note="Brazilian production uses different regional planting and harvest windows. Confirm the origin, cultivar and dispatch date for your programme rather than assuming the same lot is available throughout the year.",
    sources=[
        ("Embrapa — Culinary suitability of potato cultivars", "https://www.alice.cnptia.embrapa.br/alice/handle/doc/779525"),
        ("Embrapa — Main potato cultivars grown in Brazil", "https://www.alice.cnptia.embrapa.br/alice/bitstream/doc/1106943/1/ArionePereiraSeedNews.pdf"),
    ],
)

# The three grape colours share a page but are sold as separate lines.
GRAPE_COLOURS = [
    ("Green", "crate-grapegreen-cut", "Sugraone · Thompson Seedless"),
    ("Red", "crate-grapered-cut", "Crimson · Flame Seedless"),
    ("Black", "crate-grapeblack-cut", "Midnight Beauty · Autumn Royal"),
]

MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
