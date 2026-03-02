type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
    level: LogLevel;
    message: string;
    timestamp: string;
    context?: Record<string, unknown>;
    error?: Error;
}

class Logger {
    private static instance: Logger;
    private logs: LogEntry[] = [];
    private maxLogs = 100;

    private constructor() {}

    static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    private log(level: LogLevel, message: string, context?: Record<string, unknown>, error?: Error): void {
        const entry: LogEntry = {
            level,
            message,
            timestamp: new Date().toISOString(),
            context,
            error
        };

        this.logs.push(entry);
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }

        const formattedMessage = `[${entry.timestamp}] [${level.toUpperCase()}] ${message}`;
        
        switch (level) {
            case 'debug':
                console.debug(formattedMessage, context || '');
                break;
            case 'info':
                console.info(formattedMessage, context || '');
                break;
            case 'warn':
                console.warn(formattedMessage, context || '');
                break;
            case 'error':
                console.error(formattedMessage, error || context || '');
                break;
        }

        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('app-log', { detail: entry }));
        }
    }

    debug(message: string, context?: Record<string, unknown>): void {
        this.log('debug', message, context);
    }

    info(message: string, context?: Record<string, unknown>): void {
        this.log('info', message, context);
    }

    warn(message: string, context?: Record<string, unknown>): void {
        this.log('warn', message, context);
    }

    error(message: string, error?: Error, context?: Record<string, unknown>): void {
        this.log('error', message, context, error);
    }

    getLogs(): LogEntry[] {
        return [...this.logs];
    }

    clearLogs(): void {
        this.logs = [];
    }

    getLogsByLevel(level: LogLevel): LogEntry[] {
        return this.logs.filter(log => log.level === level);
    }
}

export const logger = Logger.getInstance();

export const createContext = (module: string) => ({
    module,
    action: ''
});

export const logApiRequest = (endpoint: string, method: string): void => {
    logger.info(`API Request: ${method} ${endpoint}`, { module: 'api' });
};

export const logApiResponse = (endpoint: string, status: number, duration: number): void => {
    const level = status >= 400 ? 'warn' : 'info';
    logger.log(level, `API Response: ${endpoint} - ${status} (${duration}ms)`, { module: 'api', status, duration });
};

export const logUserAction = (action: string, details?: Record<string, unknown>): void => {
    logger.info(`User Action: ${action}`, { module: 'user', ...details });
};

export const logPerformance = (metric: string, value: number): void => {
    logger.debug(`Performance: ${metric}`, { module: 'performance', value });
};
