// import { Link } from "react-router-dom";
import { PROJECT_NAME } from "../../data/ProjectName";
const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white text-center py-3">
      <div className="max-w-7xl mx-auto px-4">
        <p className="mb-0">© 2025 {PROJECT_NAME}. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
