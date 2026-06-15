const BASE = 'https://otakudesu.cloud';

async function fetchHTML(url) {
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  return res.text();
}

function clean(html = '') {
  return html.replace(/<[^>]+>/g, '').trim();
}

async function getLatestAnime() {
  const html = await fetchHTML(BASE);

  const results = [...html.matchAll(/<h2[^>]*><a href="([^"]+)">([^<]+)<\/a><\/h2>/gi)]
    .map(m => ({
      title: clean(m[2]),
      slug: m[1].split('/').filter(Boolean).pop()
    }));

  return { results };
}

async function searchAnime(q = '') {
  const html = await fetchHTML(`${BASE}/?s=${encodeURIComponent(q)}`);

  const results = [...html.matchAll(/<h2[^>]*><a href="([^"]+)">([^<]+)<\/a><\/h2>/gi)]
    .map(m => ({
      title: clean(m[2]),
      slug: m[1].split('/').filter(Boolean).pop()
    }));

  return { results };
}

async function getAnimeDetail(slug) {
  const html = await fetchHTML(`${BASE}/anime/${slug}`);

  return {
    title: clean(html.match(/<h1[^>]*>(.*?)<\/h1>/i)?.[1] || '')
  };
}

async function getEpisodeDetail(slug) {
  const html = await fetchHTML(`${BASE}/episode/${slug}`);

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
