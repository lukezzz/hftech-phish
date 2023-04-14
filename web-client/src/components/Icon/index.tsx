import Icon from '@ant-design/icons';


export const LogoSvg = ({ width, height }: { width: number, height: number }) => (
    <svg version="1.1" viewBox="0 0 48 48" width={width} height={height}>
        <g>
            <ellipse cx="5.58" cy="5.58" rx="5.58333333333332" ry="5.58333333333332" fill="#ae3c60" stroke="none" pointerEvents="none" />
            <ellipse cx="23.763" cy="5.58" rx="5.58333333333332" ry="5.58333333333332" fill="#df473c" stroke="none" pointerEvents="none" />
            <ellipse cx="41.9" cy="5.58" rx="5.58333333333332" ry="5.58333333333332" fill="#f15b4c" stroke="none" pointerEvents="none" />
            <ellipse cx="5.58" cy="20.97" rx="5.58333333333332" ry="5.58333333333332" fill="#faa41b" stroke="none" pointerEvents="none" />
            <ellipse cx="23.763" cy="20.97" rx="5.58333333333332" ry="5.58333333333332" fill="#ffd45b" stroke="none" pointerEvents="none" />
            <ellipse cx="41.9" cy="20.97" rx="5.58333333333332" ry="5.58333333333332" fill="#255e79" stroke="none" pointerEvents="none" />
            <ellipse cx="5.58" cy="36.34" rx="5.58333333333332" ry="5.58333333333332" fill="#26778" stroke="none" pointerEvents="none" />
            <ellipse cx="23.763" cy="36.34" rx="5.58333333333332" ry="5.58333333333332" fill="#82b4bb" stroke="none" pointerEvents="none" />
            <ellipse cx="41.9" cy="36.34" rx="5.58333333333332" ry="5.58333333333332" fill="#1ba1e2" stroke="none" pointerEvents="none" />
        </g>
    </svg>
)

export const LogoIcon = (props: any) => <Icon component={LogoSvg} {...props} />;

