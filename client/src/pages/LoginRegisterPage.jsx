import { useState } from "react";
import FormLogin from "../components/FormLogin";
import FormRegister from "../components/FormRegister";

const LoginRegisterPage = () => {
  const [isLogin, setIsLogin] = useState(true);

  const handleToggle = () => {
    setIsLogin((prevState) => !prevState);
  };

  const title = isLogin ? "Login" : "Register";

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-6">
          <div className="card">
            <div className="card-body">
              <h1 className="card-title text-center">{title}</h1>
              {isLogin ? <FormLogin /> : <FormRegister />}
              <button 
                className="btn btn-primary btn-block mt-3" 
                onClick={handleToggle}
              >
                {isLogin ? "Need to Register?" : "Already Registered?"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginRegisterPage;
