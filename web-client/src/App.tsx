import { FC, useContext } from 'react';
// import PageLoading from "./components/PageLoading";
import { ConfigProvider, theme as antdTheme } from 'antd';
import { SettingsContext } from '@/providers/Settings.provider'
import ErrorBoundary from "./components/Error";
import { Home } from './pages';
import { Route, Routes, Navigate } from 'react-router-dom';
import { App as AntdApp } from "antd";
import { ThemeProvider } from 'antd-style';

const App: FC = () => {

  const { token, componentsToken, themeName } = useContext(SettingsContext)

  return (
    <ConfigProvider
      theme={{
        algorithm: themeName === "dark" ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
        token: token,
        components: componentsToken
      }}
    >
      <ThemeProvider>
        <ErrorBoundary>
          <AntdApp>
            <Routes>
              <Route path="*" element={<Home />} />
            </Routes>
          </AntdApp>
        </ErrorBoundary>
      </ThemeProvider>
    </ConfigProvider>
  )
}

export default App;