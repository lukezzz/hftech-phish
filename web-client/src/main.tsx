import ReactDOM from 'react-dom/client'
import App from './App'

import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import { Provider } from "react-redux";
import { store, persistor } from "./redux/store";
import { PersistGate } from 'redux-persist/integration/react';
import SettingsProvider from '@/providers/Settings.provider';
import { LoadingOutlined } from '@ant-design/icons';
import { Spin } from 'antd';


const router = createBrowserRouter([
  {
    path: "*",
    element: <App />,
  },
]);


const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;
Spin.setDefaultIndicator(antIcon)

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <Provider store={store}>
    <PersistGate loading={null} persistor={persistor}>
      <SettingsProvider>
        <RouterProvider router={router} />
      </SettingsProvider>
    </PersistGate>
  </Provider>
)
