const express = require('express');
const cors = require('cors');
const app = express();
const port = 3001;

const comboRoutes = require('./routes/comboRoutes');
const frameRoutes = require('./routes/frameRoutes');

app.use(cors());
app.use(express.json());

app.use('/api/combos', comboRoutes);
app.use('/api/frames', frameRoutes);

app.listen(port, () => {
  console.log(`✅ API server running at http://localhost:${port}`);
});
