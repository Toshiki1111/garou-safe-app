
import React from 'react';
import ComboRegisterForm from '../components/ComboRegisterForm';
import ComboList from '../components/ComboList';
import FrameTable from '../components/FrameTable';
import SetupAdjustList from '../components/SetupAdjustList';

const Home: React.FC = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>餓狼伝説 COTW フレーム＆コンボツール</h1>
      <ComboRegisterForm />
      <ComboList />
      <SetupAdjustList />
      <FrameTable />
    </div>
  );
};

export default Home;
