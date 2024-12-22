export interface PasswordStrength {
    score: number;  // 0-4
    feedback: string[];
    isStrong: boolean;
}

export const validatePassword = (password: string): PasswordStrength => {
    const feedback: string[] = [];
    let score = 0;

    // 长度检查
    if (password.length < 8) {
        feedback.push('密码长度至少为8位');
    } else if (password.length >= 12) {
        score += 2;
    } else {
        score += 1;
    }

    // 复杂度检查
    if (/[A-Z]/.test(password)) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 1;

    // 特殊字符检查
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        feedback.push('建议包含特殊字符');
    }

    // 大小写检查
    if (!/[A-Z]/.test(password)) {
        feedback.push('需要包含大写字母');
    }
    if (!/[a-z]/.test(password)) {
        feedback.push('需要包含小写字母');
    }

    // 数字检查
    if (!/[0-9]/.test(password)) {
        feedback.push('需要包含数字');
    }

    // 连续字符检查
    if (/(.)\1{2,}/.test(password)) {
        feedback.push('不要使用连续重复的字符');
        score -= 1;
    }

    // 键盘序列检查
    const keyboardSequences = ['qwerty', '123456', 'asdfgh'];
    if (keyboardSequences.some(seq => password.toLowerCase().includes(seq))) {
        feedback.push('不要使用键盘序列');
        score -= 1;
    }

    return {
        score: Math.max(0, Math.min(4, score)),
        feedback,
        isStrong: score >= 3 && feedback.length === 0
    };
};

export const getPasswordStrengthColor = (score: number): string => {
    switch (score) {
        case 0: return '#ff4d4f';  // 红色
        case 1: return '#ffa39e';  // 浅红色
        case 2: return '#faad14';  // 黄色
        case 3: return '#52c41a';  // 绿色
        case 4: return '#237804';  // 深绿色
        default: return '#d9d9d9'; // 灰色
    }
};

export const getPasswordStrengthText = (score: number): string => {
    switch (score) {
        case 0: return '非常弱';
        case 1: return '弱';
        case 2: return '一般';
        case 3: return '强';
        case 4: return '非常强';
        default: return '未知';
    }
}; 