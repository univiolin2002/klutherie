#!/usr/bin/env python3
"""Build klutherie.com from makers.py (data), en.py / ko.py (strings). Run: python3 build.py
English at /, Korean at /ko/. Every page links to its twin in the other language."""
import os, html
from makers import MAKERS, DEALERS, NEWS
import en, ko
from ko import MAKERS_KO, NEWS_KO, CITY_KO

ROOT = os.path.dirname(os.path.abspath(__file__))
E = html.escape

FONTS = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;6..72,400;6..72,500&family=Archivo:wght@400;500;600&family=Noto+Serif+KR:wght@400;500&family=Noto+Sans+KR:wght@400;500&display=swap">'
FORM_ENDPOINT = "https://formspree.io/f/mkjopnob"

LANGS = {"en": {"T": en.T, "prefix": ""}, "ko": {"T": ko.T, "prefix": "ko/"}}


def js(T):
    return f"""<script>
(function () {{
  var btn = document.getElementById('navtoggle');
  var nav = document.getElementById('nav');
  var slot = document.getElementById('navmobile');
  if (btn && nav && slot) {{
    btn.addEventListener('click', function () {{
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      if (open) {{ nav.classList.remove('nav--open'); nav.style.display = ''; }}
      else {{ slot.appendChild(nav); nav.classList.add('nav--open'); nav.style.display = 'flex'; }}
    }});
  }}
  var jf = document.getElementById('joinform');
  if (jf) {{
    jf.addEventListener('submit', function (e) {{
      e.preventDefault();
      var st = document.getElementById('formstatus'), b = document.getElementById('submitbtn');
      b.disabled = true; b.textContent = {T['f_sending']!r};
      fetch(jf.action, {{ method: 'POST', body: new FormData(jf), headers: {{ 'Accept': 'application/json' }} }})
        .then(function (r) {{ return r.ok ? r : r.json().then(function (j) {{ throw new Error(j && (j.error || (j.errors && j.errors[0] && j.errors[0].message)) || r.status); }}); }})
        .then(function () {{ st.hidden = false; st.textContent = {T['f_ok']!r}; jf.reset(); b.textContent = {T['f_sent']!r}; }})
        .catch(function (err) {{ st.hidden = false; st.textContent = {T['f_err']!r} + (err && err.message ? ' (' + err.message + ')' : ''); b.disabled = false; b.textContent = {T['f_send']!r}; }});
    }});
  }}
  var filters = document.getElementById('filters');
  if (filters) {{
    var state = {{ place: 'all', kind: 'all' }};
    var cards = document.querySelectorAll('[data-place]');
    var empty = document.getElementById('empty');
    function apply() {{
      var n = 0;
      cards.forEach(function (c) {{
        var ok = (state.place === 'all' || c.getAttribute('data-place') === state.place) &&
                 (state.kind === 'all' || c.getAttribute('data-kind').indexOf(state.kind) !== -1);
        c.hidden = !ok; if (ok) n++;
      }});
      if (empty) empty.hidden = n > 0;
    }}
    filters.addEventListener('click', function (e) {{
      var b = e.target.closest('button'); if (!b) return;
      var g = b.getAttribute('data-group'); state[g] = b.getAttribute('data-value');
      filters.querySelectorAll('button[data-group="' + g + '"]').forEach(function (x) {{ x.setAttribute('aria-pressed', 'false'); }});
      b.setAttribute('aria-pressed', 'true');
      apply();
    }});
  }}
}})();
</script>"""


class Site:
    """One language build. `rel` is the page path relative to the language root (e.g. 'makers/x.html')."""

    def __init__(self, lang):
        self.lang = lang
        self.T = LANGS[lang]["T"]
        self.prefix = LANGS[lang]["prefix"]

    # ---- localisation helpers ----
    def mk(self, m):
        """Return a localised copy of a maker record."""
        if self.lang == "en":
            return dict(m, display=m["name"])
        k = MAKERS_KO.get(m["slug"], {})
        d = dict(m)
        d["city"] = k.get("city", m["city"])
        d["country"] = k.get("country", m["country"])
        d["makes"] = k.get("makes", m["makes"])
        d["bio"] = k.get("bio", m["bio"])
        d["display"] = f'{k["name_ko"]} {m["name"]}' if k.get("name_ko") else m["name"]
        return d

    def nw(self, n):
        if self.lang == "en":
            return n
        return dict(n, **NEWS_KO.get(n["slug"], {}))

    def dealer_city(self, c):
        return CITY_KO.get(c, c) if self.lang == "ko" else c

    def place(self, m):
        return m["city"] or self.T["tbc"]

    def kind_label(self, kind):
        T = self.T
        return T["kind_both"] if "and" in kind else (T["kind_bows"] if kind == "bows" else T["kind_instruments"])

    # ---- page shell ----
    def page(self, rel, title, desc, body, current=None):
        T = self.T
        depth = rel.count("/")
        p = "../" * depth                      # to this language's root
        root = p + ("../" if self.prefix else "")   # to site root (for styles/images)
        other = ("../" * depth + "../" + rel) if self.lang == "ko" else ("../" * depth + "ko/" + rel)
        nav = "".join(
            f'<a href="{p}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
            for href, label in T["nav"]
        )
        switch = (f'<a class="lang" href="{other}" hreflang="ko" lang="ko">한국어</a>' if self.lang == "en"
                  else f'<a class="lang" href="{other}" hreflang="en" lang="en">English</a>')
        alt_en = ("https://klutherie.com/" + rel) if self.lang == "en" else ("https://klutherie.com/" + rel)
        alt_ko = "https://klutherie.com/ko/" + rel
        return f"""<!doctype html>
<html lang="{self.lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="ko" href="{alt_ko}">
{FONTS}
<link rel="stylesheet" href="{root}styles.css">
</head>
<body class="lang-{self.lang}">
<a class="skip" href="#main">{T['skip']}</a>
<header class="masthead">
  <div class="wrap masthead__inner">
    <a class="wordmark" href="{p}index.html">K<span>&middot;</span>Lutherie</a>
    <nav class="nav" id="nav" aria-label="Main">{nav}{switch}</nav>
    <div class="masthead__right">{switch}<button class="navtoggle" id="navtoggle" aria-expanded="false" aria-controls="nav"><span class="navtoggle__bars" aria-hidden="true"></span>{T['menu']}</button></div>
  </div>
  <div class="wrap" id="navmobile"></div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap foot__inner">
    <div>
      <div class="foot__mark">K<span>&middot;</span>Lutherie</div>
      <p class="foot__tag">{T['foot_tag']}</p>
    </div>
    <div class="foot__col">
      <strong>{T['foot_follow']}</strong>
      <a href="https://www.instagram.com/klutherie">Instagram</a><br>
      <a href="https://www.facebook.com/klutherie.official">Facebook</a>
    </div>
    <div class="foot__col">
      <strong>{T['foot_contact']}</strong>
      <a href="{p}join.html">{T['foot_apply']}</a>
    </div>
    <p class="foot__legal">{T['foot_legal']}</p>
  </div>
</footer>
{js(T)}
</body>
</html>
"""

    def maker_card(self, m, depth=0, small=False):
        p = "../" * depth
        root = p + ("../" if self.prefix else "")
        size = 480 if small else 960
        return f"""<article class="maker" data-place="{E(self.place(m))}" data-kind="{E(m['kind'])}">
  <a href="{p}makers/{m['slug']}.html">
    <div class="maker__plate"><img src="{root}images/makers/{m['photo']}-{size}.jpg" srcset="{root}images/makers/{m['photo']}-480.jpg 480w, {root}images/makers/{m['photo']}-960.jpg 960w" sizes="(max-width: 699px) 45vw, 25vw" width="4" height="5" alt="{E(m['display'])}" loading="lazy"></div>
    <h3 class="maker__name">{E(m['display'])}</h3>
    <p class="maker__meta">{E(self.place(m))}<br>{E(m['makes'].split(';')[0])}</p>
  </a>
</article>"""

    def write(self, rel, content):
        full = os.path.join(ROOT, self.prefix + rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content)

    # ---- build ----
    def build(self):
        T = self.T
        makers = [self.mk(m) for m in sorted(MAKERS, key=lambda m: m["sort"])]
        news = [self.nw(n) for n in NEWS]
        places = sorted({self.place(m) for m in makers if m["city"]})

        # index
        grid = "\n".join(self.maker_card(m, small=True) for m in makers)
        news_rows = "\n".join(
            f"""<article class="row">
  <div class="row__k">{E(n['date_text'])}</div>
  <div><h3 class="row__t"><a href="news/{n['slug']}.html">{E(n['title'])}</a></h3><p class="row__d">{E(n['summary'])}</p></div>
</article>""" for n in news)
        body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>{T['index_h1']}</h1></div>
    <div class="lede__aside"><p>{T['index_lede']}</p></div>
  </div>
  <section class="section" style="padding-top:0">
    <div class="section__head"><h2>{T['makers']}</h2><a class="more" href="makers.html">{T['all_makers']}</a></div>
    <div class="grid grid--6">
{grid}
    </div>
  </section>
  <section class="statement">
    <span class="label">{T['about']}</span>
    <div><p>{T['statement']}</p></div>
  </section>
  <section class="section">
    <div class="section__head"><h2>{T['news']}</h2><a class="more" href="news.html">{T['all']}</a></div>
    <div class="rows">
{news_rows}
    </div>
  </section>
</div>"""
        self.write("index.html", self.page("index.html", T["index_title"], T["index_desc"], body, "index.html"))

        # makers
        place_btns = "".join(f'<button data-group="place" data-value="{E(pl)}" aria-pressed="false">{E(pl)}</button>' for pl in places)
        grid = "\n".join(self.maker_card(m) for m in makers)
        body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>{T['makers']}</h1></div>
    <div class="lede__aside"><p>{T['makers_lede'].format(n=len(makers))}</p></div>
  </div>
  <div class="filters" id="filters">
    <button data-group="place" data-value="all" aria-pressed="true">{T['all_places']}</button>{place_btns}
    <span class="filters__sep" aria-hidden="true">|</span>
    <button data-group="kind" data-value="all" aria-pressed="true">{T['all_work']}</button>
    <button data-group="kind" data-value="instruments" aria-pressed="false">{T['instruments']}</button>
    <button data-group="kind" data-value="bows" aria-pressed="false">{T['bows']}</button>
  </div>
  <div class="grid">
{grid}
  </div>
  <p class="empty" id="empty" hidden>{T['no_match']}</p>
</div>"""
        self.write("makers.html", self.page("makers.html", T["makers_title"], T["makers_desc"], body, "makers.html"))

        # maker pages
        root1 = "../" + ("../" if self.prefix else "")
        for i, m in enumerate(makers):
            prev = makers[i - 1] if i > 0 else None
            nxt = makers[i + 1] if i < len(makers) - 1 else None
            dealers = "".join(
                f'<div class="row"><div class="row__k">{E(self.dealer_city(d["city"]))}</div><div class="row__v"><a href="{d["url"]}">{E(d["name"])}</a></div></div>'
                for d in m["dealers"]
            ) or f'<div class="row"><div class="row__k">&nbsp;</div><div class="row__v"><small>{T["tbc"]}</small></div></div>'
            work = "".join(
                f'<figure><div class="plate"><img src="{url}" alt="{E(cap)}" loading="lazy"></div><figcaption>{E(cap)}</figcaption></figure>'
                for cap, url in m["work"])
            work_sec = f"""<section class="section"><div class="section__head"><h2>{T['work']}</h2></div><div class="work">{work}</div></section>""" if work else ""
            bio = f'<p class="profile__bio">{E(m["bio"])}</p>' if m["bio"] else f'<p class="profile__bio is-empty">{T["bio_pending"]}</p>'
            pager = f"""<nav class="pager" aria-label="Makers">
    <span>{f'<a href="{prev["slug"]}.html">&lsaquo; {E(prev["display"])}</a>' if prev else ''}</span>
    <span>{f'<a href="{nxt["slug"]}.html">{E(nxt["display"])} &rsaquo;</a>' if nxt else ''}</span>
  </nav>"""
            body = f"""<div class="wrap">
  <div class="profile">
    <div>
      <div class="profile__plate"><img src="{root1}images/makers/{m['photo']}-full.jpg" alt="{E(m['display'])}"></div>
      <p class="caption">{T['photo_pending'] if m.get('photo_pending') else T['photo_courtesy']}</p>
    </div>
    <div class="profile__body">
      <span class="label">{E(self.kind_label(m['kind']))}</span>
      <h1>{E(m['display'])}</h1>
      <p class="profile__meta">{E(self.place(m))}{(', ' + E(m['country'])) if m['country'] else ''}<br>{E(m['makes'])}</p>
      {bio}
      <div class="facts rows">
        <div class="row"><div class="row__k">{T['works_in']}</div><div class="row__v">{E(self.place(m))}</div></div>
        <div class="row"><div class="row__k">{T['makes']}</div><div class="row__v">{E(m['makes'])}</div></div>
        {f'<div class="row"><div class="row__k">{T["website"]}</div><div class="row__v"><a href="{m["website"]}">{E(m["website"].replace("https://","").replace("http://","").rstrip("/"))}</a></div></div>' if m.get('website') else ''}
        {f'<div class="row"><div class="row__k">{T["instagram"]}</div><div class="row__v"><a href="https://www.instagram.com/{m["instagram"].lstrip("@")}">@{E(m["instagram"].lstrip("@"))}</a></div></div>' if m.get('instagram') else ''}
      </div>
    </div>
  </div>
  {work_sec}
  <section class="section"><div class="section__head"><h2>{T['dealers']}</h2></div><div class="rows">{dealers}</div></section>
  {pager}
</div>"""
            desc = (m["bio"][:150] + "…") if m["bio"] else f"{m['display']}, {m['makes']}."
            self.write(f"makers/{m['slug']}.html", self.page(f"makers/{m['slug']}.html", f"{m['display']} — K-Lutherie", desc, body, "makers.html"))

        # dealers
        rows = ""
        for d in DEALERS:
            carried = [m for m in makers if d in m["dealers"]]
            names = ", ".join(f'<a href="makers/{m["slug"]}.html">{E(m["display"])}</a>' for m in carried)
            rows += f"""<article class="row">
  <div class="row__k">{E(self.dealer_city(d['city']))}</div>
  <div><h3 class="row__t"><a href="{d['url']}">{E(d['name'])}</a></h3><p class="row__d">{names}</p></div>
</article>"""
        body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>{T['dealers']}</h1></div>
    <div class="lede__aside"><p>{T['dealers_lede']}</p></div>
  </div>
  <div class="rows">{rows}</div>
  <section class="split" style="margin-top:48px">
    <span class="label">{T['listing']}</span>
    <div class="split__body"><p>{T['dealers_listing'].format(join=f'<a href="join.html" style="text-decoration:underline;text-underline-offset:4px">{T["join_link"]}</a>')}</p></div>
  </section>
</div>"""
        self.write("dealers.html", self.page("dealers.html", T["dealers_title"], T["dealers_desc"], body, "dealers.html"))

        # news
        rows = "\n".join(
            f"""<article class="row">
  <div class="row__k">{E(n['date_text'])}</div>
  <div><h3 class="row__t"><a href="news/{n['slug']}.html">{E(n['title'])}</a></h3><p class="row__d">{E(n['summary'])}</p></div>
</article>""" for n in sorted(news, key=lambda n: n["date"], reverse=True))
        body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>{T['news']}</h1></div>
    <div class="lede__aside"><p>{T['news_lede']}</p></div>
  </div>
  <div class="rows">{rows}</div>
</div>"""
        self.write("news.html", self.page("news.html", T["news_title"], T["news_desc"], body, "news.html"))

        by_slug = {m["slug"]: m for m in makers}
        for n in news:
            paras = "".join(f"<p>{E(p)}</p>" for p in n["body"])
            related = ", ".join(f'<a href="../makers/{s}.html">{E(by_slug[s]["display"])}</a>' for s in n["makers"] if s in by_slug)
            sources = ", ".join(f'<a href="{u}">{E(t)}</a>' for t, u in n.get("sources", []))
            fig = ""
            if n.get("image"):
                u, cap = n["image"]
                fig = f'<figure class="article__fig"><div class="plate"><img src="{u}" alt="" loading="lazy"></div><figcaption>{E(n.get("image_caption", cap))}</figcaption></figure>'
            body = f"""<div class="wrap">
  <article class="article">
    <span class="label">{E(n['date_text'])}</span>
    <h1>{E(n['title'])}</h1>
    <p class="article__summary">{E(n['summary'])}</p>
    {fig}
    <div class="article__body">{paras}</div>
    <div class="article__links">
      {f'<p>{T["related_makers"]}: {related}</p>' if related else ''}
      {f'<p>{T["sources"]}: {sources}</p>' if sources else ''}
    </div>
  </article>
</div>"""
            self.write(f"news/{n['slug']}.html", self.page(f"news/{n['slug']}.html", f"{n['title']} — K-Lutherie", n["summary"], body, "news.html"))

        # join
        def chk(name, opts, en_opts):
            return '<div class="choices">' + "".join(f'<label><input type="checkbox" name="{name}" value="{E(v)}"> {E(o)}</label>' for o, v in zip(opts, en_opts)) + '</div>'
        def rad(name, opts, en_opts):
            return '<div class="choices">' + "".join(f'<label><input type="radio" name="{name}" value="{E(v)}"> {E(o)}</label>' for o, v in zip(opts, en_opts)) + '</div>'
        body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>{T['join_h1']}</h1></div>
    <div class="lede__aside"><p>{T['join_lede']}</p></div>
  </div>
  <form class="form" id="joinform" action="{FORM_ENDPOINT}" method="POST" enctype="multipart/form-data">
    <input type="hidden" name="_subject" value="K-Lutherie application">
    <input type="hidden" name="language" value="{self.lang}">
    <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
    <fieldset>
      <legend>{T['f_who']}</legend>
      <div class="field"><label for="name">{T['f_name']} <small>{T['f_name_s']}</small></label><input type="text" id="name" name="name" required></div>
      <div class="field"><label for="name_ko">{T['f_name_ko']} <small>{T['f_opt']}</small></label><input type="text" id="name_ko" name="name_korean"></div>
      <div class="field"><label>{T['f_conn']}</label>{chk('korean_connection', T['f_conn_opts'], en.T['f_conn_opts'])}</div>
      <div class="field"><label for="born">{T['f_born']} <small>{T['f_opt']}</small></label><input type="text" id="born" name="born" placeholder="{E(T['f_born_ph'])}"></div>
    </fieldset>
    <fieldset>
      <legend>{T['f_where']}</legend>
      <div class="field"><label for="city">{T['f_city']}</label><input type="text" id="city" name="city" required placeholder="{E(T['f_city_ph'])}"></div>
      <div class="field"><label for="workshop">{T['f_workshop']}</label><input type="text" id="workshop" name="workshop" placeholder="{E(T['f_workshop_ph'])}"></div>
    </fieldset>
    <fieldset>
      <legend>{T['f_what']}</legend>
      <div class="field"><label>{T['f_kind']}</label>{rad('work_type', T['f_kind_opts'], en.T['f_kind_opts'])}</div>
      <div class="field"><label>{T['f_instr']}</label>{chk('instruments', T['f_instr_opts'], en.T['f_instr_opts'])}</div>
      <div class="field"><label for="instruments_other">{T['f_instr_other']}</label><input type="text" id="instruments_other" name="instruments_other"></div>
    </fieldset>
    <fieldset>
      <legend>{T['f_bg']}</legend>
      <div class="field"><label for="training">{T['f_training']} <small>{T['f_training_s']}</small></label><textarea id="training" name="training" placeholder="{E(T['f_training_ph'])}"></textarea></div>
      <div class="field"><label for="awards">{T['f_awards']} <small>{T['f_awards_s']}</small></label><textarea id="awards" name="awards" placeholder="{E(T['f_awards_ph'])}"></textarea></div>
      <div class="field"><label for="bio">{T['f_bio']} <small>{T['f_bio_s']}</small></label><textarea id="bio" name="biography" required style="min-height:180px"></textarea></div>
      <div class="field"><label for="dealers">{T['f_dealers']} <small>{T['f_dealers_s']}</small></label><textarea id="dealers" name="dealers" placeholder="{E(T['f_dealers_ph'])}"></textarea></div>
    </fieldset>
    <fieldset>
      <legend>{T['f_links']}</legend>
      <div class="field"><label for="instagram">{T['f_ig']}</label><input type="text" id="instagram" name="instagram" placeholder="{E(T['f_ig_ph'])}"></div>
      <div class="field"><label for="website">{T['f_web']} <small>{T['f_opt']}</small></label><input type="url" id="website" name="website" placeholder="https://"></div>
      <div class="field"><label for="email">{T['f_email']}</label><input type="email" id="email" name="email" required></div>
      <div class="field"><label for="phone">{T['f_phone']} <small>{T['f_phone_s']}</small></label><input type="tel" id="phone" name="phone"></div>
    </fieldset>
    <fieldset>
      <legend>{T['f_photo']}</legend>
      <div class="field">
        <label for="photo">{T['f_photo_l']}</label>
        <input type="url" id="photo" name="photo_link" placeholder="https://drive.google.com/…">
        <p class="hint">{T['f_photo_hint']}</p>
      </div>
      <div class="field"><div class="choices"><label><input type="checkbox" name="photo_rights" value="yes" required> {T['f_rights']}</label></div></div>
    </fieldset>
    <fieldset>
      <legend>{T['f_else']}</legend>
      <div class="field"><label for="notes">{T['f_notes']} <small>{T['f_notes_s']}</small></label><textarea id="notes" name="notes"></textarea></div>
    </fieldset>
    <button class="btn btn--solid btn--lg" type="submit" id="submitbtn">{T['f_send']}</button>
    <p class="form__note">{T['f_note']}</p>
    <p class="form__status" id="formstatus" hidden></p>
  </form>
</div>"""
        self.write("join.html", self.page("join.html", T["join_title"], T["join_desc"], body, "join.html"))

        # about
        body = f"""<div class="wrap">
  <div class="lede"><div class="lede__text"><h1>{T['about']}</h1></div></div>
  <div class="prose">
    <p class="lead">{T['about_lead']}</p>
    <p>{T['about_p1']}</p>
  </div>
  <section class="split"><span class="label">{T['what_listed']}</span><div class="split__body"><p>{T['about_p2']}</p></div></section>
  <section class="split" id="listing"><span class="label">{T['being_listed']}</span><div class="split__body">
    <p>{T['about_p3a']}<a href="join.html" style="text-decoration:underline;text-underline-offset:4px">{T['about_p3_link']}</a>{T['about_p3b']}</p>
    <p>{T['about_p4'].format(join=f'<a href="join.html" style="text-decoration:underline;text-underline-offset:4px">{T["join_link"]}</a>')}</p></div></section>
  <section class="split"><span class="label">{T['who_runs']}</span><div class="split__body"><p>{T['about_p5']}</p></div></section>
  <section class="split"><span class="label">{T['follow']}</span><div class="split__body"><p><a href="https://www.instagram.com/klutherie">Instagram @klutherie</a><br><a href="https://www.facebook.com/klutherie.official">Facebook /klutherie.official</a></p></div></section>
</div>"""
        self.write("about.html", self.page("about.html", T["about_title"], T["about_desc"], body, "about.html"))
        return len(makers), len(news)


for lang in ("en", "ko"):
    nm, nn = Site(lang).build()
    print(f"[{lang}] built: index, makers, {nm} maker pages, dealers, news, {nn} articles, join, about")
