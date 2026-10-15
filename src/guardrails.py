"""Deterministic routing and evidence validation. User assertions are not evidence."""
import re
from .config import ALLOWED_URLS


def detect_language(text):
    if re.search(r'[\u0600-\u06ff]', text):
        return 'ar'
    if re.search(r'\b(cu[aá]nto|precio|incluye|incluido|tratamiento|recuperaci[oó]n|barato|puedes|clima)\b', text, re.I):
        return 'es'
    if re.search(r'\b(kitna|kitni|kya|kia|mujhe|mujhy|mujy|kaisy|kaise|hai|hain|qeemat|batao|chahiye)\b', text, re.I):
        return 'ur'
    return 'en'


TEXT = {
    'en': {
        'not_found': "I couldn't find that information in the seven provided pages. Please contact PlacidWay through the source page for a free quote.",
        'medical': "I can't assess whether a treatment is safe or suitable for your condition. Please speak with a qualified doctor who knows your medical history.",
        'appointment': "I can't book appointments. Please use the contact or free quote form on the PlacidWay source page.",
        'declined': "I can help with information on the seven provided PlacidWay pages. I can't answer that request from those sources.",
        'unavailable': 'Service temporarily unavailable. Please try again. You can also contact PlacidWay through a source page for a free quote.',
        'excerpt_fallback': 'AI summaries are temporarily unavailable. Showing the original source text instead.',
        'comparison': "I couldn't verify a like-for-like comparison for both countries in the provided pages. Different treatments or package inclusions should not be compared as equivalent. Please request a free quote from PlacidWay.",
        'recovery': "The provided package page does not state a verified recovery time. A treatment program's duration is not the same as recovery time. Please contact the clinic through PlacidWay for a free quote and recovery guidance.",
        'trick': "I can't confirm the price you suggested. Here is what the provided page actually lists:",
        'evidence': 'The provided page states:',
        'disclaimer': 'Website information only; not personal medical advice. Treatment descriptions do not establish safety or effectiveness.',
    },
    'ur': {
        'not_found': 'Diye gaye 7 pages mein ye maloomat nahi mili. Free quote ke liye source page ke zariye PlacidWay se rabta karein.',
        'medical': 'Main aap ki condition ke liye treatment ki safety ya suitability tay nahi kar sakta. Apni medical history jaannay wale qualified doctor se baat karein.',
        'appointment': 'Main appointment book nahi kar sakta. PlacidWay ke source page par contact ya free quote form use karein.',
        'declined': 'Main sirf diye gaye 7 PlacidWay pages ki maloomat mein madad kar sakta hoon. Is sawal ka jawab un sources se nahi de sakta.',
        'unavailable': 'Service filhal available nahi. Dobara koshish karein ya source page par free quote ke liye rabta karein.',
        'excerpt_fallback': 'AI summary filhal available nahi. Source page ka asal text dikhaya ja raha hai.',
        'comparison': 'Dono mulkon ke liye aik jaisay treatment aur inclusions ka comparison verify nahi hua. PlacidWay se free quote lein.',
        'recovery': 'Package page par verified recovery time nahi diya gaya. Treatment ki duration aur recovery time aik cheez nahi. Clinic se poochhein.',
        'trick': 'Main aap ki batayi hui qeemat confirm nahi kar sakta. Source page par ye likha hai:',
        'evidence': 'Diye gaye source page par ye likha hai:',
        'disclaimer': 'Ye website ki maloomat hai, personal medical advice nahi. Treatment ki description safety ya effectiveness ka saboot nahi.',
    },
    'es': {
        'not_found': 'No encontré esa información en las siete páginas proporcionadas. Contacta con PlacidWay mediante la página fuente para una cotización gratuita.',
        'medical': 'No puedo evaluar si un tratamiento es seguro o adecuado para tu condición. Consulta a un médico cualificado que conozca tu historial clínico.',
        'appointment': 'No puedo reservar citas. Utiliza el formulario de contacto o de cotización gratuita de la página fuente de PlacidWay.',
        'declined': 'Solo puedo ayudar con información de las siete páginas de PlacidWay proporcionadas. No puedo responder a esa solicitud con esas fuentes.',
        'unavailable': 'Servicio temporalmente no disponible. Inténtalo de nuevo o solicita una cotización gratuita en la página fuente.',
        'excerpt_fallback': 'Los resúmenes de IA no están disponibles temporalmente. Se muestra el texto original de la fuente.',
        'comparison': 'No pude verificar una comparación equivalente entre ambos países. Solicita una cotización gratuita a PlacidWay.',
        'recovery': 'La página del paquete no indica un tiempo de recuperación verificado. La duración del programa no equivale al tiempo de recuperación. Consulta con la clínica.',
        'trick': 'No puedo confirmar el precio que sugieres. Esto es lo que indica la página proporcionada:',
        'evidence': 'La página proporcionada indica:',
        'disclaimer': 'Información del sitio web; no es asesoramiento médico personal. Las descripciones no demuestran seguridad ni eficacia.',
    },
    'ar': {
        'not_found': 'لم أجد هذه المعلومات في الصفحات السبع المقدمة. يرجى التواصل مع PlacidWay عبر صفحة المصدر للحصول على عرض سعر مجاني.',
        'medical': 'لا أستطيع تقييم سلامة العلاج أو ملاءمته لحالتك. يرجى استشارة طبيب مؤهل يعرف تاريخك الطبي.',
        'appointment': 'لا أستطيع حجز المواعيد. يرجى استخدام نموذج التواصل أو عرض السعر المجاني في صفحة المصدر.',
        'declined': 'يمكنني المساعدة فقط بالمعلومات الواردة في صفحات PlacidWay السبع المقدمة. لا أستطيع الإجابة عن هذا الطلب من تلك المصادر.',
        'unavailable': 'الخدمة غير متاحة مؤقتاً. يرجى المحاولة مرة أخرى أو طلب عرض سعر عبر صفحة المصدر.',
        'excerpt_fallback': 'ملخصات الذكاء الاصطناعي غير متاحة مؤقتاً. يتم عرض النص الأصلي من المصدر.',
        'comparison': 'لم أتمكن من التحقق من مقارنة متكافئة بين البلدين. يرجى طلب عرض سعر مجاني من PlacidWay.',
        'recovery': 'صفحة الباقة لا تحدد مدة تعافٍ موثقة. مدة البرنامج ليست مدة التعافي. يرجى سؤال العيادة.',
        'trick': 'لا أستطيع تأكيد السعر الذي ذكرته. هذا ما ورد في صفحة المصدر:',
        'evidence': 'تذكر صفحة المصدر ما يلي:',
        'disclaimer': 'معلومات من الموقع وليست نصيحة طبية شخصية. وصف العلاج لا يثبت سلامته أو فعاليته.',
    },
}


def message(key, language='en'):
    return TEXT.get(language, TEXT['en'])[key]


def route(question):
    q = question.lower()
    if re.search(r'ignore (all |any |the )?(previous|system|prior)|reveal.*(prompt|key|token)|system prompt', q):
        return 'declined'
    if re.search(r'\b(diabetes|pregnant|pregnancy|diagnose|diagnosis|my medication|my condition|should i stop|cure me|safe for me|safe for my)\b|آمن.*حالتي|seguro.*(mi|diabetes)', q):
        return 'medical'
    if (re.search(r'\b(safe|safety|suitable|recommend|should|cure)\b', q) and re.search(r'\b(i|me|my)\b', q)) or re.search(r'\b(safe|suitable) (for|if)\b', q):
        return 'medical'
    if re.search(r'\b(book|schedule|reserve)\b.*\b(appointment|consultation|tomorrow)\b|reserva.*cita|حجز.*موعد', q):
        return 'appointment'
    if re.search(r'\b(weather|football|bitcoin|recipe|president|clima)\b|الطقس', q):
        return 'declined'
    return None


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


def numbers(text):
    return {m.replace(',', '').lstrip('0') or '0' for m in re.findall(r'(?<!\w)\d[\d,]*(?:\.\d+)?', text)}


def validate_output(payload, retrieved):
    """Check schema, retrieved-only IDs, verbatim evidence and per-claim numbers.

    This is a conservative guard, not a proof of semantic entailment.
    Price answers are rendered from exact evidence instead of model paraphrases.
    """
    if not isinstance(payload, dict) or payload.get('status') not in ('answered', 'not_found', 'declined', 'medical'):
        return False
    if payload['status'] != 'answered':
        return True
    available = {c['id']: c for c in retrieved if c['url'] in ALLOWED_URLS}
    ids, claims = payload.get('used_chunk_ids'), payload.get('claims')
    if not isinstance(ids, list) or not ids or not set(ids) <= set(available):
        return False
    if not isinstance(claims, list) or not 1 <= len(claims) <= 6:
        return False
    for claim in claims:
        if not isinstance(claim, dict) or claim.get('chunk_id') not in ids:
            return False
        text, quote = claim.get('text'), claim.get('quote')
        if not isinstance(text, str) or not isinstance(quote, str) or not 12 <= len(quote) <= 1800 or not text or len(text) > 1600:
            return False
        chunk = available[claim['chunk_id']]
        if normalize(quote) not in normalize(chunk['text']):
            return False
        supporting = quote + ' ' + chunk.get('heading', '')
        if not numbers(text) <= numbers(supporting):
            return False
        if not set(re.findall(r'\b(?:USD|EUR|MXN|GBP|CAD|AUD|TRY)\b', text)) <= set(re.findall(r'\b(?:USD|EUR|MXN|GBP|CAD|AUD|TRY)\b', supporting)):
            return False
        if '%' in text and '%' not in supporting:
            return False
        if re.search(r'https?://|www\.|\]\(', text + quote, re.I):
            return False
        # Never render instruction-like snippets as patient information.
        if re.search(r'ignore.*instructions|system prompt|api[_ ]key|admin[_ ]token', text + quote, re.I):
            return False
    return set(ids) == {c['chunk_id'] for c in claims}
