
import '../styles/globals.css';
// import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
// import LoginPage from "./LoginPage";
// import SymptomsPage from "./SymptomsPage";

function MyApp({ Component, pageProps }) {
  return (
    <>
      
      <Component {...pageProps} />
    </>
  //   <Router>
  //   <Routes>
  //     <Route path="/login" element={<LoginPage />} />
  //     <Route path="/symptoms" element={<SymptomsPage />} />
  //   </Routes>
  // </Router>
  );
}

export default MyApp;
