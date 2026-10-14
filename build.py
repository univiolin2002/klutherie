#!/usr/bin/env python3
"""Build klutherie.com from makers.py. Run: python3 build.py"""
import os, html
from makers import MAKERS, DEALERS, NEWS

ROOT = os.path.dirname(os.path.abspath(__file__))
E = html.escape

FONTS = '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,300;6..72,400;6..72,500&family=Archivo:wght@400;500;600&display=swap">'

NAV = [("makers.html", "Makers"), ("dealers.html", "Dealers"), ("news.html", "News & Events"), ("about.html", "About"), ("join.html", "Join")]
FORM_ENDPOINT = "https://formspree.io/f/REPLACE_ME"

JS = """<script>
(function () {
  var btn = document.getElementById('navtoggle');
  var nav = document.getElementById('nav');
  var slot = document.getElementById('navmobile');
  if (btn && nav && slot) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      if (open) { nav.classList.remove('nav--open'); nav.style.display = ''; }
      else { slot.appendChild(nav); nav.classList.add('nav--open'); nav.style.display = 'flex'; }
    });
  }
  var jf = document.getElementById('joinform');
  if (jf) {
    jf.addEventListener('submit', function (e) {
      e.preventDefault();
      var st = document.getElementById('formstatus'), btn = document.getElementById('submitbtn');
      btn.disabled = true; btn.textContent = 'Sending…';
      fetch(jf.action, { method: 'POST', body: new FormData(jf), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.ok ? r : Promise.reject(r); })
        .then(function () { st.hidden = false; st.textContent = 'Thank you. Your application has been sent. We will be in touch within a week.'; jf.reset(); btn.textContent = 'Sent'; })
        .catch(function () { st.hidden = false; st.textContent = 'Something went wrong. Please email your details to owensparkley@gmail.com instead.'; btn.disabled = false; btn.textContent = 'Send application'; });
    });
  }
  var filters = document.getElementById('filters');
  if (filters) {
    var state = { place: 'all', kind: 'all' };
    var cards = document.querySelectorAll('[data-place]');
    var empty = document.getElementById('empty');
    function apply() {
      var n = 0;
      cards.forEach(function (c) {
        var ok = (state.place === 'all' || c.getAttribute('data-place') === state.place) &&
                 (state.kind === 'all' || c.getAttribute('data-kind').indexOf(state.kind) !== -1);
        c.hidden = !ok; if (ok) n++;
      });
      if (empty) empty.hidden = n > 0;
    }
    filters.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var g = b.getAttribute('data-group'); state[g] = b.getAttribute('data-value');
      filters.querySelectorAll('button[data-group="' + g + '"]').forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
      b.setAttribute('aria-pressed', 'true');
      apply();
    });
  }
})();
</script>"""


def page(title, desc, body, current=None, depth=0):
    p = "../" * depth
    nav = "".join(
        f'<a href="{p}{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
        for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
{FONTS}
<link rel="stylesheet" href="{p}styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="wrap masthead__inner">
    <a class="wordmark" href="{p}index.html">K<span>&middot;</span>Lutherie</a>
    <nav class="nav" id="nav" aria-label="Main">{nav}</nav>
    <button class="navtoggle" id="navtoggle" aria-expanded="false" aria-controls="nav"><span class="navtoggle__bars" aria-hidden="true"></span>Menu</button>
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
      <p class="foot__tag">Korean makers of stringed instruments and bows, wherever they work.</p>
    </div>
    <div class="foot__col">
      <strong>Follow</strong>
      <a href="https://www.instagram.com/klutherie">Instagram</a><br>
      <a href="https://www.facebook.com/klutherie.official">Facebook</a>
    </div>
    <div class="foot__col">
      <strong>Contact</strong>
      owensparkley@gmail.com<br>
      <a href="{p}join.html">Apply to be listed</a>
    </div>
    <p class="foot__legal">&copy; 2026 K-Lutherie. Photographs courtesy of the makers. An independent project by Owen Hojoon Lee, Los Angeles.</p>
  </div>
</footer>
{JS}
</body>
</html>
"""


def place(m):
    return m["city"] or "To be confirmed"


def maker_card(m, depth=0, small=False):
    p = "../" * depth
    size = 480 if small else 960
    return f"""<article class="maker" data-place="{E(place(m))}" data-kind="{E(m['kind'])}">
  <a href="{p}makers/{m['slug']}.html">
    <div class="maker__plate"><img src="{p}images/makers/{m['photo']}-{size}.jpg" srcset="{p}images/makers/{m['photo']}-480.jpg 480w, {p}images/makers/{m['photo']}-960.jpg 960w" sizes="(max-width: 699px) 45vw, 25vw" width="4" height="5" alt="{E(m['name'])}" loading="lazy"></div>
    <h3 class="maker__name">{E(m['name'])}</h3>
    <p class="maker__meta">{E(place(m))}<br>{E(m['makes'].split(';')[0])}</p>
  </a>
</article>"""


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


makers = sorted(MAKERS, key=lambda m: m["sort"])
places = sorted({place(m) for m in makers if m["city"]})

# ---------- index ----------
grid = "\n".join(maker_card(m, small=True) for m in makers)
news_rows = "\n".join(
    f"""<article class="row">
  <div class="row__k">{E(n['date_text'])}</div>
  <div><h3 class="row__t"><a href="news/{n['slug']}.html">{E(n['title'])}</a></h3><p class="row__d">{E(n['summary'])}</p></div>
</article>""" for n in NEWS
)
body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>Korean makers of stringed instruments and bows, wherever they work.</h1></div>
    <div class="lede__aside"><p>K-Lutherie is a register of luthiers and archetiers of Korean origin: who they are, where they work, what they make, and where their instruments can be found.</p></div>
  </div>

  <section class="section" style="padding-top:0">
    <div class="section__head"><h2>Makers</h2><a class="more" href="makers.html">All makers &rsaquo;</a></div>
    <div class="grid grid--6">
{grid}
    </div>
  </section>

  <section class="statement">
    <span class="label">About</span>
    <div><p>Korean luthiers now work in Cremona, Seoul, Los Angeles and beyond, winning medals at the Triennale and the VSA and sitting on international juries. Their work is known to the players who own it and the dealers who sell it, and to few others. This site puts them in one place.</p></div>
  </section>

  <section class="section">
    <div class="section__head"><h2>News &amp; Events</h2><a class="more" href="news.html">All &rsaquo;</a></div>
    <div class="rows">
{news_rows}
    </div>
  </section>
</div>"""
write("index.html", page("K-Lutherie", "A register of Korean makers of stringed instruments and bows, wherever they work.", body, "index.html"))

# ---------- makers ----------
place_btns = "".join(f'<button data-group="place" data-value="{E(pl)}" aria-pressed="false">{E(pl)}</button>' for pl in places)
grid = "\n".join(maker_card(m) for m in makers)
body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>Makers</h1></div>
    <div class="lede__aside"><p>{len(makers)} makers, listed alphabetically by surname. Filter by where they work or what they make.</p></div>
  </div>
  <div class="filters" id="filters">
    <button data-group="place" data-value="all" aria-pressed="true">All places</button>{place_btns}
    <span class="filters__sep" aria-hidden="true">|</span>
    <button data-group="kind" data-value="all" aria-pressed="true">All work</button>
    <button data-group="kind" data-value="instruments" aria-pressed="false">Instruments</button>
    <button data-group="kind" data-value="bows" aria-pressed="false">Bows</button>
  </div>
  <div class="grid">
{grid}
  </div>
  <p class="empty" id="empty" hidden>No makers match this selection.</p>
</div>"""
write("makers.html", page("Makers — K-Lutherie", "All makers listed on K-Lutherie, by place and by kind of work.", body, "makers.html"))

# ---------- maker pages ----------
for i, m in enumerate(makers):
    prev = makers[i - 1] if i > 0 else None
    nxt = makers[i + 1] if i < len(makers) - 1 else None
    dealers = "".join(
        f'<div class="row"><div class="row__k">{E(d["city"])}</div><div class="row__v"><a href="{d["url"]}">{E(d["name"])}</a></div></div>'
        for d in m["dealers"]
    ) or '<div class="row"><div class="row__k">&nbsp;</div><div class="row__v"><small>To be confirmed</small></div></div>'
    work = "".join(
        f'<figure><div class="plate"><img src="{url}" alt="{E(cap)}" loading="lazy"></div><figcaption>{E(cap)}</figcaption></figure>'
        for cap, url in m["work"]
    )
    work_sec = f"""<section class="section">
    <div class="section__head"><h2>Work</h2></div>
    <div class="work">{work}</div>
  </section>""" if work else ""
    bio = f'<p class="profile__bio">{E(m["bio"])}</p>' if m["bio"] else '<p class="profile__bio is-empty">Biography to follow.</p>'
    pager = f"""<nav class="pager" aria-label="Makers">
    <span>{f'<a href="{prev["slug"]}.html">&lsaquo; {E(prev["name"])}</a>' if prev else ''}</span>
    <span>{f'<a href="{nxt["slug"]}.html">{E(nxt["name"])} &rsaquo;</a>' if nxt else ''}</span>
  </nav>"""
    body = f"""<div class="wrap">
  <div class="profile">
    <div>
      <div class="profile__plate"><img src="../images/makers/{m['photo']}-full.jpg" alt="{E(m['name'])}"></div>
      <p class="caption">{'Photograph to follow' if m.get('photo_pending') else 'Photograph courtesy of the maker'}</p>
    </div>
    <div class="profile__body">
      <span class="label">{E(m['kind'].replace('and', '&amp;'))}</span>
      <h1>{E(m['name'])}</h1>
      <p class="profile__meta">{E(place(m))}{(', ' + E(m['country'])) if m['country'] else ''}<br>{E(m['makes'])}</p>
      {bio}
      <div class="facts rows">
        <div class="row"><div class="row__k">Works in</div><div class="row__v">{E(place(m))}</div></div>
        <div class="row"><div class="row__k">Makes</div><div class="row__v">{E(m['makes'])}</div></div>
        {f'<div class="row"><div class="row__k">Website</div><div class="row__v"><a href="{m["website"]}">{E(m["website"].replace("https://","").replace("http://","").rstrip("/"))}</a></div></div>' if m.get('website') else ''}
        {f'<div class="row"><div class="row__k">Instagram</div><div class="row__v"><a href="https://www.instagram.com/{m["instagram"].lstrip("@")}">@{E(m["instagram"].lstrip("@"))}</a></div></div>' if m.get('instagram') else ''}
      </div>
    </div>
  </div>
  {work_sec}
  <section class="section">
    <div class="section__head"><h2>Dealers</h2></div>
    <div class="rows">{dealers}</div>
  </section>
  {pager}
</div>"""
    desc = (m["bio"][:150] + "…") if m["bio"] else f"{m['name']}, {m['makes']}."
    write(f"makers/{m['slug']}.html", page(f"{m['name']} — K-Lutherie", desc, body, "makers.html", depth=1))

# ---------- dealers ----------
rows = ""
for d in DEALERS:
    carried = [m for m in makers if d in m["dealers"]]
    names = ", ".join(f'<a href="makers/{m["slug"]}.html">{E(m["name"])}</a>' for m in carried)
    rows += f"""<article class="row">
  <div class="row__k">{E(d['city'])}</div>
  <div><h3 class="row__t"><a href="{d['url']}">{E(d['name'])}</a></h3><p class="row__d">{names}</p></div>
</article>"""
body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>Dealers</h1></div>
    <div class="lede__aside"><p>Shops and ateliers that carry work by the makers listed here. Listing is a standing relationship, not current stock; contact the dealer for what is available.</p></div>
  </div>
  <div class="rows">{rows}</div>
  <section class="split" style="margin-top:48px">
    <span class="label">Listing</span>
    <div class="split__body"><p>Dealers who carry instruments or bows by a Korean maker are welcome to be listed. Write to owensparkley@gmail.com with the shop name, city, website and the makers carried.</p></div>
  </section>
</div>"""
write("dealers.html", page("Dealers — K-Lutherie", "Shops and ateliers that carry work by Korean makers.", body, "dealers.html"))

# ---------- news ----------
rows = "\n".join(
    f"""<article class="row">
  <div class="row__k">{E(n['date_text'])}</div>
  <div><h3 class="row__t"><a href="news/{n['slug']}.html">{E(n['title'])}</a></h3><p class="row__d">{E(n['summary'])}</p></div>
</article>""" for n in sorted(NEWS, key=lambda n: n["date"], reverse=True)
)
body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>News &amp; Events</h1></div>
    <div class="lede__aside"><p>Interviews with makers, exhibitions, competition results and other news from the network.</p></div>
  </div>
  <div class="rows">{rows}</div>
</div>"""
write("news.html", page("News & Events — K-Lutherie", "Interviews, exhibitions and news about Korean makers.", body, "news.html"))

by_slug = {m["slug"]: m for m in makers}
for n in NEWS:
    paras = "".join(f"<p>{E(p)}</p>" for p in n["body"])
    related = ", ".join(f'<a href="../makers/{s}.html">{E(by_slug[s]["name"])}</a>' for s in n["makers"] if s in by_slug)
    sources = ", ".join(f'<a href="{u}">{E(t)}</a>' for t, u in n.get("sources", []))
    body = f"""<div class="wrap">
  <article class="article">
    <span class="label">{E(n['date_text'])}</span>
    <h1>{E(n['title'])}</h1>
    <p class="article__summary">{E(n['summary'])}</p>
    <div class="article__body">{paras}</div>
    <div class="article__links">
      {f'<p>Makers: {related}</p>' if related else ''}
      {f'<p>Sources: {sources}</p>' if sources else ''}
    </div>
  </article>
</div>"""
    write(f"news/{n['slug']}.html", page(f"{n['title']} — K-Lutherie", n["summary"], body, "news.html", depth=1))

# ---------- join ----------
def chk(name, opts):
    return '<div class="choices">' + "".join(f'<label><input type="checkbox" name="{name}" value="{E(o)}"> {E(o)}</label>' for o in opts) + '</div>'
def rad(name, opts):
    return '<div class="choices">' + "".join(f'<label><input type="radio" name="{name}" value="{E(o)}"> {E(o)}</label>' for o in opts) + '</div>'

body = f"""<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>Join the register</h1></div>
    <div class="lede__aside"><p>For makers and restorers of Korean origin, anywhere in the world. Listing is free. We write every biography in one voice from what you send, and nothing goes online before you have seen it.</p></div>
  </div>

  <form class="form" id="joinform" action="{FORM_ENDPOINT}" method="POST" enctype="multipart/form-data">
    <input type="hidden" name="_subject" value="K-Lutherie application">
    <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">

    <fieldset>
      <legend>Who you are</legend>
      <div class="field"><label for="name">Name in English <small>(as you would like it shown)</small></label><input type="text" id="name" name="name" required></div>
      <div class="field"><label for="name_ko">Name in Korean <small>(optional)</small></label><input type="text" id="name_ko" name="name_korean"></div>
      <div class="field"><label>Korean connection</label>{chk('korean_connection', ['Born in Korea', 'Korean descent', 'Trained in Korea'])}</div>
      <div class="field"><label for="born">Place and year of birth <small>(optional)</small></label><input type="text" id="born" name="born" placeholder="Incheon, 1990"></div>
    </fieldset>

    <fieldset>
      <legend>Where you work</legend>
      <div class="field"><label for="city">City and country</label><input type="text" id="city" name="city" required placeholder="Cremona, Italy"></div>
      <div class="field"><label for="workshop">Workshop or employer</label><input type="text" id="workshop" name="workshop" placeholder="Own workshop, Via Magenta 48 / Head restorer at …"></div>
    </fieldset>

    <fieldset>
      <legend>What you do</legend>
      <div class="field"><label>Kind of work</label>{rad('work_type', ['Making', 'Repair and restoration', 'Both'])}</div>
      <div class="field"><label>Instruments</label>{chk('instruments', ['Violin', 'Viola', 'Cello', 'Double bass', 'Bows', 'Guitar', 'Other'])}</div>
      <div class="field"><label for="instruments_other">If other, or anything to add</label><input type="text" id="instruments_other" name="instruments_other"></div>
    </fieldset>

    <fieldset>
      <legend>Your background</legend>
      <div class="field"><label for="training">Training <small>(schools, teachers, years)</small></label><textarea id="training" name="training" placeholder="Istituto Stradivari, Cremona, 2011–2015, under …"></textarea></div>
      <div class="field"><label for="awards">Competition awards and recognition <small>(year, competition, category, result)</small></label><textarea id="awards" name="awards" placeholder="2024 — Cremona Triennale — cello — Gold Medal"></textarea></div>
      <div class="field"><label for="bio">Short biography <small>(in your own words; we will edit it to the site’s style and send it back to you)</small></label><textarea id="bio" name="biography" required style="min-height:180px"></textarea></div>
      <div class="field"><label for="dealers">Dealers who carry your work <small>(shop name and city)</small></label><textarea id="dealers" name="dealers" placeholder="LA Violin Shop, Los Angeles"></textarea></div>
    </fieldset>

    <fieldset>
      <legend>Links and contact</legend>
      <div class="field"><label for="instagram">Instagram</label><input type="text" id="instagram" name="instagram" placeholder="@yourhandle"></div>
      <div class="field"><label for="website">Website <small>(optional)</small></label><input type="url" id="website" name="website" placeholder="https://"></div>
      <div class="field"><label for="email">Email</label><input type="email" id="email" name="email" required></div>
      <div class="field"><label for="phone">Phone <small>(optional, with country code)</small></label><input type="tel" id="phone" name="phone"></div>
    </fieldset>

    <fieldset>
      <legend>Photograph</legend>
      <div class="field">
        <label for="photo">A photograph of you, ideally at the bench</label>
        <input type="file" id="photo" name="photo" accept="image/jpeg,image/png">
        <p class="hint">JPG or PNG, at least 2000 pixels on the long side if you have it. Portrait orientation works best. If the file is too large to attach, send it separately to owensparkley@gmail.com.</p>
      </div>
      <div class="field"><div class="choices"><label><input type="checkbox" name="photo_rights" value="yes" required> I own this photograph, or have the photographer’s permission, and it may be published on klutherie.com with the credit “Photograph courtesy of the maker”.</label></div></div>
    </fieldset>

    <fieldset>
      <legend>Anything else</legend>
      <div class="field"><label for="notes">Notes <small>(exhibitions you take part in, instruments played by notable musicians, anything we should know)</small></label><textarea id="notes" name="notes"></textarea></div>
    </fieldset>

    <button class="btn btn--solid btn--lg" type="submit" id="submitbtn">Send application</button>
    <p class="form__note">Your application goes to Owen Hojoon Lee at owensparkley@gmail.com. We reply within a week with a draft of your page for approval.</p>
    <p class="form__status" id="formstatus" hidden></p>
  </form>
</div>"""
write("join.html", page("Join — K-Lutherie", "Apply to be listed on K-Lutherie: makers and restorers of Korean origin, anywhere in the world.", body, "join.html"))

# ---------- about ----------
body = """<div class="wrap">
  <div class="lede">
    <div class="lede__text"><h1>About</h1></div>
  </div>
  <div class="prose">
    <p class="lead">K-Lutherie is a register of makers of stringed instruments and bows who are Korean by birth or descent, wherever in the world they work.</p>
    <p>The name borrows from K-pop and K-food. <em>Lutherie</em> is the craft of making and restoring stringed instruments, and here it covers luthiers and archetiers alike. Korean makers trained in Cremona, Mittenwald, Chicago, Salt Lake City and Seoul now work across Europe, Asia and North America. Their instruments win medals at the Cremona Triennale, the VSA and Mittenwald, and in 2025 a Korean maker sat on the jury of the Wieniawski competition for the first time. Until now there has been no one place to see this work together.</p>
  </div>

  <section class="split">
    <span class="label">What is listed</span>
    <div class="split__body">
      <p>Each maker has a page with a photograph, a short biography, the city they work in, the kind of work they do, and the dealers who carry their instruments. Dealer listings are standing relationships rather than current stock. Biographies are written in one voice from material the makers supply, and are kept to the facts: training, workshop, recognition.</p>
    </div>
  </section>

  <section class="split" id="listing">
    <span class="label">Being listed</span>
    <div class="split__body">
      <p>Makers of Korean origin who make or restore stringed instruments or bows are welcome to be listed, at no cost. <a href="join.html" style="text-decoration:underline;text-underline-offset:4px">Use the application form</a>, or write to owensparkley@gmail.com with a photograph of yourself at work, a short biography, your city, what you make, and the dealers who carry your work.</p>
      <p>Dealers who carry a listed maker, or a maker not yet listed, can write to the same address.</p>
    </div>
  </section>

  <section class="split">
    <span class="label">Who runs it</span>
    <div class="split__body">
      <p>K-Lutherie was started in 2026 by Owen Hojoon Lee, who has worked in the violin trade in Los Angeles since 2002 and is the founder of LA Violin Shop. It is an independent project with no commercial purpose: makers are listed on their merits, and dealers are listed on the same terms whoever they are.</p>
    </div>
  </section>

  <section class="split">
    <span class="label">Follow</span>
    <div class="split__body">
      <p><a href="https://www.instagram.com/klutherie">Instagram @klutherie</a><br><a href="https://www.facebook.com/klutherie.official">Facebook /klutherie.official</a></p>
    </div>
  </section>
</div>"""
write("about.html", page("About — K-Lutherie", "What K-Lutherie is, who runs it, and how makers and dealers are listed.", body, "about.html"))

print(f"built: index, makers, {len(makers)} maker pages, dealers, news, {len(NEWS)} articles, about")
