import React, { useState } from 'react';
import axios from 'axios';

const ComboRegisterForm: React.FC = () => {
  const [character, setCharacter] = useState('DongHwan'); // 固定。後で props 予定
  const [recipe, setRecipe] = useState('');
  const [advantage, setAdvantage] = useState<number>(0);
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    axios
      .post('http://localhost:3001/api/combos', {
        character,
        recipe,
        advantage
      })
      .then((res) => {
        setMessage('✅ 登録成功！');
        setRecipe('');
        setAdvantage(0);
      })
      .catch((err) => {
        console.error(err);
        setMessage('❌ 登録失敗');
      });
  };

  return (
    <div>
      <h2>コンボ登録</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>キャラ名: </label>
          <input value={character} onChange={(e) => setCharacter(e.target.value)} />
        </div>
        <div>
          <label>コンボレシピ: </label>
          <input value={recipe} onChange={(e) => setRecipe(e.target.value)} required />
        </div>
        <div>
          <label>有利F: </label>
          <input
            type="number"
            value={advantage}
            onChange={(e) => setAdvantage(Number(e.target.value))}
            required
          />
        </div>
        <button type="submit">登録</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default ComboRegisterForm;
