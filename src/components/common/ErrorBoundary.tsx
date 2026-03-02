import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null };
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
        console.error('ErrorBoundary caught an error:', error, errorInfo);
        this.setState({ errorInfo });
        
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('app-error', { 
                detail: { error: error.message, stack: error.stack, timestamp: new Date().toISOString() } 
            }));
        }
    }

    handleReload = (): void => {
        window.location.reload();
    };

    render(): ReactNode {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
                    <div className="max-w-md w-full bg-slate-800 rounded-2xl p-8 border border-red-500/30">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-3 bg-red-500/20 rounded-xl">
                                <AlertTriangle className="text-red-400" size={32} />
                            </div>
                            <div>
                                <h1 className="text-xl font-black text-white">Algo salió mal</h1>
                                <p className="text-slate-400 text-sm">Error inesperado en la aplicación</p>
                            </div>
                        </div>
                        
                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <div className="mb-6 p-4 bg-red-500/10 rounded-xl border border-red-500/20">
                                <p className="text-red-400 text-sm font-mono">{this.state.error.message}</p>
                            </div>
                        )}

                        <button
                            onClick={this.handleReload}
                            className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl transition-all"
                        >
                            <RefreshCw size={18} />
                            Recargar Página
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
