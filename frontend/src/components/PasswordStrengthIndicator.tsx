import { Progress, Space, Typography } from 'antd';
import React from 'react';
import {
    getPasswordStrengthColor,
    getPasswordStrengthText,
    PasswordStrength
} from '../utils/passwordValidation';

const { Text } = Typography;

interface PasswordStrengthIndicatorProps {
    strength: PasswordStrength;
}

const PasswordStrengthIndicator: React.FC<PasswordStrengthIndicatorProps> = ({
    strength
}) => {
    const color = getPasswordStrengthColor(strength.score);
    const text = getPasswordStrengthText(strength.score);

    return (
        <div className="password-strength">
            <Space direction="vertical" style={{ width: '100%' }}>
                <Progress
                    percent={strength.score * 25}
                    strokeColor={color}
                    showInfo={false}
                    size="small"
                />
                <div className="password-strength__info">
                    <Text type="secondary">密码强度：</Text>
                    <Text style={{ color }}>{text}</Text>
                </div>
                {strength.feedback.length > 0 && (
                    <ul className="password-strength__feedback">
                        {strength.feedback.map((item, index) => (
                            <li key={index}>
                                <Text type="danger">{item}</Text>
                            </li>
                        ))}
                    </ul>
                )}
            </Space>
        </div>
    );
};

export default PasswordStrengthIndicator; 