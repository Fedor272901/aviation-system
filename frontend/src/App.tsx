import { Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Persons } from './pages/Persons';
import { Flights } from './pages/Flights';

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/persons" element={<Persons />} />
        <Route path="/flights" element={<Flights />} />
      </Route>
    </Routes>
  );
}

export default App;