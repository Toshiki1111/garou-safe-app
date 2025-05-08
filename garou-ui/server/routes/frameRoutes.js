const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./db/frame_data.db');

// GET /api/frames/:character → 技データ（name + total）
router.get('/:character', (req, res) => {
  const char = req.params.character;
  const query = `
    SELECT name, total
    FROM frame_data
    WHERE character = ?
  `;
  db.all(query, [char], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });

    const cleaned = rows
      .filter(r => r.total !== null && r.total !== "//")
      .map(r => ({
        name: r.name,
        total: parseInt(r.total)
      }))
      .filter(r => !isNaN(r.total));

    res.json(cleaned);
  });
});

// GET /api/frames/characters → キャラ一覧（英語名のみ）
router.get('/characters', (req, res) => {
  const sql = `
    SELECT DISTINCT character
    FROM frame_data
    ORDER BY character
  `;
  db.all(sql, [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows.map(r => r.character));
  });
});

module.exports = router;
