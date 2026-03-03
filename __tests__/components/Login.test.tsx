/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Login from '../../components/Login';
import userEvent from '@testing-library/user-event';

// Mock de fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('Login Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('should render login form correctly', () => {
    const mockOnLogin = jest.fn();
    render(<Login onLogin={mockOnLogin} />);

    expect(screen.getByPlaceholderText(/tu.email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/•{4,}/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /ingresar/i })).toBeInTheDocument();
  });

  it('should show error when email is empty', async () => {
    const mockOnLogin = jest.fn();
    render(<Login onLogin={mockOnLogin} />);

    fireEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/email es obligatorio/i)).toBeInTheDocument();
    });
  });

  it('should show error when password is empty', async () => {
    const mockOnLogin = jest.fn();
    render(<Login onLogin={mockOnLogin} />);

    fireEvent.change(screen.getByPlaceholderText(/tu.email/i), {
      target: { value: 'test@assetplan.cl' },
    });
    fireEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/contraseña es obligatoria/i)).toBeInTheDocument();
    });
  });

  it('should show error for non-corporate email', async () => {
    const mockOnLogin = jest.fn();
    render(<Login onLogin={mockOnLogin} />);

    fireEvent.change(screen.getByPlaceholderText(/tu.email/i), {
      target: { value: 'test@gmail.com' },
    });
    fireEvent.change(screen.getByPlaceholderText(/•{4,}/i), {
      target: { value: 'password123' },
    });
    fireEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/debes usar tu email corporativo/i)).toBeInTheDocument();
    });
  });

  it('should call onLogin with valid credentials', async () => {
    const mockOnLogin = jest.fn();
    const mockUser = {
      email: 'test@assetplan.cl',
      role: 'admin',
      squad: 'test@assetplan.cl',
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        token: 'mock-token-123',
        user: mockUser,
      }),
    });

    render(<Login onLogin={mockOnLogin} />);

    await userEvent.type(screen.getByPlaceholderText(/tu.email/i), 'test@assetplan.cl');
    await userEvent.type(screen.getByPlaceholderText(/•{4,}/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'test@assetplan.cl',
          password: 'password123',
        }),
      });
    });

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith(
        'test@assetplan.cl',
        'mock-token-123',
        mockUser
      );
    });

    expect(mockFetch).toHaveBeenCalled();
  });

  it('should show error for invalid credentials', async () => {
    const mockOnLogin = jest.fn();

    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({
        success: false,
        error: 'Contraseña incorrecta',
      }),
    });

    render(<Login onLogin={mockOnLogin} />);

    await userEvent.type(screen.getByPlaceholderText(/tu.email/i), 'test@assetplan.cl');
    await userEvent.type(screen.getByPlaceholderText(/•{4,}/i), 'wrongpassword');
    await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/contraseña incorrecta/i)).toBeInTheDocument();
    });

    expect(mockOnLogin).not.toHaveBeenCalled();
  });

  it('should show rate limit error when too many attempts', async () => {
    const mockOnLogin = jest.fn();

    mockFetch.mockResolvedValueOnce({
      status: 429,
      ok: false,
      json: async () => ({
        success: false,
        error: 'Demasiados intentos',
      }),
    });

    render(<Login onLogin={mockOnLogin} />);

    await userEvent.type(screen.getByPlaceholderText(/tu.email/i), 'test@assetplan.cl');
    await userEvent.type(screen.getByPlaceholderText(/•{4,}/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/demasiados intentos/i)).toBeInTheDocument();
    });
  });

  it('should show connection error message on network failure', async () => {
    const mockOnLogin = jest.fn();

    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    render(<Login onLogin={mockOnLogin} />);

    await userEvent.type(screen.getByPlaceholderText(/tu.email/i), 'test@assetplan.cl');
    await userEvent.type(screen.getByPlaceholderText(/•{4,}/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(screen.getByText(/error de conexión/i)).toBeInTheDocument();
    });
  });

  it('should accept @arriendos-assetplan.cl email domain', async () => {
    const mockOnLogin = jest.fn();
    const mockUser = {
      email: 'broker@arriendos-assetplan.cl',
      role: 'broker',
      squad: 'broker@arriendos-assetplan.cl',
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        success: true,
        token: 'mock-token',
        user: mockUser,
      }),
    });

    render(<Login onLogin={mockOnLogin} />);

    await userEvent.type(screen.getByPlaceholderText(/tu.email/i), 'broker@arriendos-assetplan.cl');
    await userEvent.type(screen.getByPlaceholderText(/•{4,}/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalled();
    });
  });

  it('should show loading state while authenticating', async () => {
    const mockOnLogin = jest.fn();

    mockFetch.mockImplementationOnce(() => new Promise(resolve =>
      setTimeout(() => resolve({
        ok: true,
        json: async () => ({ success: true, token: 'token', user: {} }),
      }), 100)
    ));

    render(<Login onLogin={mockOnLogin} />);

    const emailInput = screen.getByPlaceholderText(/tu.email/i);
    const passwordInput = screen.getByPlaceholderText(/•{4,}/i);
    await userEvent.type(emailInput, 'test@assetplan.cl');
    await userEvent.type(passwordInput, 'password123');
    await userEvent.click(screen.getByRole('button', { name: /ingresar/i }));

    expect(screen.getByText(/validando/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalled();
    });
  });
});
