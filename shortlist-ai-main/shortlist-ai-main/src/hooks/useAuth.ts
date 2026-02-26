import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

const TOKEN_KEY = "auth_token";

export function useAuth() {
    const [token, setToken] = useState<string | null>(() =>
        localStorage.getItem(TOKEN_KEY)
    );
    const navigate = useNavigate();

    // On mount: extract ?token= from URL if present
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const urlToken = params.get("token");

        if (urlToken) {
            localStorage.setItem(TOKEN_KEY, urlToken);
            setToken(urlToken);

            // Clean the token from the URL without reload
            params.delete("token");
            const cleanUrl =
                window.location.pathname +
                (params.toString() ? `?${params.toString()}` : "");
            window.history.replaceState({}, "", cleanUrl);

            navigate("/dashboard", { replace: true });
        }
    }, [navigate]);

    const logout = useCallback(() => {
        localStorage.removeItem(TOKEN_KEY);
        setToken(null);
        navigate("/", { replace: true });
    }, [navigate]);

    return {
        token,
        isAuthenticated: !!token,
        logout,
    };
}
