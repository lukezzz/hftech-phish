import { Row, Col, Typography } from 'antd'

const { Title } = Typography;


export const Home = () => {


    return (
        <Row justify="center" gutter={[24, 24]}>
            <Col span={24} style={{
                textAlign: "center",
            }}>

            </Col>
            <div style={{
                zIndex: 10,
                pointerEvents: 'none',
                position: 'absolute',
                top: -250,
                left: "50%",
                transform: "translateX(-50%) scale(1.5)",
                width: 600,
                height: 400,
                opacity: 0.2,
                filter: "blur(69px)",
                willChange: "transform",
                background: "linear-gradient( 135deg, #722ED1 0%, #1677ff 30%, #F5222D 70%, #13C2C2 100% )",
                backgroundSize: "200% 200%",
                animation: "gradient 10s ease infinite",
            }}></div>
        </Row>
    );
};