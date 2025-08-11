export type AuthFormProps = {
  value: string; // each option gets its own input value
  username: string;
  password: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
};
