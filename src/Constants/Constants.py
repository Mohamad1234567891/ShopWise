NOW, NEXT = 0, 1  # priorities: work for products already started goes before opening new product pages

STORES_BY_REGION = {
    # North America
    "US": [
        "walmart.com", "amazon.com", "target.com", "bestbuy.com", "costco.com",
        "homedepot.com", "macys.com", "nordstrom.com", "etsy.com", "ebay.com",
        "kohls.com", "chewy.com", "crutchfield.com", "bhphotovideo.com"
    ],
    "CA": [
        "amazon.ca", "walmart.ca", "costco.ca", "canadiantire.ca", "bestbuy.ca",
        "homedepot.ca", "indigo.ca", "well.ca", "simons.ca", "ikea.com/ca",
        "etsy.com"
    ],
    "MX": [
        "amazon.com.mx", "mercadolibre.com.mx", "walmart.com.mx", "liverpool.com.mx",
        "coppel.com", "elektra.com.mx", "cyberpuerta.mx", "lg.com/mx",
        "homedepot.com.mx", "chedraui.com.mx"
    ],

    # South America
    "BR": [
        "mercadolivre.com.br", "amazon.com.br", "magazineluiza.com.br", "shopee.com.br",
        "netshoes.com.br", "shein.com", "americanas.com.br", "submarino.com.br"
    ],
    "AR": [
        "mercadolibre.com.ar", "fravega.com", "garbarino.com", "musimundo.com",
        "carrefour.com.ar", "easy.com.ar", "falabella.com.ar", "adidas.com.ar"
    ],
    "CO": [
        "mercadolibre.com.co", "amazon.com", "falabella.com.co", "exito.com",
        "alkosto.com", "homecenter.com.co", "olimpica.com", "yaxa.com"
    ],
    "CL": [
        "mercadolibre.cl", "falabella.com", "paris.cl", "ripley.cl", "easy.cl",
        "lider.cl", "santaisabel.cl", "pcfactory.cl"
    ],
    "PE": [
        "mercadolibre.com.pe", "falabella.com.pe", "ripley.com.pe", "oechsle.pe",
        "plazavea.com.pe", "tottus.com.pe", "linio.com.pe", "juntoz.com"
    ],

    # Europe
    "GB": [
        "amazon.co.uk", "ebay.co.uk", "argos.co.uk", "johnlewis.com", "asos.com",
        "next.co.uk", "marksandspencer.com", "currys.co.uk", "boots.com",
        "tesco.com", "asda.com", "thebookshop.org", "waterstones.com", "zalando.co.uk"
    ],
    "DE": [
        "amazon.de", "otto.de", "zalando.de", "mediamarkt.de", "saturn.de",
        "lidl.de", "tchibo.de", "ikea.com/de", "decathlon.de", "aboutyou.de",
        "coolblue.de", "rewe.de", "knuspr.de"
    ],
    "FR": [
        "amazon.fr", "fnac.com", "cdiscount.com", "leroymerlin.fr", "darty.com",
        "boulanger.com", "zalando.fr", "vinted.fr", "laredoute.fr", "vertbaudet.fr",
        "decathlon.fr", "yves-rocher.fr", "ikea.com/fr"
    ],
    "IT": [
        "amazon.it", "zalando.it", "unieuro.it", "decathlon.it", "sephora.it",
        "leroymerlin.it", "refurbed.it", "lancome.it", "lovable.it", "napapijri.com"
    ],
    "ES": [
        "amazon.es", "elcorteingles.es", "pccomponentes.com", "mango.com", "zara.com",
        "carrefour.es", "mediamarkt.es", "decathlon.es", "wallapop.com",
        "laredoute.es", "nespresso.com"
    ],
    "NL": [
        "bol.com", "coolblue.nl", "wehkamp.nl", "marktplaats.nl", "amazon.nl",
        "zalando.nl", "hema.nl", "ah.nl", "thuiswinkel.org"
    ],
    "BE": [
        "bol.com", "coolblue.be", "amazon.com.be", "zalando.be", "newpharma.be",
        "decathlon.be", "ikea.com/be", "mediamarkt.be", "baunat.com", "torfs.be"
    ],
    "CH": [
        "digitec.ch", "galaxus.ch", "ricardo.ch", "brack.ch", "manor.ch",
        "interdiscount.ch", "coop.ch", "migros.ch", "zalando.ch", "amazon.de"
    ],
    "AT": [
        "amazon.de", "zalando.at", "shop-apotheke.at", "bestsecret.at", "ottoversand.at",
        "hornbach.at", "kastner-oehler.at", "decathlon.at", "morawa.at", "gans.at"
    ],
    "SE": [
        "apotea.se", "amazon.se", "zalando.se", "adlibris.se", "hm.com", "inet.se",
        "ikea.com/se", "elgiganten.se", "webhallen.com", "boozt.com", "sellpy.com"
    ],
    "NO": [
        "komplett.no", "finn.no", "zalando.no", "elkjop.no", "ikea.com/no",
        "netonnet.no", "biltema.no", "clasohlson.com", "dressmann.com"
    ],
    "DK": [
        "nemlig.com", "zalando.dk", "boozt.com", "elgiganten.dk", "power.dk",
        "ikea.com/dk", "dba.dk", "gucca.dk", "thansen.dk", "silvan.dk"
    ],
    "PL": [
        "allegro.pl", "empik.com", "mediaexpert.pl", "amazon.pl", "oponeo.pl",
        "ceneo.pl", "sfd.pl", "mi-store.pl", "czytam.pl", "dobraksiazka.pl"
    ],
    "IE": [
        "amazon.co.uk", "elara.ie", "mcsport.ie", "lenehans.ie", "agridirect.ie",
        "petmania.ie", "aosom.ie", "allirelandfoods.ie", "rackzone.ie"
    ],
    "RU": [
        "wildberries.ru", "ozon.ru", "market.yandex.ru", "vkusvill.ru", "lamoda.ru",
        "sportmaster.ru", "dns-shop.ru", "magnit.ru", "metro-cc.ru", "letu.ru"
    ],

    # Asia
    "TR": [
        "trendyol.com", "hepsiburada.com", "n11.com",
        "gittigidiyor.com", "pttavm.com", "mediamarkt.com.tr",
        "pamuka.com.tr"
    ],
    "JP": [
        "rakuten.co.jp", "amazon.co.jp", "yodobashi.com", "yahoo.co.jp",
        "uniqlo.com/jp", "joshinweb.jp", "zozo.jp", "mercari.com"
    ],
    "CN": [
        "taobao.com", "tmall.com", "jd.com", "pinduoduo.com", "1688.com",
        "vip.com", "aliexpress.com", "shein.com", "dhgate.com"
    ],
    "KR": [
        "ssg.com", "smartstore.naver.com", "lotteon.com", "gmarket.co.kr",
        "auction.co.kr", "11st.co.kr", "coupang.com", "kakao.com"
    ],
    "IN": [
        "amazon.in", "flipkart.com", "myntra.com", "nykaa.com", "meesho.com",
        "jiomart.com", "snapdeal.com", "shopsy.in", "ajio.com", "tatacliq.com"
    ],
    "SG": [
        "shopee.sg", "lazada.sg", "amazon.sg", "zalora.sg", "robinsons.com.sg",
        "fairprice.com.sg", "ikea.com/sg", "carousell.sg", "redmart.com"
    ],
    "MY": [
        "shopee.com.my", "lazada.com.my", "lelong.com.my", "pgmall.my",
        "zalora.com.my", "qoo10.my", "harveynorman.com.my"
    ],
    "TH": [
        "shopee.co.th", "lazada.co.th", "sasom.co.th", "konvy.com", "grab.com",
        "line.me", "jib.co.th"
    ],
    "ID": [
        "shopee.co.id", "tokopedia.com", "bukalapak.com", "lazada.co.id", "blibli.com",
        "ruparupa.com", "sociolla.com", "orami.co.id", "datascripmall.id"
    ],
    "PH": [
        "shopee.ph", "lazada.com.ph", "shopsm.com", "watsons.com.ph", "lg.com/ph",
        "concepcion.com.ph", "pursemaison.com"
    ],
    "VN": [
        "shopee.vn", "lazada.vn", "thegioididong.com", "dienmayxanh.com", "tiki.vn",
        "meta.vn", "fado.vn", "aeoneshop.com"
    ],

    # Middle East & Africa
    "AE": [
        "amazon.ae", "noon.com", "namshi.com", "ounass.ae", "sharafdg.com",
        "6thstreet.com", "carrefouruae.com", "mumzworld.com"
    ],
    "SA": [
        "amazon.sa", "noon.com", "alassly.com", "theoutlet.sa", "eoutlet.sa",
        "jazp.com"
    ],
    "IL": [
        "ksp.co.il", "shufersal.co.il", "super-pharm.co.il", "worker.co.il",
        "israelcart.com", "silal.com"
    ],
    "EG": [
        "jumia.com.eg", "noon.com", "amazon.eg", "alymarket.com", "ubuy.com.eg"
    ],
    "ZA": [
        "takealot.com", "superbalist.com", "zando.co.za", "yuppiechef.com",
        "checkers.co.za", "woolworths.co.za", "clicks.co.za", "dis-chem.co.za",
        "makro.co.za", "bobshop.co.za"
    ],
    "NG": [
        "jumia.com.ng", "konga.com", "jiji.ng", "payporte.com", "slot.ng",
        "kara.com.ng", "ajebomarket.com", "supermart.ng"
    ],
    "KE": [
        "kilimall.co.ke", "jumia.co.ke", "njirobale.com", "masoko.com"
    ],

    # Oceania
    "AU": [
        "amazon.com.au", "ebay.com.au", "theiconic.com.au", "myer.com.au",
        "bunnings.com.au", "kmart.com.au", "woolworths.com.au", "chemistwarehouse.com.au",
        "officeworks.com.au", "adorebeauty.com.au", "countryroad.com.au"
    ],
    "NZ": [
        "trademe.co.nz", "thewarehouse.co.nz", "noelleeming.co.nz", "pbtech.co.nz",
        "tum.co.nz", "gearshop.co.nz", "buykiwidirect.co.nz", "mocka.co.nz",
        "youknow.co.nz"
    ],
}

# Known search-page templates for EVERY store in STORES_BY_REGION.
# {query} is replaced with the (URL-encoded) search query, so every regional
# store is resolved directly without any search engine.
# Note: formats of the big international stores are verified; the rarer ones
# use their best-known pattern and can be adjusted here in one line if needed.
SEARCH_URL_TEMPLATES = {
    # North America
    "walmart.com": "https://www.walmart.com/search?q={query}",
    "amazon.com": "https://www.amazon.com/s?k={query}",
    "target.com": "https://www.target.com/s?searchTerm={query}",
    "bestbuy.com": "https://www.bestbuy.com/site/searchpage.jsp?st={query}",
    "costco.com": "https://www.costco.com/CatalogSearch?keyword={query}",
    "homedepot.com": "https://www.homedepot.com/s/{query}",
    "macys.com": "https://www.macys.com/shop/search?keyword={query}",
    "nordstrom.com": "https://www.nordstrom.com/sr?keyword={query}",
    "etsy.com": "https://www.etsy.com/search?q={query}",
    "ebay.com": "https://www.ebay.com/sch/i.html?_nkw={query}",
    "kohls.com": "https://www.kohls.com/search.jsp?search={query}",
    "chewy.com": "https://www.chewy.com/search?query={query}",
    "crutchfield.com": "https://www.crutchfield.com/search?q={query}",
    "bhphotovideo.com": "https://www.bhphotovideo.com/c/search?q={query}",

    "amazon.ca": "https://www.amazon.ca/s?k={query}",
    "walmart.ca": "https://www.walmart.ca/search?q={query}",
    "costco.ca": "https://www.costco.ca/CatalogSearch?keyword={query}",
    "canadiantire.ca": "https://www.canadiantire.ca/en/search-results.html?q={query}",
    "bestbuy.ca": "https://www.bestbuy.ca/en-ca/search?search={query}",
    "homedepot.ca": "https://www.homedepot.ca/search?q={query}",
    "indigo.ca": "https://www.chapters.indigo.ca/en-ca/search/?keywords={query}",
    "well.ca": "https://well.ca/search?q={query}",
    "simons.ca": "https://www.simons.ca/en/search?q={query}",
    "ikea.com/ca": "https://www.ikea.com/ca/en/search/?q={query}",

    "amazon.com.mx": "https://www.amazon.com.mx/s?k={query}",
    "mercadolibre.com.mx": "https://www.mercadolibre.com.mx/jm/search?as_word={query}",
    "walmart.com.mx": "https://www.walmart.com.mx/buscar?q={query}",
    "liverpool.com.mx": "https://www.liverpool.com.mx/tienda?s={query}",
    "coppel.com": "https://www.coppel.com/buscar?text={query}",
    "elektra.com.mx": "https://www.elektra.com.mx/buscar?q={query}",
    "cyberpuerta.mx": "https://www.cyberpuerta.mx/index.php?cl=search&searchparam={query}",
    "lg.com/mx": "https://www.lg.com/mx/busqueda?q={query}",
    "homedepot.com.mx": "https://www.homedepot.com.mx/search?q={query}",
    "chedraui.com.mx": "https://www.chedraui.com.mx/search?q={query}",

    # South America
    "mercadolivre.com.br": "https://www.mercadolivre.com.br/jm/search?as_word={query}",
    "amazon.com.br": "https://www.amazon.com.br/s?k={query}",
    "magazineluiza.com.br": "https://www.magazineluiza.com.br/busca/{query}/",
    "shopee.com.br": "https://shopee.com.br/search?keyword={query}",
    "netshoes.com.br": "https://www.netshoes.com.br/busca?q={query}",
    "shein.com": "https://www.shein.com/pdsearch/{query}/",
    "americanas.com.br": "https://www.americanas.com.br/busca/{query}",
    "submarino.com.br": "https://www.submarino.com.br/busca/{query}",

    "mercadolibre.com.ar": "https://www.mercadolibre.com.ar/jm/search?as_word={query}",
    "fravega.com": "https://www.fravega.com/l/?keyword={query}",
    "garbarino.com": "https://www.garbarino.com/search?q={query}",
    "musimundo.com": "https://www.musimundo.com/search?text={query}",
    "carrefour.com.ar": "https://www.carrefour.com.ar/search?q={query}",
    "easy.com.ar": "https://www.easy.com.ar/search?q={query}",
    "falabella.com.ar": "https://www.falabella.com.ar/search?Ntt={query}",
    "adidas.com.ar": "https://www.adidas.com.ar/search?q={query}",

    "mercadolibre.com.co": "https://www.mercadolibre.com.co/jm/search?as_word={query}",
    "falabella.com.co": "https://www.falabella.com.co/search?Ntt={query}",
    "exito.com": "https://www.exito.com/s?query={query}",
    "alkosto.com": "https://www.alkosto.com/search?text={query}",
    "homecenter.com.co": "https://www.homecenter.com.co/homecenter-co/search/?Ntt={query}",
    "olimpica.com": "https://www.olimpica.com/search?q={query}",
    "yaxa.com": "https://www.yaxa.com/search?q={query}",

    "mercadolibre.cl": "https://www.mercadolibre.cl/jm/search?as_word={query}",
    "falabella.com": "https://www.falabella.com/falabella-cl/search?Ntt={query}",
    "paris.cl": "https://www.paris.cl/search?query={query}",
    "ripley.cl": "https://simple.ripley.cl/search/{query}",
    "easy.cl": "https://www.easy.cl/search?q={query}",
    "lider.cl": "https://www.lider.cl/supermercado/search?query={query}",
    "santaisabel.cl": "https://www.santaisabel.cl/search?q={query}",
    "pcfactory.cl": "https://www.pcfactory.cl/busqueda?categoria=0&texto={query}",

    "mercadolibre.com.pe": "https://www.mercadolibre.com.pe/jm/search?as_word={query}",
    "falabella.com.pe": "https://www.falabella.com.pe/search?Ntt={query}",
    "ripley.com.pe": "https://simple.ripley.com.pe/search/{query}",
    "oechsle.pe": "https://www.oechsle.pe/search?q={query}",
    "plazavea.com.pe": "https://www.plazavea.com.pe/search?q={query}",
    "tottus.com.pe": "https://www.tottus.com.pe/search?q={query}",
    "linio.com.pe": "https://www.linio.com.pe/search?q={query}",
    "juntoz.com": "https://www.juntoz.com/search?q={query}",

    # Europe
    "amazon.co.uk": "https://www.amazon.co.uk/s?k={query}",
    "ebay.co.uk": "https://www.ebay.co.uk/sch/i.html?_nkw={query}",
    "argos.co.uk": "https://www.argos.co.uk/search/{query}/",
    "johnlewis.com": "https://www.johnlewis.com/search?search-term={query}",
    "asos.com": "https://www.asos.com/search/?q={query}",
    "next.co.uk": "https://www.next.co.uk/search?w={query}",
    "marksandspencer.com": "https://www.marksandspencer.com/l/search?searchTerm={query}",
    "currys.co.uk": "https://www.currys.co.uk/search?q={query}",
    "boots.com": "https://www.boots.com/search?q={query}",
    "tesco.com": "https://www.tesco.com/groceries/en-GB/search?query={query}",
    "asda.com": "https://groceries.asda.com/search/{query}",
    "thebookshop.org": "https://uk.bookshop.org/search?keywords={query}",
    "waterstones.com": "https://www.waterstones.com/books/search/term/{query}",
    "zalando.co.uk": "https://www.zalando.co.uk/catalog/?q={query}",

    "amazon.de": "https://www.amazon.de/s?k={query}",
    "otto.de": "https://www.otto.de/suche/{query}/",
    "zalando.de": "https://www.zalando.de/catalog/?q={query}",
    "mediamarkt.de": "https://www.mediamarkt.de/de/search.html?query={query}",
    "saturn.de": "https://www.saturn.de/de/search.html?query={query}",
    "lidl.de": "https://www.lidl.de/q/search?q={query}",
    "tchibo.de": "https://www.tchibo.de/suche?q={query}",
    "ikea.com/de": "https://www.ikea.com/de/de/search/?q={query}",
    "decathlon.de": "https://www.decathlon.de/search?Ntt={query}",
    "aboutyou.de": "https://www.aboutyou.de/suche?term={query}",
    "coolblue.de": "https://www.coolblue.de/zoeken?query={query}",
    "rewe.de": "https://shop.rewe.de/search?search={query}",
    "knuspr.de": "https://www.knuspr.de/suche?q={query}",

    "amazon.fr": "https://www.amazon.fr/s?k={query}",
    "fnac.com": "https://www.fnac.com/SearchResult/ResultList.aspx?Search={query}",
    "cdiscount.com": "https://www.cdiscount.com/search/10/{query}.html",
    "leroymerlin.fr": "https://www.leroymerlin.fr/recherche?q={query}",
    "darty.com": "https://www.darty.com/nav/achat/recherche?text={query}",
    "boulanger.com": "https://www.boulanger.com/resultats?tr={query}",
    "zalando.fr": "https://www.zalando.fr/catalog/?q={query}",
    "vinted.fr": "https://www.vinted.fr/catalog?search_text={query}",
    "laredoute.fr": "https://www.laredoute.fr/psr.aspx?q={query}",
    "vertbaudet.fr": "https://www.vertbaudet.fr/recherche?q={query}",
    "decathlon.fr": "https://www.decathlon.fr/search?Ntt={query}",
    "yves-rocher.fr": "https://www.yves-rocher.fr/ctl/resultats?motcle={query}",
    "ikea.com/fr": "https://www.ikea.com/fr/fr/search/?q={query}",

    "amazon.it": "https://www.amazon.it/s?k={query}",
    "zalando.it": "https://www.zalando.it/catalog/?q={query}",
    "unieuro.it": "https://www.unieuro.it/online/ricerca?text={query}",
    "decathlon.it": "https://www.decathlon.it/search?Ntt={query}",
    "sephora.it": "https://www.sephora.it/search?q={query}",
    "leroymerlin.it": "https://www.leroymerlin.it/ricerca?q={query}",
    "refurbed.it": "https://www.refurbed.it/search?q={query}",
    "lancome.it": "https://www.lancome.it/search?q={query}",
    "lovable.it": "https://www.lovable.it/search?q={query}",
    "napapijri.com": "https://www.napapijri.com/search?q={query}",

    "amazon.es": "https://www.amazon.es/s?k={query}",
    "elcorteingles.es": "https://www.elcorteingles.es/s/?text={query}",
    "pccomponentes.com": "https://www.pccomponentes.com/buscar/?query={query}",
    "mango.com": "https://shop.mango.com/catalogsearch/result/?q={query}",
    "zara.com": "https://www.zara.com/tr/tr/search?searchTerm={query}",
    "carrefour.es": "https://www.carrefour.es/supermercado/?q={query}",
    "mediamarkt.es": "https://www.mediamarkt.es/es/search.html?query={query}",
    "decathlon.es": "https://www.decathlon.es/search?Ntt={query}",
    "wallapop.com": "https://es.wallapop.com/app/search?keywords={query}",
    "laredoute.es": "https://www.laredoute.es/psr.aspx?q={query}",
    "nespresso.com": "https://www.nespresso.com/search?q={query}",

    "bol.com": "https://www.bol.com/nl/nl/s/?searchtext={query}",
    "coolblue.nl": "https://www.coolblue.nl/zoeken?query={query}",
    "wehkamp.nl": "https://www.wehkamp.nl/zoeken/?q={query}",
    "marktplaats.nl": "https://www.marktplaats.nl/q/{query}/",
    "amazon.nl": "https://www.amazon.nl/s?k={query}",
    "zalando.nl": "https://www.zalando.nl/catalog/?q={query}",
    "hema.nl": "https://www.hema.nl/zoeken?q={query}",
    "ah.nl": "https://www.ah.nl/zoeken?query={query}",
    "thuiswinkel.org": "https://www.thuiswinkel.org/zoeken/?q={query}",

    "coolblue.be": "https://www.coolblue.be/zoeken?query={query}",
    "amazon.com.be": "https://www.amazon.com.be/s?k={query}",
    "zalando.be": "https://www.zalando.be/catalog/?q={query}",
    "newpharma.be": "https://www.newpharma.be/search/?query={query}",
    "decathlon.be": "https://www.decathlon.be/search?Ntt={query}",
    "ikea.com/be": "https://www.ikea.com/be/fr/search/?q={query}",
    "mediamarkt.be": "https://www.mediamarkt.be/nl/search.html?query={query}",
    "baunat.com": "https://www.baunat.com/search?q={query}",
    "torfs.be": "https://www.torfs.be/nl/search/?text={query}",

    "digitec.ch": "https://www.digitec.ch/de/search?q={query}",
    "galaxus.ch": "https://www.galaxus.ch/de/search?q={query}",
    "ricardo.ch": "https://www.ricardo.ch/de/search?query={query}",
    "brack.ch": "https://www.brack.ch/de/search?query={query}",
    "manor.ch": "https://www.manor.ch/de/search?text={query}",
    "interdiscount.ch": "https://www.interdiscount.ch/de/search?q={query}",
    "coop.ch": "https://www.coop.ch/de/search/?text={query}",
    "migros.ch": "https://www.migros.ch/de/product/search?text={query}",
    "zalando.ch": "https://www.zalando.ch/catalog/?q={query}",

    "zalando.at": "https://www.zalando.at/catalog/?q={query}",
    "shop-apotheke.at": "https://www.shop-apotheke.at/search.htm?searchtext={query}",
    "bestsecret.at": "https://www.bestsecret.at/search.htm?searchtext={query}",
    "ottoversand.at": "https://www.ottoversand.at/suche/{query}/",
    "hornbach.at": "https://www.hornbach.at/de/suche/{query}/",
    "kastner-oehler.at": "https://www.kastner-oehler.at/search?q={query}",
    "decathlon.at": "https://www.decathlon.at/search?Ntt={query}",
    "morawa.at": "https://www.morawa.at/search?s={query}",
    "gans.at": "https://www.gans.at/search?q={query}",

    "apotea.se": "https://www.apotea.se/sok?q={query}",
    "amazon.se": "https://www.amazon.se/s?k={query}",
    "zalando.se": "https://www.zalando.se/catalog/?q={query}",
    "adlibris.se": "https://www.adlibris.com/se/sok?q={query}",
    "hm.com": "https://www2.hm.com/sv_se/search-results.html?q={query}",
    "inet.se": "https://www.inet.se/search?q={query}",
    "ikea.com/se": "https://www.ikea.com/se/sv/search/?q={query}",
    "elgiganten.se": "https://www.elgiganten.se/search?SearchTerm={query}",
    "webhallen.com": "https://www.webhallen.com/se/search?searchString={query}",
    "boozt.com": "https://www.boozt.com/se/sv/s/search?q={query}",
    "sellpy.com": "https://www.sellpy.se/search?q={query}",

    "komplett.no": "https://www.komplett.no/search?q={query}",
    "finn.no": "https://www.finn.no/bap/forsale/search.html?q={query}",
    "zalando.no": "https://www.zalando.no/catalog/?q={query}",
    "elkjop.no": "https://www.elkjop.no/search?q={query}",
    "ikea.com/no": "https://www.ikea.com/no/no/search/?q={query}",
    "netonnet.no": "https://www.netonnet.no/art/search?query={query}",
    "biltema.no": "https://www.biltema.no/sok?query={query}",
    "clasohlson.com": "https://www.clasohlson.com/no/search?text={query}",
    "dressmann.com": "https://dressmann.com/no/search?q={query}",

    "nemlig.com": "https://www.nemlig.com/soegning?query={query}",
    "zalando.dk": "https://www.zalando.dk/catalog/?q={query}",
    "elgiganten.dk": "https://www.elgiganten.dk/search?SearchTerm={query}",
    "power.dk": "https://www.power.dk/soegning/?q={query}",
    "ikea.com/dk": "https://www.ikea.com/dk/da/search/?q={query}",
    "dba.dk": "https://www.dba.dk/soeg/?q={query}",
    "gucca.dk": "https://www.gucca.dk/search?query={query}",
    "thansen.dk": "https://www.thansen.dk/search?q={query}",
    "silvan.dk": "https://www.silvan.dk/search?q={query}",

    "allegro.pl": "https://allegro.pl/listing?string={query}",
    "empik.com": "https://www.empik.com/szukaj/produkt?q={query}",
    "mediaexpert.pl": "https://www.mediaexpert.pl/search?query={query}",
    "amazon.pl": "https://www.amazon.pl/s?k={query}",
    "oponeo.pl": "https://www.oponeo.pl/wyszukiwarka?text={query}",
    "ceneo.pl": "https://www.ceneo.pl/;szukaj-{query}",
    "sfd.pl": "https://sfd.pl/szukaj/?q={query}",
    "mi-store.pl": "https://mi-store.pl/search?q={query}",
    "czytam.pl": "https://czytam.pl/szukaj/?szukaj={query}",
    "dobraksiazka.pl": "https://www.dobraksiazka.pl/szukaj/?q={query}",

    "elara.ie": "https://www.elara.ie/search?q={query}",
    "mcsport.ie": "https://www.mcsport.ie/search?q={query}",
    "lenehans.ie": "https://www.lenehans.ie/search?q={query}",
    "agridirect.ie": "https://www.agridirect.ie/search?q={query}",
    "petmania.ie": "https://www.petmania.ie/search?q={query}",
    "aosom.ie": "https://www.aosom.ie/search?q={query}",
    "allirelandfoods.ie": "https://www.allirelandfoods.ie/search?q={query}",
    "rackzone.ie": "https://www.rackzone.ie/search?q={query}",

    "wildberries.ru": "https://www.wildberries.ru/catalog/0/search.aspx?search={query}",
    "ozon.ru": "https://www.ozon.ru/search/?text={query}",
    "market.yandex.ru": "https://market.yandex.ru/search?text={query}",
    "vkusvill.ru": "https://vkusvill.ru/search?text={query}",
    "lamoda.ru": "https://www.lamoda.ru/catalogsearch/result/?q={query}",
    "sportmaster.ru": "https://www.sportmaster.ru/search/result?query={query}",
    "dns-shop.ru": "https://www.dns-shop.ru/search/?q={query}",
    "magnit.ru": "https://magnit.ru/search/?q={query}",
    "metro-cc.ru": "https://online.metro-cc.ru/search?q={query}",
    "letu.ru": "https://www.letu.ru/search?text={query}",

    # Turkey
    "trendyol.com": "https://www.trendyol.com/sr?q={query}",
    "hepsiburada.com": "https://www.hepsiburada.com/ara?q={query}",
    "n11.com": "https://www.n11.com/arama?q={query}",
    "gittigidiyor.com": "https://www.gittigidiyor.com/arama/?k={query}",
    "pttavm.com": "https://www.pttavm.com/arama?q={query}",
    "mediamarkt.com.tr": "https://www.mediamarkt.com.tr/tr/search.html?query={query}",
    "pamuka.com.tr": "https://www.pamuka.com.tr/arama?q={query}",

    # Asia
    "rakuten.co.jp": "https://search.rakuten.co.jp/search/mall/{query}/",
    "amazon.co.jp": "https://www.amazon.co.jp/s?k={query}",
    "yodobashi.com": "https://www.yodobashi.com/ec/category/index.html?word={query}",
    "yahoo.co.jp": "https://shopping.yahoo.co.jp/search?p={query}",
    "uniqlo.com/jp": "https://www.uniqlo.com/jp/ja/search?q={query}",
    "joshinweb.jp": "https://joshinweb.jp/search?q={query}",
    "zozo.jp": "https://zozo.jp/search/?p_keyv={query}",
    "mercari.com": "https://www.mercari.com/jp/search/?keyword={query}",

    "taobao.com": "https://s.taobao.com/search?q={query}",
    "tmall.com": "https://list.tmall.com/search_product.htm?q={query}",
    "jd.com": "https://search.jd.com/Search?keyword={query}",
    "pinduoduo.com": "https://mobile.yangkeduo.com/search_result.html?search_key={query}",
    "1688.com": "https://s.1688.com/selloffer/offer_search.htm?keywords={query}",
    "vip.com": "https://category.vip.com/search-1-0-1.html?q={query}",
    "aliexpress.com": "https://www.aliexpress.com/wholesale?SearchText={query}",
    "dhgate.com": "https://www.dhgate.com/wholesale/search.do?searchkey={query}",

    "ssg.com": "https://www.ssg.com/search.ssg?target=all&query={query}",
    "smartstore.naver.com": "https://search.shopping.naver.com/search/all?query={query}",
    "lotteon.com": "https://www.lotteon.com/search/search?q={query}",
    "gmarket.co.kr": "https://browse.gmarket.co.kr/search?keyword={query}",
    "auction.co.kr": "https://browse.auction.co.kr/search?keyword={query}",
    "11st.co.kr": "https://search.11st.co.kr/Search.tmall?kwd={query}",
    "coupang.com": "https://www.coupang.com/np/search?q={query}",
    "kakao.com": "https://shoppinghow.kakao.com/top/search?q={query}",

    "amazon.in": "https://www.amazon.in/s?k={query}",
    "flipkart.com": "https://www.flipkart.com/search?q={query}",
    "myntra.com": "https://www.myntra.com/{query}",
    "nykaa.com": "https://www.nykaa.com/search/result/?q={query}",
    "meesho.com": "https://www.meesho.com/search?q={query}",
    "jiomart.com": "https://www.jiomart.com/search/{query}",
    "snapdeal.com": "https://www.snapdeal.com/search?keyword={query}",
    "shopsy.in": "https://www.shopsy.in/search?q={query}",
    "ajio.com": "https://www.ajio.com/search/?text={query}",
    "tatacliq.com": "https://www.tatacliq.com/search/?text={query}",

    "shopee.sg": "https://shopee.sg/search?keyword={query}",
    "lazada.sg": "https://www.lazada.sg/catalog/?q={query}",
    "amazon.sg": "https://www.amazon.sg/s?k={query}",
    "zalora.sg": "https://www.zalora.sg/catalog/?q={query}",
    "robinsons.com.sg": "https://www.robinsons.com.sg/search?q={query}",
    "fairprice.com.sg": "https://www.fairprice.com.sg/search?query={query}",
    "ikea.com/sg": "https://www.ikea.com/sg/en/search/?q={query}",
    "carousell.sg": "https://www.carousell.sg/search/{query}",
    "redmart.com": "https://redmart.lazada.sg/catalog/?q={query}",

    "shopee.com.my": "https://shopee.com.my/search?keyword={query}",
    "lazada.com.my": "https://www.lazada.com.my/catalog/?q={query}",
    "lelong.com.my": "https://www.lelong.com.my/kx/{query}",
    "pgmall.my": "https://pgmall.my/search?q={query}",
    "zalora.com.my": "https://www.zalora.com.my/catalog/?q={query}",
    "qoo10.my": "https://www.qoo10.my/s/{query}",
    "harveynorman.com.my": "https://www.harveynorman.com.my/search?q={query}",

    "shopee.co.th": "https://shopee.co.th/search?keyword={query}",
    "lazada.co.th": "https://www.lazada.co.th/catalog/?q={query}",
    "sasom.co.th": "https://www.sasom.co.th/search?q={query}",
    "konvy.com": "https://www.konvy.com/search?q={query}",
    "grab.com": "https://mart.grab.com/th/th/search?q={query}",
    "line.me": "https://shop.line.me/search?query={query}",
    "jib.co.th": "https://www.jib.co.th/web/index.php/search/searchproducts?searchkey={query}",

    "shopee.co.id": "https://shopee.co.id/search?keyword={query}",
    "tokopedia.com": "https://www.tokopedia.com/search?q={query}",
    "bukalapak.com": "https://www.bukalapak.com/products?search%5Bkeywords%5D={query}",
    "lazada.co.id": "https://www.lazada.co.id/catalog/?q={query}",
    "blibli.com": "https://www.blibli.com/cari/{query}",
    "ruparupa.com": "https://www.ruparupa.com/catalogsearch/result/?q={query}",
    "sociolla.com": "https://www.sociolla.com/search?q={query}",
    "orami.co.id": "https://www.orami.co.id/catalogsearch/result/?q={query}",
    "datascripmall.id": "https://www.datascripmall.id/catalogsearch/result/?q={query}",

    "shopee.ph": "https://shopee.ph/search?keyword={query}",
    "lazada.com.ph": "https://www.lazada.com.ph/catalog/?q={query}",
    "shopsm.com": "https://shopsm.com/search?q={query}",
    "watsons.com.ph": "https://www.watsons.com.ph/search?text={query}",
    "lg.com/ph": "https://www.lg.com/ph/search?q={query}",
    "concepcion.com.ph": "https://www.concepcion.com.ph/search?q={query}",
    "pursemaison.com": "https://pursemaison.com/search?q={query}",

    "shopee.vn": "https://shopee.vn/search?keyword={query}",
    "lazada.vn": "https://www.lazada.vn/catalog/?q={query}",
    "thegioididong.com": "https://www.thegioididong.com/tim-kiem?key={query}",
    "dienmayxanh.com": "https://www.dienmayxanh.com/tim-kiem?key={query}",
    "tiki.vn": "https://tiki.vn/search?q={query}",
    "meta.vn": "https://meta.vn/tim-kiem?q={query}",
    "fado.vn": "https://fado.vn/search?q={query}",
    "aeoneshop.com": "https://aeoneshop.com/search?q={query}",

    # Middle East & Africa
    "amazon.ae": "https://www.amazon.ae/s?k={query}",
    "noon.com": "https://www.noon.com/uae-en/search/?q={query}",
    "namshi.com": "https://www.namshi.com/uae-en/search?q={query}",
    "ounass.ae": "https://www.ounass.ae/search?q={query}",
    "sharafdg.com": "https://uae.sharafdg.com/search?q={query}",
    "6thstreet.com": "https://en-ae.6thstreet.com/catalogsearch/result/?q={query}",
    "carrefouruae.com": "https://www.carrefouruae.com/mafuae/en/search?q={query}",
    "mumzworld.com": "https://www.mumzworld.com/en/search?q={query}",

    "amazon.sa": "https://www.amazon.sa/s?k={query}",
    "alassly.com": "https://www.alassly.com/en/search?q={query}",
    "theoutlet.sa": "https://theoutlet.sa/en/search?q={query}",
    "eoutlet.sa": "https://www.eoutlet.sa/en/search?q={query}",
    "jazp.com": "https://www.jazp.com/en/search?q={query}",

    "ksp.co.il": "https://ksp.co.il/?select=1101&txt={query}",
    "shufersal.co.il": "https://www.shufersal.co.il/online/he/search?text={query}",
    "super-pharm.co.il": "https://shop.super-pharm.co.il/search?q={query}",
    "worker.co.il": "https://www.worker.co.il/search?q={query}",
    "israelcart.com": "https://www.israelcart.com/search?q={query}",
    "silal.com": "https://silal.com/search?q={query}",

    "jumia.com.eg": "https://www.jumia.com.eg/catalog/?q={query}",
    "amazon.eg": "https://www.amazon.eg/s?k={query}",
    "alymarket.com": "https://www.alymarket.com/search?q={query}",
    "ubuy.com.eg": "https://www.ubuy.com.eg/en/search/?q={query}",

    "takealot.com": "https://www.takealot.com/all?qsearch={query}",
    "superbalist.com": "https://superbalist.com/search?q={query}",
    "zando.co.za": "https://www.zando.co.za/catalog/?q={query}",
    "yuppiechef.com": "https://www.yuppiechef.com/spatula/search?keywords={query}",
    "checkers.co.za": "https://www.checkers.co.za/search/all?q={query}",
    "woolworths.co.za": "https://www.woolworths.co.za/cat?Ntt={query}",
    "clicks.co.za": "https://clicks.co.za/search?text={query}",
    "dis-chem.co.za": "https://www.dischem.co.za/search?text={query}",
    "makro.co.za": "https://www.makro.co.za/search?text={query}",
    "bobshop.co.za": "https://www.bobshop.co.za/search?q={query}",

    "jumia.com.ng": "https://www.jumia.com.ng/catalog/?q={query}",
    "konga.com": "https://www.konga.com/search?search={query}",
    "jiji.ng": "https://jiji.ng/search?query={query}",
    "payporte.com": "https://www.payporte.com/search?q={query}",
    "slot.ng": "https://slot.ng/search?q={query}",
    "kara.com.ng": "https://www.kara.com.ng/search?q={query}",
    "ajebomarket.com": "https://www.ajebomarket.com/search?q={query}",
    "supermart.ng": "https://www.supermart.ng/search?q={query}",

    "kilimall.co.ke": "https://www.kilimall.co.ke/catalog/?q={query}",
    "jumia.co.ke": "https://www.jumia.co.ke/catalog/?q={query}",
    "njirobale.com": "https://njirobale.com/search?q={query}",
    "masoko.com": "https://masoko.com/catalogsearch/result/?q={query}",

    # Oceania
    "amazon.com.au": "https://www.amazon.com.au/s?k={query}",
    "ebay.com.au": "https://www.ebay.com.au/sch/i.html?_nkw={query}",
    "theiconic.com.au": "https://www.theiconic.com.au/search?q={query}",
    "myer.com.au": "https://www.myer.com.au/search?query={query}",
    "bunnings.com.au": "https://www.bunnings.com.au/search/products?q={query}",
    "kmart.com.au": "https://www.kmart.com.au/search/?searchTerm={query}",
    "woolworths.com.au": "https://www.woolworths.com.au/shop/search/products?searchTerm={query}",
    "chemistwarehouse.com.au": "https://www.chemistwarehouse.com.au/search?searchtext={query}",
    "officeworks.com.au": "https://www.officeworks.com.au/shop/SearchDisplay?searchTerm={query}",
    "adorebeauty.com.au": "https://www.adorebeauty.com.au/search?q={query}",
    "countryroad.com.au": "https://www.countryroad.com.au/search?q={query}",

    "trademe.co.nz": "https://www.trademe.co.nz/a/marketplace/search?search_string={query}",
    "thewarehouse.co.nz": "https://www.thewarehouse.co.nz/search?text={query}",
    "noelleeming.co.nz": "https://www.noelleeming.co.nz/search?text={query}",
    "pbtech.co.nz": "https://www.pbtech.co.nz/search?sf={query}",
    "tum.co.nz": "https://www.tum.co.nz/search?q={query}",
    "gearshop.co.nz": "https://www.gearshop.co.nz/search?q={query}",
    "buykiwidirect.co.nz": "https://www.buykiwidirect.co.nz/search?q={query}",
    "mocka.co.nz": "https://www.mocka.co.nz/search?q={query}",
    "youknow.co.nz": "https://www.youknow.co.nz/search?q={query}",
}

# Units that mark a number as a variant attribute (capacity, size, power...),
# NOT as a model number: "256 gb", "45 w", "500 ml". These are unit symbols,
# not product vocabulary, and they are written in Latin letters on stores
# worldwide.
UNITS = {"gb", "tb", "mb", "kb", "mm", "cm", "m", "in", "inch", "hz", "mhz",
         "ghz", "mah", "w", "wh", "kg", "g", "gr", "ml", "l", "lt", "cl",
         "v", "a", "ah", "mp", "watt"}