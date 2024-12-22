// 格式化日期
export const formatDate = (date) => {
    const d = new Date(date);
    return d.toLocaleDateString('zh-CN');
};

// 格式化货币
export const formatCurrency = (amount) => {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY'
    }).format(amount);
};

// 验证邮箱格式
export const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

// 验证密码强度
export const validatePassword = (password) => {
    // 至少8位，包含大小写字母和数字
    const re = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    return re.test(password);
};

// 生成随机ID
export const generateId = () => {
    return Math.random().toString(36).substr(2, 9);
};

// 深拷贝对象
export const deepClone = (obj) => {
    return JSON.parse(JSON.stringify(obj));
};

// 防抖函数
export const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// 节流函数
export const throttle = (func, limit) => {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// 获取查询参数
export const getQueryParams = () => {
    const params = new URLSearchParams(window.location.search);
    const paramsObj = {};
    for (const [key, value] of params.entries()) {
        paramsObj[key] = value;
    }
    return paramsObj;
};

// 本地存储操作
export const storage = {
    set: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value));
    },
    get: (key) => {
        const item = localStorage.getItem(key);
        try {
            return JSON.parse(item);
        } catch {
            return item;
        }
    },
    remove: (key) => {
        localStorage.removeItem(key);
    },
    clear: () => {
        localStorage.clear();
    }
};
