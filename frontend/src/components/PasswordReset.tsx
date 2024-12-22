import { LockOutlined, MailOutlined, SafetyOutlined } from '@ant-design/icons';
import { Alert, Button, Form, Input, message, Steps, Typography } from 'antd';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { validatePassword } from '../utils/passwordValidation';
import './PasswordReset.scss';
import PasswordStrengthIndicator from './PasswordStrengthIndicator';

const { Title, Text } = Typography;
const { Step } = Steps;

const PasswordReset = () => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isRequesting, setIsRequesting] = useState(false);
    const [isResetting, setIsResetting] = useState(false);
    const [email, setEmail] = useState('');
    const [passwordStrength, setPasswordStrength] = useState(null);
    const navigate = useNavigate();

    const steps = [
        {
            title: '请求重置',
            description: '输入您的邮箱地址'
        },
        {
            title: '验证身份',
            description: '输入重置令牌'
        },
        {
            title: '重置密码',
            description: '设置新密码'
        }
    ];

    const onRequestReset = async (values) => {
        setIsRequesting(true);
        try {
            const response = await fetch('/api/v1/password/reset-request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(values),
            });

            const data = await response.json();

            if (response.ok) {
                message.success('重置邮件已发送，请检查您的邮箱');
                setEmail(values.email);
                setCurrentStep(1);
            } else {
                message.error(data.detail || '发送重置邮件失败');
            }
        } catch (error) {
            message.error('网络错误，请稍后重试');
        } finally {
            setIsRequesting(false);
        }
    };

    const onConfirmReset = async (values) => {
        setIsResetting(true);
        try {
            const response = await fetch('/api/v1/password/reset-confirm', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(values),
            });

            const data = await response.json();

            if (response.ok) {
                message.success('密码重置成功');
                setCurrentStep(2);
                setTimeout(() => navigate('/login'), 3000);
            } else {
                message.error(data.detail || '密码重置失败');
            }
        } catch (error) {
            message.error('网络错误，请稍后重试');
        } finally {
            setIsResetting(false);
        }
    };

    const handlePasswordChange = (e) => {
        const value = e.target.value;
        const strength = validatePassword(value);
        setPasswordStrength(strength);
    };

    return (
        <div className="password-reset">
            <Title level={2} className="password-reset__title">
                密码重置
            </Title>

            <Steps current={currentStep} className="password-reset__steps">
                {steps.map(item => (
                    <Step key={item.title} title={item.title} description={item.description} />
                ))}
            </Steps>

            {currentStep === 0 && (
                <Form onFinish={onRequestReset} className="password-reset__form">
                    <Form.Item
                        name="email"
                        rules={[
                            { required: true, message: '请输入邮箱' },
                            { type: 'email', message: '请输入有效的邮箱地址' }
                        ]}
                    >
                        <Input
                            prefix={<MailOutlined />}
                            placeholder="邮箱地址"
                            size="large"
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={isRequesting}
                            block
                            size="large"
                        >
                            发送重置邮件
                        </Button>
                    </Form.Item>
                </Form>
            )}

            {currentStep === 1 && (
                <>
                    <Alert
                        message="重置邮件已发送"
                        description={`我们已向 ${email} 发送了重置邮件，请查收并输入重置令牌。`}
                        type="info"
                        showIcon
                        className="password-reset__alert"
                    />

                    <Form onFinish={onConfirmReset} className="password-reset__form">
                        <Form.Item
                            name="token"
                            rules={[{ required: true, message: '请输入重置令牌' }]}
                        >
                            <Input
                                prefix={<SafetyOutlined />}
                                placeholder="重置令牌"
                                size="large"
                            />
                        </Form.Item>

                        <Form.Item
                            name="new_password"
                            rules={[
                                {
                                    validator: async (_, value) => {
                                        if (!value) {
                                            throw new Error('请输入密码');
                                        }
                                        const strength = validatePassword(value);
                                        if (!strength.isStrong) {
                                            throw new Error(strength.feedback[0]);
                                        }
                                    }
                                }
                            ]}
                        >
                            <Input.Password
                                prefix={<LockOutlined />}
                                placeholder="新密码"
                                onChange={handlePasswordChange}
                                size="large"
                            />
                        </Form.Item>

                        {passwordStrength && (
                            <Form.Item>
                                <PasswordStrengthIndicator strength={passwordStrength} />
                            </Form.Item>
                        )}

                        <Form.Item>
                            <Button
                                type="primary"
                                htmlType="submit"
                                loading={isResetting}
                                block
                                size="large"
                            >
                                重置密码
                            </Button>
                        </Form.Item>
                    </Form>

                    <div className="password-reset__tips">
                        <h4>密码要求：</h4>
                        <ul>
                            <li>至少8个字符</li>
                            <li>包含大写字母</li>
                            <li>包含小写字母</li>
                            <li>包含数字</li>
                        </ul>
                    </div>
                </>
            )}

            {currentStep === 2 && (
                <Alert
                    message="密码重置成功"
                    description="您的密码已经成功重置，3秒后将跳转到登录页面。"
                    type="success"
                    showIcon
                    className="password-reset__alert"
                />
            )}
        </div>
    );
};

export default PasswordReset;