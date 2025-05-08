import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Combo {
  recipe: string;
  advantage: number;
}

const ComboList: React.FC = () => {
  const [combos, setCombos] = useState<Combo[]>([]);
  const [character, setCharacter] = useState<string>('DongHwan'); // 一旦固定。後でpropsにします

  useEffect(() => {
    axios
      .get(`http://localhost:3001/api/combos/${character}`)
      .then((res) => {
        setCombos(res.data);
      })
      .catch((err) => {
        console.error('コンボ取得失敗:', err);
      });
  }, [character]);

  return (
    <div>
      <h2>登録済みコンボ（{character}）</h2>
      {combos.length === 0 ? (
        <p>データがありません</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>レシピ</th>
              <th>有利F</th>
            </tr>
          </thead>
          <tbody>
            {combos.map((combo, index) => (
              <tr key={index}>
                <td>{combo.recipe}</td>
                <td>{combo.advantage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ComboList;
