import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Common/Layout';
import ProjectList from './components/Project/ProjectList';
import ProjectView from './components/Project/ProjectView';
import NewProject from './components/Project/NewProject';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<ProjectList />} />
          <Route path="/projects/new" element={<NewProject />} />
          <Route path="/projects/:id" element={<ProjectView />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
