// import { Form } from "react-bootstrap";
import type { AuthFormProps } from "../../types/AuthFormProp.ts";

const AuthForm: React.FC<AuthFormProps> = ({
  isLogin,
  username,
  password,
  email,
  onChange,
  onSubmit,
}) => (
  <form
    onSubmit={onSubmit}
    className="p-6 border rounded-lg bg-gray-100 shadow space-y-4 max-w-md mx-auto"
  >
    <label className="block font-semibold text-gray-700">Username</label>
    <input
      type="text"
      name="username"
      value={username}
      onChange={onChange}
      required
      className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />

    {!isLogin && (
      <>
        <label className="block font-semibold text-gray-700">Email</label>
        <input
          type="text"
          name="email"
          value={email}
          onChange={onChange}
          required
          className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </>
    )}

    <label className="block font-semibold text-gray-700">Password</label>
    <input
      type="text"
      name="password"
      value={password}
      onChange={onChange}
      required
      className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    />

    <button
      type="submit"
      className="w-full bg-blue-600 text-white font-semibold py-2 px-4 rounded-md hover:bg-blue-700 transition"
    >
      {isLogin ? "Login" : "Sign Up"}
    </button>
  </form>
);

export default AuthForm;
