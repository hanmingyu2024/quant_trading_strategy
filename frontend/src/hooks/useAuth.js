import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getCurrentUser } from '../store/actions/authActions';

export const useAuth = () => {
    const dispatch = useDispatch();
    const { user, isAuthenticated, loading, error } = useSelector((state) => state.auth);

    useEffect(() => {
        if (!user && isAuthenticated) {
            dispatch(getCurrentUser());
        }
    }, [dispatch, user, isAuthenticated]);

    return {
        user,
        isAuthenticated,
        loading,
        error
    };
};