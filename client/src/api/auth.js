import axios from './axios';


export const registerRequest = async (user) => {
    const res = await axios.post(`/register`, user);
    return res.data;
}

export const loginRequest = async (user) => {
    const res = await axios.post(`/login`, user);
    return res.data;
}

export const logoutRequest = () => axios.post(`/logout`);

export const checkAuthRequest = async () => {
    const res = await axios.get(`/check-auth`);
    return res.data;
};