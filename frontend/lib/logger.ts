/**
 * Frontend logging utility for debugging and monitoring
 * Provides structured logging with different log levels
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogContext {
  [key: string]: any;
}

class Logger {
  private isDevelopment: boolean;
  private logLevel: LogLevel;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    // In production, only log warnings and errors
    this.logLevel = this.isDevelopment ? 'debug' : 'warn';
  }

  private shouldLog(level: LogLevel): boolean {
    const levels: LogLevel[] = ['debug', 'info', 'warn', 'error'];
    return levels.indexOf(level) >= levels.indexOf(this.logLevel);
  }

  private formatMessage(level: LogLevel, message: string, context?: LogContext): string {
    const timestamp = new Date().toISOString();
    const contextStr = context ? ` | Context: ${JSON.stringify(context)}` : '';
    return `[${timestamp}] [${level.toUpperCase()}] ${message}${contextStr}`;
  }

  debug(message: string, context?: LogContext): void {
    if (this.shouldLog('debug') && this.isDevelopment) {
      console.debug(this.formatMessage('debug', message, context));
    }
  }

  info(message: string, context?: LogContext): void {
    if (this.shouldLog('info')) {
      console.info(this.formatMessage('info', message, context));
    }
  }

  warn(message: string, context?: LogContext): void {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', message, context));
    }
  }

  error(message: string, error?: Error | unknown, context?: LogContext): void {
    if (this.shouldLog('error')) {
      const errorContext = {
        ...context,
        error: error instanceof Error ? {
          name: error.name,
          message: error.message,
          stack: error.stack,
        } : String(error),
      };
      console.error(this.formatMessage('error', message, errorContext));
    }
  }

  // Specialized logging methods
  apiCall(method: string, url: string, status?: number, duration?: number, context?: LogContext): void {
    const apiContext = {
      ...context,
      method,
      url,
      status,
      duration_ms: duration,
    };
    if (status && status >= 400) {
      this.error(`API ${method} ${url} failed`, undefined, apiContext);
    } else {
      this.info(`API ${method} ${url}`, apiContext);
    }
  }

  websocketEvent(event: string, projectId?: string, data?: any): void {
    this.debug(`WebSocket: ${event}`, {
      project_id: projectId,
      event_type: event,
      data: data ? JSON.stringify(data).substring(0, 200) : undefined,
    });
  }

  componentRender(componentName: string, props?: Record<string, any>): void {
    if (this.isDevelopment) {
      this.debug(`Component rendered: ${componentName}`, {
        component: componentName,
        props: props ? Object.keys(props) : undefined,
      });
    }
  }

  userAction(action: string, details?: LogContext): void {
    this.info(`User action: ${action}`, details);
  }
}

// Export singleton instance
export const logger = new Logger();

// Export type for use in components
export type { LogLevel, LogContext };

