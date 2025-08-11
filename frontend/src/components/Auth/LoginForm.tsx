import React, { useState } from "react";
import { Container } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import AuthForm from "./AuthForm";
import { login } from "../../api/auth";
import { useUser } from "../../context/UserContext";

const LogInForm = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState<boolean>(true);
  const { setUser } = useUser();
  const navigate = useNavigate();

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    e.preventDefault();
    const { name, value } = e.target;
    switch (name) {
      case "username":
        setUsername(value);
        break;
      case "password":
        setPassword(value);
        break;
      default:
        break;
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setMessage("Logging in...");
    try {
      const data = await login(username, password);

      if (!data.user) {
        setMessage("Login failed: user not returned");
        return;
      }
      setUser(data.user);
      navigate(`/profile/${data.user.id}`);
    } catch (error) {
      console.error("Login Error", error);
      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Error Logging in");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="d-flex flex-column justify-content-center align-items-center">
      <div>
        <h1>Log In</h1>
        <AuthForm
          isLogin={true}
          username={username}
          password={password}
          onChange={handleChange}
          onSubmit={handleSubmit}
        />
        {message && <p className="text-danger">{message}</p>}
      </div>
    </Container>
  );
};

export default LogInForm;
