import { Link, useLocation } from 'react-router-dom';

export default function Sidebar() {
  const location = useLocation();

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">GSD Ollama</h1>
        <p className="text-sm text-gray-400">Get Shit Done</p>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          <li>
            <Link
              to="/"
              className={`block px-4 py-2 rounded ${
                location.pathname === '/' ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`}
            >
              Projects
            </Link>
          </li>
          <li>
            <Link
              to="/projects/new"
              className={`block px-4 py-2 rounded ${
                location.pathname === '/projects/new' ? 'bg-gray-700' : 'hover:bg-gray-700'
              }`}
            >
              New Project
            </Link>
          </li>
        </ul>
      </nav>
    </div>
  );
}
