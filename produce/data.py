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
        slug="sweet-potato", name="Sweet Potato", latin="Ipomoea batatas",
        crate="crate-sweetpotato-cut", tag="Vegetable",
        blurb="Cured and export-packed, with a long window and good transit tolerance.",
        varieties=["Beauregard", "Brazlândia Roxa", "Uruguaiana"],
        states=["Rio Grande do Sul", "São Paulo", "Minas Gerais", "Paraná"],
        peak=list(range(1, 13)), available=list(range(1, 13)),
        organic="TBC",
        notes=("Curing is the whole game: properly cured roots heal wounds, hold sugar and travel "
               "well. Beauregard is the orange-fleshed variety most European and North American "
               "retail expects."),
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

# The three grape colours share a page but are sold as separate lines.
GRAPE_COLOURS = [
    ("Green", "crate-grapegreen-cut", "Sugraone · Thompson Seedless"),
    ("Red", "crate-grapered-cut", "Crimson · Flame Seedless"),
    ("Black", "crate-grapeblack-cut", "Midnight Beauty · Autumn Royal"),
]

MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]
