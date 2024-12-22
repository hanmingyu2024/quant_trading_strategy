import { ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import { Button, Card, Col, Form, InputNumber, message, Modal, Progress, Row, Statistic } from 'antd';
import React, { useEffect, useState } from 'react';
import api from '../../utils/api';
import './EmailMonitor.scss';

interface EmailStats {
    total_sent: number;
    total_failed: number;
    recent_sent: number;
    recent_failed: number;
    success_rate: number;
}

interface QueueStatus {
    queue_size: number;
    is_processing: boolean;
    batch_size: number;
    delay: number;
}

const EmailMonitor: React.FC = () => {
    const [stats, setStats] = useState<EmailStats | null>(null);
    const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
    const [loading, setLoading] = useState(false);
    const [configModalVisible, setConfigModalVisible] = useState(false);
    const [form] = Form.useForm();

    const fetchData = async () => {
        setLoading(true);
        try {
            const [statsRes, queueRes] = await Promise.all([
                api.get('/admin/email/stats'),
                api.get('/admin/email/queue')
            ]);

            setStats(statsRes.data.stats);
            setQueueStatus(queueRes.data);
        } catch (error) {
            message.error('获取数据失败');
            console.error('Failed to fetch data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    const handleConfigSubmit = async (values: any) => {
        try {
            await api.post('/admin/email/queue/config', values);
            message.success('配置更新成功');
            await fetchData();
            setConfigModalVisible(false);
        } catch (error) {
            message.error('配置更新失败');
            console.error('Failed to update config:', error);
        }
    };

    return (
        <div className="email-monitor">
            <Row gutter={[16, 16]}>
                <Col span={24}>
                    <Card
                        title="邮件发送监控"
                        extra={
                            <>
                                <Button
                                    icon={<ReloadOutlined />}
                                    onClick={fetchData}
                                    loading={loading}
                                    style={{ marginRight: 8 }}
                                >
                                    刷新
                                </Button>
                                <Button
                                    icon={<SettingOutlined />}
                                    onClick={() => setConfigModalVisible(true)}
                                >
                                    配置
                                </Button>
                            </>
                        }
                    >
                        <Row gutter={[16, 16]}>
                            <Col span={6}>
                                <Statistic
                                    title="总发送数"
                                    value={stats?.total_sent || 0}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic
                                    title="总失败数"
                                    value={stats?.total_failed || 0}
                                    valueStyle={{ color: '#cf1322' }}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic
                                    title="队列大小"
                                    value={queueStatus?.queue_size || 0}
                                />
                            </Col>
                            <Col span={6}>
                                <Statistic
                                    title="成功率"
                                    value={stats?.success_rate || 100}
                                    suffix="%"
                                    precision={2}
                                    valueStyle={{ color: '#3f8600' }}
                                />
                            </Col>
                        </Row>

                        <div style={{ marginTop: 24 }}>
                            <Progress
                                percent={stats?.success_rate || 100}
                                status={stats?.success_rate === 100 ? 'success' : 'active'}
                                strokeWidth={20}
                            />
                        </div>
                    </Card>
                </Col>
            </Row>

            <Modal
                title="队列配置"
                open={configModalVisible}
                onOk={() => form.submit()}
                onCancel={() => setConfigModalVisible(false)}
            >
                <Form
                    form={form}
                    onFinish={handleConfigSubmit}
                    initialValues={queueStatus || {}}
                >
                    <Form.Item
                        name="queue_size"
                        label="队列大小"
                        rules={[{ required: true, message: '请输入队列大小' }]}
                    >
                        <InputNumber min={0} />
                    </Form.Item>
                    <Form.Item
                        name="is_processing"
                        label="是否处理中"
                        rules={[{ required: true, message: '请选择是否处理中' }]}
                    >
                        <InputNumber min={0} max={1} />
                    </Form.Item>
                    <Form.Item
                        name="batch_size"
                        label="批次大小"
                        rules={[{ required: true, message: '请输入批次大小' }]}
                    >
                        <InputNumber min={0} />
                    </Form.Item>
                    <Form.Item
                        name="delay"
                        label="延迟时间"
                        rules={[{ required: true, message: '请输入延迟时间' }]}
                    >
                        <InputNumber min={0} />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit">
                            提交
                        </Button>
                    </Form.Item>
                </Form>
            </Modal>
        </div>
    );
};

export default EmailMonitor; 