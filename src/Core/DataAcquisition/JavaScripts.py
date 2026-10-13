SCROLL_JS = """async () => {  // scroll down step by step (lazy-loaded products and reviews appear), end at the bottom
    const height = () => document.documentElement.scrollHeight;
    const steps = Math.min(8, Math.max(2, Math.ceil(height() / window.innerHeight)));
    for (let i = 0; i < steps; i++) {
        window.scrollBy(0, Math.max(window.innerHeight, height() / steps));
        await new Promise(r => setTimeout(r, 150));
    }
    window.scrollTo(0, height()); }"""

COUNT_JS = "document.getElementsByTagName('*').length"

REVIEW_WORDS_JS = (r"review|rezension|bewertung|avis|opini|reseñ|resen|recensi|yorum|değerlendirme|degerlendirme|"
                   r"comment|valoraci|avalia|beoordeling|recensie|opinie|отзыв|レビュー|口コミ|评价|评论|리뷰|후기|مراجع|تقييم")

CLICKABLE_JS = """const clickable = () => Array.from(document.querySelectorAll(
        'button, [role="tab"], [role="button"], a[href^="#"], a[href^="javascript"], summary'))
    .filter(el => el.offsetParent !== null && (el.innerText || '').trim().length > 0 && (el.innerText || '').trim().length < 60);
const isMore = /more|fazla|daha|mehr|weitere|plus|más|mas|altri|mais|meer|więcej|еще|ещё|もっと|更多|더보기|المزيد|all|tüm|alle|tous|todas|tutte/i;
const notOpener = /write|yaz|schreib|écri|escrib|scriv|ekle|add|submit|gönder|post|login|giriş/i;"""

# Clicks the "Reviews" tab (only elements that stay on the page; a tab that is already open is left alone)
CLICK_REVIEW_TAB_JS = """(words) => { const isReview = new RegExp(words, 'i'); """ + CLICKABLE_JS + """
    const tab = clickable().find(el => isReview.test(el.innerText) && !isMore.test(el.innerText) && !notOpener.test(el.innerText));
    if (!tab || tab.getAttribute('aria-selected') === 'true' || tab.getAttribute('aria-expanded') === 'true' ||
        (tab.tagName === 'SUMMARY' && tab.parentElement && tab.parentElement.open)) return false;
    tab.click();
    return true; }"""

# Clicks one "more reviews" button; returns the number of elements before the click (-1 = no button)
CLICK_MORE_REVIEWS_JS = """(words) => { const isReview = new RegExp(words, 'i'); """ + CLICKABLE_JS + """
    const more = clickable().find(el => isMore.test(el.innerText) && !notOpener.test(el.innerText) && (isReview.test(el.innerText)
        || isReview.test((el.closest('[class*="review" i],[id*="review" i],[class*="comment" i],[class*="yorum" i]') || {}).className || '')));
    if (!more) return -1;
    const before = document.getElementsByTagName('*').length;
    more.click();
    return before; }"""