
import classNames from 'classnames'
import './style.css'

interface IProps {
    spinning: boolean,
    fullScreen?: boolean
}

const Loader: React.FC<IProps> = ({ spinning, fullScreen = true }) => {

    return (
        <div
            className={classNames("loader", {
                ["hidden"]: !spinning,
                ["fullScreen"]: fullScreen,
            })}
        // className={`loader ${!spinning ? "hidden" : ""} ${fullScreen? "fullScreen": ""}`}
        >
            <div className={"warpper"}>
                <div className={"inner"} />
                <div className={"text"}>加载中...</div>
            </div>
        </div>
    )
}

export default Loader