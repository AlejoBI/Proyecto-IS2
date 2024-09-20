import { useState } from "react";

import FormLogin from "../components/FormLogin";
import FormRegister from "../components/FormRegister";

const LoginRegisterPage = () => {
  const [isLogin, setIsLogin] = useState(true);

  const handleToggle = () => {
    setIsLogin((prevState) => !prevState);
  };

  const tittle = isLogin ? "Login" : "Register";

  return (
    <div className="container">
      <h1>{tittle}</h1>
      {isLogin ? <FormLogin /> : <FormRegister />}
      <button onClick={handleToggle}>
        {isLogin ? "Need to Register?" : "Already Registered?"}
      </button>
    </div>
  );
};

export default LoginRegisterPage;
