const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./db/frame_data.db');

// GET /api/combos/:character → コンボ一覧取得
router.get('/:character', (req, res) => {
  const char = req.params.character;
  const sql = `
    SELECT recipe, advantage
    FROM combo_data
    WHERE character = ?
    ORDER BY advantage DESC
  `;
  db.all(sql, [char], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

// POST /api/combos → コンボ新規登録
router.post('/', (req, res) => {
  const { character, recipe, advantage } = req.body;
  const sql = `
    INSERT INTO combo_data (character, recipe, advantage)
    VALUES (?, ?, ?)
  `;
  db.run(sql, [character, recipe, advantage], function (err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ id: this.lastID });
  });
});

module.exports = router;
