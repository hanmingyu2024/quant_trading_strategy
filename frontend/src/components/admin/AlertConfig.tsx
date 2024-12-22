import {
    Button,
    Card, Form, Input,
    Select,
    Space,
    Table, Tag,
    message
} from 'antd';
import React, { useEffect, useState } from 'react';
import api from '../../utils/api';

const { Option } = Select;

interface AlertConfig {
    email: {
        enabled: boolean;
        smtp_server: string;
        smtp_port: number;
        username: string;
        password: string;
        from_email: string;
        to_emails: string[];
    };
    slack: {
        enabled: boolean;
        webhook_url: string;
    };
    webhook: {
        enabled: boolean;
        url: string;
    };
}

const AlertConfig: React.FC = () => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [alertStats, setAlertStats] = useState<any>(null);

    const fetchAlertStats = async () => {
        try {
            const response = await api.get('/admin/alerts/stats');
            setAlertStats(response.data);
        } catch (error) {
            message.error('获取告警统计失败');
        }
    };

    useEffect(() => {
        fetchAlertStats();
        const interval = setInterval(fetchAlertStats, 30000);
        return () => clearInterval(interval);
    }, []);

    const handleTestAlert = async (values: any) => {
        try {
            await api.post('/admin/alerts/test', values);
            message.success('测试告警已发送');
        } catch (error) {
            message.error('发送测试告警失败');
        }
    };

    const columns = [
        {
            title: '时间',
            dataIndex: 'timestamp',
            key: 'timestamp',
        },
        {
            title: '级别',
            dataIndex: 'level',
            key: 'level',
            render: (level: string) => (
                <Tag color={
                    level === 'critical' ? 'red' :
                        level === 'error' ? 'volcano' :
                            level === 'warning' ? 'orange' :
                                'green'
                }>
                    {level.toUpperCase()}
                </Tag>
            ),
        },
        {
            title: '标题',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: '消息',
            dataIndex: 'message',
            key: 'message',
        }
    ];

    return (
        <div className="alert-config">
            <Card title="告警统计" extra={<Button onClick={fetchAlertStats}>刷新</Button>}>
                <Space size="large">
                    <Statistic
                        title="总告警数"
                        value={alertStats?.total_alerts || 0}
                    />
                    <Statistic
                        title="最近1小时"
                        value={alertStats?.alerts_last_hour || 0}
                    />
                </Space>

                <Table
                    columns={columns}
                    dataSource={alertStats?.recent_alerts || []}
                    rowKey="timestamp"
                    pagination={false}
                    style={{ marginTop: 24 }}
                />
            </Card>

            <Card title="测试告警" style={{ marginTop: 24 }}>
                <Form layout="vertical" onFinish={handleTestAlert}>
                    <Form.Item
                        name="level"
                        label="告警级别"
                        rules={[{ required: true }]}
                    >
                        <Select>
                            <Option value="info">信息</Option>
                            <Option value="warning">警告</Option>
                            <Option value="error">错误</Option>
                            <Option value="critical">严重</Option>
                        </Select>
                    </Form.Item>

                    <Form.Item
                        name="message"
                        label="告警消息"
                        rules={[{ required: true }]}
                    >
                        <Input.TextArea />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit">
                            发送测试告警
                        </Button>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default AlertConfig; 