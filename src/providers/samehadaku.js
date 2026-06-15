const BASE = 'https://v2.samehadaku.how';

async function fetchHTML(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  return res.text();
}

function clean(html = '') {
  return html.replace(/<[^>]+>/g, '').trim();
}

async function getLatestAnime(page = 1) {
  const html = await fetchHTML(`${BASE}/page/${page}/`);

  const results = [...html.matchAll(/<article[\s\S]*?<\/article>/gi)]
    .map(m => {
      const c = m[0];

      const title = clean(c.match(/title[^>]*>(.*?)<\/a>/i)?.[1] || '');
      const slug = c.match(/href="[^"]*\/([^/"]+)\/?"/)?.[1];
      const img = c.match(/<img[^>]+src="([^"]+)"/)?.[1];

      if (!title || !slug) return null;

      return { title, slug, img };
    })
    .filter(Boolean);

  return { results };
}

async function searchAnime(q = '') {
  if (!q) return { results: [] };

  const html = await fetchHTML(`${BASE}/?s=${encodeURIComponent(q)}`);

  const results = [...html.matchAll(/<article[\s\S]*?<\/article>/gi)]
    .map(m => {
      const c = m[0];

      const title = clean(c.match(/<h2[^>]*>(.*?)<\/h2>/i)?.[1] || '');
      const slug = c.match(/href="[^"]*\/([^/"]+)\/?"/)?.[1];

      if (!title || !slug) return null;

      return { title, slug };
    })
    .filter(Boolean);

  return { results };
}

async function getAnimeDetail(slug) {
  const html = await fetchHTML(`${BASE}/anime/${slug}/`);

  return {
    title: clean(html.match(/<h1[^>]*>(.*?)<\/h1>/i)?.[1] || ''),
    genres: [...html.matchAll(/genre[^>]*>([^<]+)<\/a>/gi)].map(m => m[1]),
  };
}

async function getEpisodeDetail(slug) {
  const html = await fetchHTML(`${BASE}/episode/${slug}/`);

  const iframe = html.match(/<iframe[^>]+src="([^"]+)"/i)?.[1];

  return {
    stream: iframe || null
  };
}

module.exports = {
  getLatestAnime,
  searchAnime,
  getAnimeDetail,
  getEpisodeDetail,
};
