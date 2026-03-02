import React, { useEffect, useState } from 'react';

interface SkipLinkProps {
    targetId: string;
    children: React.ReactNode;
}

export const SkipLink: React.FC<SkipLinkProps> = ({ targetId, children }) => (
    <a
        href={`#${targetId}`}
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg focus:font-bold"
    >
        {children}
    </a>
);

export const LiveRegion: React.FC<{ message: string }> = ({ message }) => (
    <div role="status" aria-live="polite" aria-atomic="true" className="sr-only">
        {message}
    </div>
);

export const useAriaAnnounce = () => {
    const [announcement, setAnnouncement] = useState('');

    useEffect(() => {
        const handler = (e: CustomEvent) => {
            setAnnouncement(e.detail);
            setTimeout(() => setAnnouncement(''), 1000);
        };
        window.addEventListener('aria-announce', handler as EventListener);
        return () => window.removeEventListener('aria-announce', handler as EventListener);
    }, []);

    return announcement;
};

export const FocusTrap: React.FC<{ children: React.ReactNode; active: boolean }> = ({ children, active }) => {
    const containerRef = React.useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!active) return;
        
        const container = containerRef.current;
        if (!container) return;

        const focusableElements = container.querySelectorAll<HTMLElement>(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key !== 'Tab') return;

            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement?.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement?.focus();
            }
        };

        container.addEventListener('keydown', handleKeyDown);
        firstElement?.focus();

        return () => container.removeEventListener('keydown', handleKeyDown);
    }, [active]);

    return <div ref={containerRef}>{children}</div>;
};

export const LoadingSpinner: React.FC<{ label?: string }> = ({ label = 'Cargando' }) => (
    <div className="flex items-center gap-2" role="status">
        <div className="w-5 h-5 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
        <span className="sr-only">{label}</span>
    </div>
);

export const visuallyHidden = 'sr-only';
