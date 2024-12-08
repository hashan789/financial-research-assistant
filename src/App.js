import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import GetStarted from './components/GetStarted';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Homepage from './components/Homepage';
import Login from './components/Login';
import Signup from './components/Signup';

function App() {

  const user = localStorage.getItem("token");

  return (
    <BrowserRouter>
    <Routes>
      <Route path="/">
        <Route index element={ user ? <Homepage /> : <GetStarted />}/>
        <Route path="homepage" element={<Homepage />} />
        <Route path="login" element={<Login />} />
        <Route path="signup" element={<Signup />} />
      </Route>
    </Routes>
  </BrowserRouter>

  );
}

export default App;
