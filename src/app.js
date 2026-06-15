const express = require('express');
const cors = require('cors');

const providerRoutes = require('./routes/provider.routes');

const app = express();

app.use(cors());
app.use(express.json());

app.use('/api/provider', providerRoutes);

app.get('/', (req, res) => {
  res.json({
    name: "Zentra API",
    status: "running",
    structure: "src clean architecture"
  });
});

module.exports = app;
