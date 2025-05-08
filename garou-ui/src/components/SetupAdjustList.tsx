import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Combo {
  recipe: string;
  advantage: number;
}

interface Move {
  name: string;
  total: number | null;
}

const jpMap: Record<string, string> = {
  DongHwan: 'ドンファン',
  Rock: 'ロック',
  Terry: 'テリー',
  Hotaru: 'ほたる',
  Marco: 'マルコ',
  Jenet: 'ジェニー',
  Hokutomaru: '北斗丸',
  CR7: 'クリスティアーノ・ロナウド',
  Preacher: 'プリチャ',
  Salvatore: 'サルヴぁトーレ・ガナッチ'
};

const SetupAdjustList: React.FC = () => {
  const [characters, setCharacters] = useState<string[]>([]);
  const [charEng, setCharEng] = useState<string>('DongHwan');
  const [combos, setCombos] = useState<Combo[]>([]);
  const [moves, setMoves] = useState<Move[]>([]);

  // キャラ一覧を取得
  useEffect(() => {
    axios.get('http://localhost:3001/api/characters')
      .then((res) => setCharacters(res.data))
      .catch((err) => console.error('キャラ取得失敗:', err));
  }, []);

  // コンボ & 技一覧を取得
  useEffect(() => {
    if (!charEng) return;

    axios.get(`http://localhost:3001/api/combos/${charEng}`)
      .then((res) => setCombos(res.data))
      .catch((err) => console.error('コンボ取得失敗:', err));

    axios.get(`http://localhost:3001/api/frames/${charEng}`)
      .then((res) => setMoves(res.data))
      .catch((err) => console.error('技データ取得失敗:', err));
  }, [charEng]);

  // 指定Fに合う技を探す
  const findMoves = (target: number) => {
    return moves
      .filter((m) => m.total === target)
      .map((m) => `・${m.name}（${m.total}F）`);
  };

  return (
    <div style={{ marginTop: '2rem' }}>
      <h2>詐欺重ね調整リスト（+34F / +41F）</h2>

      <div style={{ marginBottom: '1rem' }}>
        <label>自キャラ選択: </label>
        <select value={charEng} onChange={(e) => setCharEng(e.target.value)}>
          {characters.map((char) => (
            <option key={char} value={char}>
              {jpMap[char] || char}
            </option>
          ))}
        </select>
      </div>

      {combos.map((combo, idx) => {
        const adjust34 = findMoves(combo.advantage - 34);
        const adjust41 = findMoves(combo.advantage - 41);

        return (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              border: '1px solid #ccc',
              padding: '1rem',
              marginBottom: '1rem'
            }}
          >
            <div style={{ flex: 1, paddingRight: '1rem' }}>
              <h4>{combo.recipe}（+{combo.advantage}F）→ 小ジャンプ（+34F）</h4>
              <ul>
                {adjust34.length > 0 ? adjust34.map((line, i) => <li key={i}>{line}</li>) : <li>該当なし</li>}
              </ul>
            </div>
            <div style={{ flex: 1 }}>
              <h4>{combo.recipe}（+{combo.advantage}F）→ ジャンプ（+41F）</h4>
              <ul>
                {adjust41.length > 0 ? adjust41.map((line, i) => <li key={i}>{line}</li>) : <li>該当なし</li>}
              </ul>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default SetupAdjustList;
