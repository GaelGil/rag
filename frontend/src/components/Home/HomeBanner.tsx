import { Link } from "react-router-dom";
import { PROJECT_NAME } from "../../data/ProjectName";
import { PROJECT_LOGO } from "../../data/ProjectLogo";
const HomeBanner = () => {
  const token = localStorage.getItem("token");
  return (
    <>
      <div className="min-h-[80vh] flex items-center justify-center bg-gradient-to-r from-[#e3f0ff] to-[#f8fafd]">
        <div className="max-w-7xl mx-auto px-4 w-full">
          <div className="flex flex-col-reverse md:flex-row items-center">
            {/* Left content */}
            <div className="w-full md:w-1/2 text-left">
              <h1 className="font-extrabold text-4xl md:text-5xl mb-6 text-[#1a237e]">
                {PROJECT_NAME}
              </h1>
              <p className="text-lg md:text-xl text-gray-700 mb-8">
                Lorem ipsum, dolor sit amet consectetur adipisicing elit.
                Itaque, quaerat minima ducimus doloribus dolore, inventore
                impedit iste maxime temporibus earum beatae tenetur quisquam
                enim reprehenderit rem necessitatibus eaque omnis deserunt.
              </p>

              {!token ? (
                <Link
                  to="/login"
                  className={`no-underline ${
                    location.pathname === "/login"
                      ? "text-blue-600"
                      : "text-gray-700 hover:text-blue-600"
                  }`}
                >
                  <button className="px-10 py-4 text-lg font-bold rounded-lg bg-[#1976d2] text-white border-none shadow-md hover:shadow-lg transition">
                    View Content
                  </button>
                </Link>
              ) : (
                <Link
                  to="/content"
                  className={` no-underline${
                    location.pathname === "/content"
                      ? "text-blue-600"
                      : "text-gray-700 hover:text-blue-600"
                  }`}
                >
                  <button className="px-10 py-4 text-lg font-bold rounded-lg bg-[#1976d2] text-white border-none shadow-md hover:shadow-lg transition">
                    View Content
                  </button>
                </Link>
              )}
            </div>

            {/* Right image */}
            <div className="w-full md:w-1/2 text-center mb-10 md:mb-0">
              <img
                src={PROJECT_LOGO}
                alt="Order Agent"
                className="w-80 max-w-[90%] mx-auto rounded-3xl shadow-[0_4px_24px_rgba(25,118,210,0.10)]"
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default HomeBanner;
