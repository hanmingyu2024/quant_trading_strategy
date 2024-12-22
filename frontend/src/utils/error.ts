export interface ApiError {
    message: string;
    code: number;
    details?: Record<string, any>;
}

export class AppError extends Error {
    code: number;
    details?: Record<string, any>;

    constructor(error: ApiError) {
        super(error.message);
        this.code = error.code;
        this.details = error.details;
        this.name = 'AppError';
    }

    static fromResponse(response: any): AppError {
        const error = response.data?.error || {
            message: 'Unknown error',
            code: 500
        };
        return new AppError(error);
    }

    toUserMessage(): string {
        // 将错误转换为用户友好的消息
        switch (this.code) {
            case 401:
                return '请先登录';
            case 403:
                return '没有权限执行此操作';
            case 404:
                return '请求的资源不存在';
            case 429:
                return '请求过于频繁，请稍后再试';
            default:
                return this.message || '操作失败，请重试';
        }
    }
}

export const handleError = (error: any) => {
    if (error.response) {
        throw AppError.fromResponse(error.response);
    }
    throw new AppError({
        message: error.message || 'Network error',
        code: 0
    });
}; 