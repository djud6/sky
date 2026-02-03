import {useDispatch, useSelector} from "react-redux";

const useUserInfo = () => {
    const {userInfo} = useSelector((state) => state.apiCallData);
    return userInfo;
}

export {useUserInfo};