import { useSelector } from "react-redux";
import { Redirect, Route } from "react-router-dom";
import {
  hasModulePermission,
  getAuthHeader,
  getRolePermissions,
  logout,
} from "../helpers/Authorization";

// Different role has different home page
const RoleHomePage = {
  executive: "/dashboard",
  operator: "/dashboard",
  manager: "/dashboard",
  admin: "/dashboard",
};

const PrivateRoute = ({ component: Component, module, ...rest }) => {
  const { initDataLoaded } = useSelector((state) => state.apiCallData);
  const isAuthenticated = !!getAuthHeader();

  return (
    <Route
      {...rest}
      render={(props) => {

        if (!isAuthenticated) {
          // not logged in so redirect to login page with the return url
          logout();
          return <Redirect to="/login" />;
        }

        if (!initDataLoaded) {
          return (
            <div style={{
              padding: '50px',
              textAlign: 'center',
              backgroundColor: '#f0f0f0',
              height: '100vh',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column'
            }}>
              <h1 style={{ color: '#333' }}>Carregando dados iniciais...</h1>
              <p style={{ color: '#666' }}>Aguardando o estado inicial ser preenchido (initDataLoaded).</p>
            </div>
          );
        }

        if (!hasModulePermission(module)) {
          // role not authorised so redirect to role's home page
          return <Redirect to={{ pathname: RoleHomePage[getRolePermissions().role] }} />;
        }

        return <Component {...props} />;
      }}
    />
  );
};

export default PrivateRoute;