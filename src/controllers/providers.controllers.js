const { getProvider } = require('../providers');

exports.latest = async (req, res) => {
  const p = getProvider(req.params.provider);
  if (!p) return res.status(404).json({ error: 'Provider not found' });

  const data = await p.getLatestAnime(req.query.page || 1);
  res.json(data);
};

exports.search = async (req, res) => {
  const p = getProvider(req.params.provider);
  if (!p) return res.status(404).json({ error: 'Provider not found' });

  const data = await p.searchAnime(req.query.q || '');
  res.json(data);
};

exports.detail = async (req, res) => {
  const p = getProvider(req.params.provider);
  if (!p) return res.status(404).json({ error: 'Provider not found' });

  const data = await p.getAnimeDetail(req.params.slug);
  res.json(data);
};

exports.episode = async (req, res) => {
  const p = getProvider(req.params.provider);
  if (!p) return res.status(404).json({ error: 'Provider not found' });

  const data = await p.getEpisodeDetail(req.params.slug);
  res.json(data);
};
