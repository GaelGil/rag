import React, { createContext, useContext, useEffect, useState } from "react";
import { getCurrentUser } from "../api/auth";

// user context
const UserContext = createContext<any>(null);

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState(null); // user and setUser
  const [loading, setLoading] = useState(true); // for initial load

  // get current user on initial load
  useEffect(() => {
    getCurrentUser().then((user) => {
      setUser(user);
      setLoading(false);
    });
  }, []);

  // provider
  return (
    <UserContext.Provider value={{ user, setUser, loading }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
