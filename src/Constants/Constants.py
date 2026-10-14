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