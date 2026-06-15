const samehadaku = require('./samehadaku');
const otakudesu = require('./otakudesu');

const providers = {
  samehadaku,
  otakudesu,
};

function getProvider(name) {
  return providers[name] || null;
}

module.exports = { getProvider };
