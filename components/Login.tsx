import React, { useState } from 'react';
import { Mail, Lock, LogIn, AlertCircle, Crown } from 'lucide-react';

interface LoginProps {
    onLogin: (email: string) => void;
}

const VALID_COORDINATORS = [
    'carlos.echeverria@assetplan.cl',
    'luis.gomez@assetplan.cl',
    'nataly.venegas@assetplan.cl',
    'angely.perez@assetplan.cl'
];

const ADMIN_PASSWORD = 'Soymimejorversion';

const Login: React.FC<LoginProps> = ({ onLogin }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        // Validaciones básicas
        if (!email || !email.trim()) {
            setError('El email es obligatorio');
            setIsLoading(false);
            return;
        }

        if (!password) {
            setError('La contraseña es obligatoria');
            setIsLoading(false);
            return;
        }

        // Validar contraseña fija
        if (password !== ADMIN_PASSWORD) {
            setError('Contraseña incorrecta');
            setIsLoading(false);
            return;
        }

        // Validar email (debe ser @assetplan.cl o @arriendos-assetplan.cl)
        const emailLower = email.toLowerCase().trim();
        const isValidAssetplan = emailLower.includes('@assetplan.cl') || emailLower.includes('@arriendos-assetplan.cl');
        
        if (!isValidAssetplan) {
            setError('Debes usar tu email corporativo (@assetplan.cl o @arriendos-assetplan.cl)');
            setIsLoading(false);
            return;
        }

        // Simular validación contra DB (en producción esto sería una llamada API)
        // Por ahora aceptamos cualquier email @assetplan.cl o @arriendos-assetplan.cl
        // Se puede validar contra la DB si es necesario
        
        try {
            // Pequeño delay para UX
            await new Promise(resolve => setTimeout(resolve, 800));
            
            // Login exitoso
            onLogin(emailLower);
        } catch (err) {
            setError('Error al iniciar sesión. Intenta nuevamente.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#101622] flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background Effects */}
            <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none"></div>

            <div className="w-full max-w-md">
                {/* Logo y Header */}
                <div className="text-center mb-8">
                    <div className="flex justify-center mb-6">
                        <div className="p-4 bg-gradient-to-br from-blue-500/20 to-indigo-500/20 rounded-3xl border border-blue-500/30">
                            <Crown className="text-blue-400" size={48} />
                        </div>
                    </div>
                    <h1 className="text-3xl font-black text-white uppercase tracking-widest mb-2">
                        Assetplan Ranking
                    </h1>
                    <p className="text-slate-400 text-sm font-bold uppercase tracking-wide">
                        Home Operativo 2026
                    </p>
                </div>

                {/* Login Card */}
                <div className="bg-[#1e293b] rounded-3xl border border-[#324467] shadow-2xl p-8">
                    <div className="mb-6">
                        <h2 className="text-xl font-bold text-white uppercase tracking-widest text-center">
                            Iniciar Sesión
                        </h2>
                        <p className="text-slate-500 text-xs text-center mt-2">
                            Ingresa tus credenciales para acceder
                        </p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-6">
                        {/* Email Input */}
                        <div>
                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                                <Mail size={14} className="inline mr-1.5" />
                                Email Corporativo
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => {
                                        setEmail(e.target.value);
                                        setError('');
                                    }}
                                    placeholder="tu.email@assetplan.cl o @arriendos-assetplan.cl"
                                    className="w-full bg-[#101622] text-white text-base px-6 py-4 pl-12 rounded-2xl border border-[#324467] focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                                    autoFocus
                                />
                            </div>
                        </div>

                        {/* Password Input */}
                        <div>
                            <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                                <Lock size={14} className="inline mr-1.5" />
                                Contraseña
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => {
                                        setPassword(e.target.value);
                                        setError('');
                                    }}
                                    placeholder="••••••••"
                                    className="w-full bg-[#101622] text-white text-base px-6 py-4 pl-12 rounded-2xl border border-[#324467] focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                                />
                            </div>
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex items-center gap-3">
                                <AlertCircle className="text-red-400 flex-shrink-0" size={18} />
                                <p className="text-red-400 text-sm font-bold">{error}</p>
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="w-full py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-700 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-black text-base uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
                        >
                            {isLoading ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                    Validando...
                                </>
                            ) : (
                                <>
                                    <LogIn size={20} />
                                    Ingresar
                                </>
                            )}
                        </button>
                    </form>

                    {/* Footer Info */}
                    <div className="mt-6 pt-6 border-t border-[#324467]">
                        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4">
                            <p className="text-blue-400 text-xs font-bold text-center">
                                🔒 Acceso exclusivo para corredores Assetplan
                            </p>
                            <p className="text-slate-500 text-[10px] text-center mt-1">
                                Coordinadores: @assetplan.cl • Corredores: @arriendos-assetplan.cl
                            </p>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center mt-8">
                    <p className="text-slate-600 text-[10px] font-bold uppercase tracking-widest">
                        © 2026 Assetplan • Todos los derechos reservados
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
