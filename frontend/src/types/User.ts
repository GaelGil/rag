// movie type for declaring var types
export type User = {
  id: string;
  username: string;
  email: string;
  pfp: string;
};

// moviecardProps type for declaring var types
export type UserProps = {
  user: User;
};

export interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
}
