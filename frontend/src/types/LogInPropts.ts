export type AuthFormProps = {
  value: string;
  username: string;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
};
