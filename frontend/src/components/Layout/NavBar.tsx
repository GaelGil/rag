import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import { PROJECT_NAME } from "../../data/ProjectName";
import { PROJECT_LOGO } from "../../data/ProjectLogo";
import { useUser } from "../../context/UserContext";
import { logout } from "../../api/auth";
const Navigation = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>();
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  const { user, setUser } = useUser();

  const handleLogout = async () => {
    localStorage.removeItem("token");
    try {
      setLoading(true);
      await logout();
      setUser(null);
    } catch (error) {
      alert(`error logging out: ${error}`);
    } finally {
      setLoading(false);
    }
    console.log(loading);
    navigate("/login");
  };

  return (
    <nav className="bg-white shadow-sm py-1">
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2">
          <img
            src={PROJECT_LOGO}
            alt="Logo"
            className="w-24 h-12 object-contain"
          />
          <span className="font-bold text-xl text-gray-800 no-underline">
            {PROJECT_NAME}
          </span>
        </Link>

        {/* Mobile menu toggle */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-black focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
        >
          <svg
            className="h-6 w-6"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {isOpen ? (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            ) : (
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 8h16M4 16h16"
              />
            )}
          </svg>
        </button>

        {/* Desktop nav */}
        <div className="hidden md:flex md:items-center space-x-6 font-semibold text-lg">
          {!user ? (
            <Link
              to="/login"
              className={`no-underline ${
                location.pathname === "/login"
                  ? "text-blue-600"
                  : "text-gray-700 hover:text-blue-600"
              }`}
            >
              Content
            </Link>
          ) : (
            <Link
              to="/content"
              className={`no-underline${
                location.pathname === "/content"
                  ? "text-blue-600 no-underline"
                  : "text-gray-700 hover:text-blue-600 no-underline"
              }`}
            >
              Content
            </Link>
          )}

          {!user ? (
            <Link
              to="/login"
              className={`no-underline ${
                location.pathname === "/login"
                  ? "text-blue-600"
                  : "text-gray-700 hover:text-blue-600"
              }`}
            >
              Log In
            </Link>
          ) : (
            <Link
              onClick={handleLogout}
              to="/"
              className={`no-underline ${
                location.pathname === "/login"
                  ? "text-blue-600"
                  : "text-gray-700 hover:text-blue-600"
              }`}
            >
              Log Out
            </Link>
          )}
        </div>
      </div>

      {/* Mobile nav */}
      {isOpen && (
        <div className="md:hidden px-4 pb-4 space-y-2 font-semibold text-lg">
          <Link
            to="/orders"
            onClick={() => setIsOpen(false)}
            className={`block ${
              location.pathname === "/orders"
                ? "text-blue-600"
                : "text-gray-700 hover:text-blue-600"
            }`}
          >
            Orders
          </Link>
        </div>
      )}
    </nav>
  );
};

export default Navigation;
