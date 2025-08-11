import React, { useState } from "react";
import LogInForm from "../components/Auth/LoginForm";
import SignUpForm from "../components/Auth/SignUpForm";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../context/UserContext";
const AuthPage: React.FC = () => {
  const [selected, setSelected] = useState<"login" | "signup">("login"); // declare the default state as string
  const { user } = useUser();
  const navigate = useNavigate();

  useEffect(() => {
    if (!user) {
      console.log("No user found, stay on auth page");
    }
  }, [navigate]);

  return (
    <div className="mt-5">
      {selected === "login" ? <LogInForm /> : <SignUpForm />}
      {/* the selection options for sorting options */}
      <div className="mb-4 flex justify-center space-x-4">
        {selected === "login" ? (
          <>
            <p>Don't have an account yet?</p>
            <p className="text-blue-600" onClick={() => setSelected("signup")}>
              Sign Up
            </p>
          </>
        ) : (
          <>
            <p>Already have an account?</p>
            <p className="text-blue-600" onClick={() => setSelected("login")}>
              Log In
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthPage;
