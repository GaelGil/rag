export type AuthFormProps = {
  isLogin: boolean;
  username: string;
  password: string;
  email?: string; // optional for login
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
};
