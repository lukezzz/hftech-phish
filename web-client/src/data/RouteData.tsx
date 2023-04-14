import {
    HomeOutlined,
} from "@ant-design/icons";

export interface ISiteItem {
    exact?: boolean;
    icon: JSX.Element | string;
    locale: string;
    name: string;
    path: string;
    hideInMenu?: boolean;
    hideChildrenInMenu?: boolean;
    breadcrumbName?: string
    // sub menu
    routes?: ISiteRoute["routes"];
}

export interface ISiteRoute {
    path: string;
    routes: Array<ISiteItem>;
}


const siteRoutes: ISiteRoute = {
    path: "/",
    routes: [
        {
            name: "Home",
            icon: <HomeOutlined />,
            locale: "menu.Home",
            path: "/home",
            hideInMenu: false,
        },
    ],
};

export default siteRoutes;
