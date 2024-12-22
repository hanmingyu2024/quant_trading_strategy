import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import EmailMonitor from './components/admin/EmailMonitor';

function App() {
    return (
        <Router>
            <Routes>
                {/* 其他路由 */}
                <Route path="/admin/email-monitor" element={<EmailMonitor />} />
            </Routes>
        </Router>
    );
}

export default App; 