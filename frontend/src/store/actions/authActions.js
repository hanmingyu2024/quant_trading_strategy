import { authService } from '../../services/auth';
import { loginFailure, loginStart, loginSuccess, logout } from '../reducers/authReducer';

export const login = (username, password) => async (dispatch) => {
    try {
        dispatch(loginStart());
        const data = await authService.login(username, password);
        localStorage.setItem('token', data.token);
        dispatch(loginSuccess(data.user));
    } catch (error) {
        dispatch(loginFailure(error.response?.data?.message || '登录失败'));
    }
};

export const getCurrentUser = () => async (dispatch) => {
    try {
        dispatch(loginStart());
        const user = await authService.getCurrentUser();
        dispatch(loginSuccess(user));
    } catch (error) {
        dispatch(loginFailure(error.response?.data?.message));
    }
};

export const logoutUser = () => (dispatch) => {
    dispatch(logout());
};
