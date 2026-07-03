import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import Home from './pages/Home';
import Playground from './pages/Playground';
import Models from './pages/Models';
import Agents from './pages/Agents';
import Knowledge from './pages/Knowledge';
import Governance from './pages/Governance';
import Infrastructure from './pages/Infrastructure';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="playground" element={<Playground />} />
          <Route path="models" element={<Models />} />
          <Route path="agents" element={<Agents />} />
          <Route path="knowledge" element={<Knowledge />} />
          <Route path="governance" element={<Governance />} />
          <Route path="infrastructure" element={<Infrastructure />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
