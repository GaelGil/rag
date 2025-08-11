// components/PrivateRoute.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useUser } from "../context/UserContext";
const PrivateRoute = () => {
  const { user, loading } = useUser(); // get user from context and loading
  if (loading) return null; // if loading return null

  return user ? <Outlet /> : <Navigate to="/login" />; // if user is logged in return outlet
};

export default PrivateRoute;
